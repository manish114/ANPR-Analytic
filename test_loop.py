# import cv2
# from ultralytics import YOLO
# import time

# cap = cv2.VideoCapture("rtsp://admin:admin@123@192.168.0.109:554/Streaming/channels/101")  # Replace with your actual path
# model = YOLO("app/models/yolov8_plate.pt")

# frame_count = 0

# while cap.isOpened():
#     ret, frame = cap.read()
#     if not ret:
#         print("❌ Can't read frame.")
#         break

#     frame_count += 1
#     print(f"\n📸 Frame {frame_count}")

#     try:
#         results = model(frame)
#         boxes = results[0].boxes

#         if boxes is not None and len(boxes) > 0:
#             print(f"✅ Detected {len(boxes)} plate(s)")
#         else:
#             print("🔍 No plates detected.")
#     except Exception as e:
#         print("❌ YOLO error:", e)

#     time.sleep(0.1)

# cap.release()
# print("🛑 Stream ended.")

# test_easyocr.py

# test_easyocr.py

import pytesseract
from PIL import Image
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

img = Image.open("27f9d097-3b4e-4572-8a04-f970bb7c3a07.jpg")  # use any test plate image

text = pytesseract.image_to_string(img)
print("Detected text:", text)

