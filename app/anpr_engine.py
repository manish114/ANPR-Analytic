import cv2
import os
import uuid
import time
from datetime import datetime
from ultralytics import YOLO
import pytesseract
import threading

# Set tesseract path (adjust if needed)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

output_dir = "app/static"
os.makedirs(f"{output_dir}/plates", exist_ok=True)
os.makedirs(f"{output_dir}/frames", exist_ok=True)

model = YOLO("models/yolov8_plate.pt")

# Store latest frame per stream_id
latest_frames = {}
frame_locks = {}

def update_frame(stream_id, frame):
    _, jpeg = cv2.imencode(".jpg", frame)
    frame_locks[stream_id] = threading.Lock()
    with frame_locks[stream_id]:
        latest_frames[stream_id] = jpeg.tobytes()

def get_frame(stream_id):
    if stream_id in latest_frames:
        with frame_locks[stream_id]:
            return latest_frames[stream_id]
    return None

def stop_stream(stream_id):
    if stream_id in latest_frames:
        del latest_frames[stream_id]
    if stream_id in frame_locks:
        del frame_locks[stream_id]

# def ocr_with_tesseract(cropped_img):
#     gray = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)
#     blur = cv2.bilateralFilter(gray, 11, 17, 17)
#     _, thresh = cv2.threshold(blur, 150, 255, cv2.THRESH_BINARY)

#     text = pytesseract.image_to_string(thresh, config='--psm 7')
#     return text.strip()

def ocr_with_tesseract(cropped_img):
    text = pytesseract.image_to_string(cropped_img)
    return text.strip()

def process_video(source_url: str, stream_id: str, stop_event):
    source_url = "video.mp4"
    cap = cv2.VideoCapture(source_url)
    fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"🎥 Video FPS: {fps}")
    print(f"▶️ Started ANPR stream: {stream_id}")

    frame_count = 0
    while cap.isOpened() and not stop_event.is_set():
        ret, frame = cap.read()
        if not ret:
            print(f"⚠️ Frame read failed for {stream_id}. Retrying...")
            time.sleep(0.5)
            continue

        frame_count += 1
        print(f"📸 Read frame {frame_count}")

        # ✅ Skip frames to get ~1 FPS
        if frame_count % int(fps) != 0:
            continue  # Skip this frame

        print(f"📸 Processing frame {frame_count}")

        # 🔽 Save every processed frame
        frame_debug_path = f"{output_dir}/frames/frame_debug_{frame_count}.jpg"
        cv2.imwrite(frame_debug_path, frame)
        print(f"💾 Saved frame {frame_count} to: {frame_debug_path}")

        detections = model(frame)[0].boxes
        for box in detections:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cropped = frame[y1:y2, x1:x2]

            uid = str(uuid.uuid4())
            plate_path = f"{output_dir}/plates/{uid}.jpg"
            cv2.imwrite(plate_path, cropped)
            print(f"📷 Saved cropped plate: {plate_path}")

            plate_number = ocr_with_tesseract(cropped)
            if plate_number:
                timestamp = datetime.utcnow().isoformat()
                print(f"🟩 Detected plate: {plate_number} at {timestamp}")

                cv2.putText(frame, plate_number, (x1, y1 - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        update_frame(stream_id, frame)

    cap.release()
    print(f"⏹️ Stopped ANPR stream: {stream_id}")
