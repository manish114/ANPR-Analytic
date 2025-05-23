# app/main.py

from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.responses import JSONResponse, StreamingResponse
import threading
import subprocess
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from anpr_engine import process_video, get_frame, stop_stream
# app/main.py



app = FastAPI()
app.mount("/hls", StaticFiles(directory="hls"), name="hls")

# Serve index.html at the root path
@app.get("/", response_class=HTMLResponse)
async def read_index():
    return FileResponse("hls/index.html")

class ANPRRequest(BaseModel):
    source_url: str
    stream_id: str

# Dictionary to track active threads and stop flags
active_streams = {}

@app.post("/start_anpr")
def start_anpr(request: ANPRRequest):
    if request.stream_id in active_streams:
        return JSONResponse(content={"message": "Stream already running."})

    stop_event = threading.Event()
    thread = threading.Thread(
        target=process_video,
        args=(request.source_url, request.stream_id, stop_event),
        daemon=True
    )
    thread.start()
    ffmpeg_proc = start_hls_ffmpeg(request.stream_id) #uncomment To start hls stream
    active_streams[request.stream_id] = {"thread": thread, "stop_event": stop_event}
    return JSONResponse(content={"message": f"Started ANPR for stream: {request.stream_id}"})


@app.get("/stream/{stream_id}")
def stream_video(stream_id: str):
    def generate():
        while True:
            frame = get_frame(stream_id)
            if frame is None:
                continue
            yield (b"--frame\r\n"
                   b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")

    return StreamingResponse(generate(), media_type="multipart/x-mixed-replace; boundary=frame")


@app.post("/stop_anpr")
def stop_anpr(request: ANPRRequest):
    if request.stream_id not in active_streams:
        return JSONResponse(content={"message": "Stream not running."})

    stop_event = active_streams[request.stream_id]["stop_event"]
    stop_event.set()
    stop_stream(request.stream_id)
    del active_streams[request.stream_id]
    return JSONResponse(content={"message": f"Stopped ANPR for stream: {request.stream_id}"})




def start_hls_ffmpeg(stream_id):
    os.makedirs(f"hls/{stream_id}", exist_ok=True)
    ffmpeg_cmd = [
        "ffmpeg", "-re", "-loop", "1",
        "-i", f"app/streams/{stream_id}.jpg",
        "-c:v", "libx264", "-tune", "zerolatency", "-preset", "ultrafast",
        "-f", "hls",
        "-hls_time", "1", "-hls_list_size", "3", "-hls_flags", "delete_segments",
        "-y", f"hls/{stream_id}/index.m3u8"
    ]
    return subprocess.Popen(ffmpeg_cmd)
