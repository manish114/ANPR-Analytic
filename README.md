🔍 Automatic Number Plate Recognition (ANPR) with HLS Streaming
A production-ready ANPR web application that detects license plates from RTSP or MP4 video streams, extracts text using Tesseract OCR, and streams the annotated video using HLS for cross-device/browser support.

🚀 Features
✅ Live video input (RTSP/MP4)

✅ YOLOv8-based license plate detection

✅ Tesseract OCR for plate text extraction

✅ Real-time video annotation with bounding boxes and text

✅ Debug storage of full frames and cropped plates

✅ Converts streams to HLS (.m3u8) using FFmpeg

✅ Web-accessible player with HLS.js

✅ Scalable and modular FastAPI backend

📦 Tech Stack
Layer	Technology
Backend	FastAPI (Python)
OCR	Tesseract OCR
Detection	YOLOv8 (Ultralytics)
Video	OpenCV, FFmpeg
Streaming	HLS (HTTP Live Streaming)
Frontend	Plain HTML + HLS.js
Storage	Cropped Plates + Debug Frames
Serving	Static files via FastAPI

🧰 Requirements
🔧 Dependencies
Install via pip:

bash
Copy
Edit
pip install fastapi uvicorn opencv-python pytesseract ultralytics python-multipart
Also install:

Tesseract OCR (must be in system PATH)

FFmpeg (for stream conversion)

Python ≥ 3.8

📂 Project Structure
csharp
Copy
Edit
anpr_app/
├── app/
│   ├── main.py                # FastAPI server
│   ├── anpr_engine.py         # Video processing & detection
│   ├── utils/
│   │   └── ocr_utils.py       # OCR handling
│   ├── static/
│   │   ├── index.html         # Web UI
│   │   ├── hls/               # HLS output (.m3u8, .ts)
│   │   ├── frames/            # Debug full frames
│   │   └── plates/            # Cropped license plates
├── run.py                     # Entry point
└── requirements.txt
▶️ Running the Project
1. Prepare Your Environment
Make sure FFmpeg and Tesseract are installed and accessible via your system path.

2. Start the FastAPI Server
bash
Copy
Edit
uvicorn app.main:app --host 0.0.0.0 --port 8000
3. Start HLS Stream from RTSP
Start an HLS stream using FFmpeg (example command):

bash
Copy
Edit
ffmpeg -i rtsp://your-camera-url -an -c:v copy -f hls -hls_time 1 -hls_list_size 5 -hls_flags delete_segments app/static/hls/stream1.m3u8
Or use auto-FFmpeg trigger inside the app (if added).

4. Open in Browser
Visit:

arduino
Copy
Edit
http://localhost:8000/
You'll see an HLS player for the video stream.

🧪 Debugging
Debug frames are saved in: app/static/frames/

Cropped plates are saved in: app/static/plates/

OCR is logged in the terminal (with timestamps and results)

🛠️ Tips & Tricks
Use cap.get(cv2.CAP_PROP_FPS) to read source FPS.

Use frame skipping (if frame_count % int(fps) != 0) to reduce processing.

Annotate frames with cv2.putText and cv2.rectangle for live visual feedback.

Use HLS.js on frontend to ensure compatibility with all browsers.


📡 API Endpoints
🔹 GET /
Description: Serves the main index.html HLS player page.

Response: HTML page with embedded HLS.js video player.

🔹 POST /start-stream
Description: Starts ANPR processing for a given RTSP or video URL.

Request Body (JSON):

json
Copy
Edit
{
  "stream_url": "rtsp://your-camera-url",
  "stream_id": "cam1"
}
Response:

json
Copy
Edit
{ "message": "Stream started", "stream_id": "cam1" }
🔹 POST /stop-stream
Description: Gracefully stops an active ANPR stream.

Request Body (JSON):

json
Copy
Edit
{
  "stream_id": "cam1"
}
Response:

json
Copy
Edit
{ "message": "Stream stopped", "stream_id": "cam1" }
🔹 GET /frame/{stream_id}
Description: Returns the latest processed frame (as JPEG) from the specified stream.

Response: image/jpeg (or 404 if stream not found)

🔹 GET /hls/stream1.m3u8
Description: Serves the HLS .m3u8 playlist for live video playback.

Use Case: Embed or load via HLS.js in the frontend.



📌 TODO / Extensions
 Add camera registration UI

 Add authentication + token access

 Save detections in a database (PostgreSQL/SQLite)

 Export logs or create analytics dashboard

 Add Docker support for portable deployment










