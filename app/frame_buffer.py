# app/frame_buffer.py

from collections import defaultdict
import threading

# Store latest frame for each stream
latest_frames = defaultdict(lambda: None)

# Locks to protect concurrent access
frame_locks = defaultdict(threading.Lock)

def update_frame(stream_id, frame):
    with frame_locks[stream_id]:
        latest_frames[stream_id] = frame

def get_latest_frame(stream_id):
    with frame_locks[stream_id]:
        return latest_frames[stream_id]
