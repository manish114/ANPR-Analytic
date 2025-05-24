import cv2
import os
import uuid
import time
from datetime import datetime
from ultralytics import YOLO
import threading

output_dir = "app/static"
os.makedirs(f"{output_dir}/plates", exist_ok=True)
os.makedirs(f"{output_dir}/frames", exist_ok=True)
os.makedirs(f"app/streams", exist_ok=True)

import easyocr
model = YOLO("models/best.pt")
reader = easyocr.Reader(['en'], gpu=False)

from utils import license_complies_format,format_license
# Store latest frame per stream_id
latest_frames = {}
frame_locks = {}

def update_frame(stream_id, frame):
    stream_path = f"app/streams/{stream_id}.jpg" ## to save frame with bounding box 
    cv2.imwrite(stream_path, frame)  # Overwrite latest frame ## to save frame with bounding box 
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

# def ocr_with_tesseract(cropped_img):
#     text = pytesseract.image_to_string(cropped_img)
#     return text.strip()

def process_video(source_url: str, stream_id: str, stop_event, target_fps: int = 1):
    #source_url = "video.mp4"
    cap = cv2.VideoCapture(source_url)
    video_fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"🎥 Video FPS: {video_fps}")
    print(f"▶️ Started ANPR stream: {stream_id}")

    frame_interval = int(video_fps // target_fps) if target_fps < video_fps else 1
    print(f"⏱️ Processing every {frame_interval} frames for target FPS = {target_fps}")

    frame_count = 0
    while cap.isOpened() and not stop_event.is_set():
        ret, frame = cap.read()
        if not ret:
            print(f"⚠️ Frame read failed for {stream_id}. Retrying...")
            time.sleep(0.5)
            continue

        frame_count += 1
        print(f"📸 Read frame {frame_count}")

        if frame_count % frame_interval != 0:
            continue  # Skip frames to control FPS

        print(f"🧠 Processing frame {frame_count}")

        frame_debug_path = f"{output_dir}/frames/frame_debug_{frame_count}.jpg"
        cv2.imwrite(frame_debug_path, frame)
        print(f"💾 Saved frame {frame_count} to: {frame_debug_path}")
        results = model.predict(frame, save=True, conf=0.2)
        
        for result in results:
            boxes = result.boxes
            
            for box_tensor in boxes.xyxy:
                x1, y1, x2, y2 = map(int, box_tensor)
                cropped_plate = frame[y1:y2, x1:x2]
                gray_img = cv2.cvtColor(cropped_plate, cv2.COLOR_RGB2GRAY)
                uid = str(uuid.uuid4())
                plate_path = f"{output_dir}/plates/{uid}.jpg"
                cv2.imwrite(plate_path, cropped_plate)
                print(f"📷 Saved cropped plate: {plate_path}")
                detections = reader.readtext(gray_img)

                for detection in detections:
                    bbox, text, score = detection
                    text = text.upper().replace(' ', '').replace('.', '').replace(',', '')
                    formatted = format_license(text)

                    if license_complies_format(formatted):
                        timestamp = datetime.utcnow().isoformat()
                        print(f"🟩 Detected plate: {formatted} at {timestamp}")

                        cv2.putText(frame, formatted, (x1, y1 - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

                    else:
                        timestamp = datetime.utcnow().isoformat()
                        print(f"🟩 Detected plate: {formatted} at {timestamp}")
                        cv2.putText(frame, formatted+"not in format", (x1, y1 - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    
                

            update_frame(stream_id, frame)

    cap.release()
    print(f"⏹️ Stopped ANPR stream: {stream_id}")
