# app/main.py

from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.responses import JSONResponse, StreamingResponse
import threading
from anpr_engine import process_video, get_frame, stop_stream

app = FastAPI()

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
