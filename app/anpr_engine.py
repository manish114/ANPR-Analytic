# app/anpr_engine.py

import cv2
import os
import uuid
import time
import queue
import threading
from datetime import datetime
from ultralytics import YOLO
import easyocr

# Setup
output_dir = "app/static"
os.makedirs(f"{output_dir}/plates", exist_ok=True)

model = YOLO("models/yolov8_plate.pt")
ocr_reader = easyocr.Reader(['en'], gpu=False)

latest_frames = {}
frame_locks = {}
ocr_queue = queue.Queue()
stop_events = {}

def update_frame(stream_id, frame):
    _, jpeg = cv2.imencode(".jpg", frame)
    if stream_id not in frame_locks:
        frame_locks[stream_id] = threading.Lock()
    with frame_locks[stream_id]:
        latest_frames[stream_id] = jpeg.tobytes()

def get_frame(stream_id):
    if stream_id in latest_frames:
        with frame_locks[stream_id]:
            return latest_frames[stream_id]
    return None

def stop_stream(stream_id):
    if stream_id in stop_events:
        stop_events[stream_id].set()
    if stream_id in latest_frames:
        del latest_frames[stream_id]
    if stream_id in frame_locks:
        del frame_locks[stream_id]

def ocr_worker():
    while True:
        try:
            item = ocr_queue.get(timeout=1)
        except queue.Empty:
            continue
        if item is None:
            break

        stream_id, cropped, box, frame, timestamp = item
        try:
            # ⚠️ Skip real OCR and simulate detection
            plate_number = f"TEST-{str(uuid.uuid4())[:8]}"  # Fake plate

            uid = str(uuid.uuid4())
            plate_path = f"{output_dir}/plates/{uid}.jpg"
            cv2.imwrite(plate_path, cropped)

            x1, y1, x2, y2 = box
            cv2.putText(frame, plate_number, (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            print(f"🟩 Simulated plate: {plate_number} at {timestamp}")

        except Exception as e:
            print(f"❌ Simulated OCR error: {e}")

        update_frame(stream_id, frame)
        ocr_queue.task_done()

# Start OCR worker
ocr_thread = threading.Thread(target=ocr_worker, daemon=True)
ocr_thread.start()

def process_video(source_url: str, stream_id: str, stop_event):
    cap = cv2.VideoCapture(source_url)
    print(f"▶️ Started ANPR stream: {stream_id}")
    stop_events[stream_id] = stop_event
    frame_count = 0

    while cap.isOpened() and not stop_event.is_set():
        ret, frame = cap.read()
        if not ret:
            print(f"⚠️ Frame read failed for {stream_id}. Retrying...")
            time.sleep(0.5)
            continue

        frame_count += 1
        print(f"📸 Frame {frame_count}")

        try:
            results = model(frame)[0].boxes
            if not results:
                print("🔎 No detections.")
                update_frame(stream_id, frame)
                continue

            for box in results:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cropped = frame[y1:y2, x1:x2]
                timestamp = datetime.utcnow().isoformat()

                # Enqueue for OCR
                ocr_queue.put((stream_id, cropped.copy(), (x1, y1, x2, y2), frame, timestamp))

        except Exception as e:
            print(f"❌ Detection error: {e}")

        time.sleep(0.03)  # throttle loop

    cap.release()
    print(f"⏹️ Stopped ANPR stream: {stream_id}")
