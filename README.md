python -m uvicorn main:app --reload  // To run this project 

✅ 1. RTSP/MP4 Video Processing
Created a process_video() function to:

Capture frames from RTSP or MP4 source.

Detect license plates using a YOLOv8 model.

Crop detected plates and save them for debugging.

Run OCR on cropped plates to extract text.

✅ 2. Replaced EasyOCR with Tesseract
Switched OCR from EasyOCR to pytesseract for improved reliability.

Verified that tesseract is installed and accessible via PATH.

Used basic or preprocessed versions of ocr_with_tesseract().

✅ 3. Frame Processing Optimization
Verified the video was processing all frames (not just the first).

Printed and monitored frame count + FPS.

Reduced processing frequency to 1 frame per second using:

python
Copy
Edit
if frame_count % int(fps) != 0:
    continue
✅ 4. Debugging Support
Saved:

Debug full frames to app/static/frames/.

Cropped plates to app/static/plates/.

✅ 5. MJPEG to HLS Conversion (Preparation)
Identified the need to switch from MJPEG to HLS streaming for browser/device compatibility.

Planned to use FFmpeg to convert RTSP to HLS format (.m3u8 + .ts segments).

✅ 6. Serve Frontend with FastAPI
Set up FastAPI to:

Serve static files (app/static/).

Serve index.html by default on /.

Prepare /static/hls/ directory to serve generated HLS streams.

Below are the example of stream::

rtsp://admin:admin@123@103.233.116.181:554/Streaming/channels/1 

{
  "source_url": "rtsp://admin:admin@123@192.168.0.109:554/Streaming/channels/101",
  "stream_id": "cam1"
}

{
  "source_url": "rtsp://localhost:8554/",
  "stream_id": "cam1"
}
