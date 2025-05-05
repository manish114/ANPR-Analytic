# app/stream_manager.py

import threading

stream_threads = {}
stop_flags = {}

def start_stream(stream_id, target_func, *args):
    if stream_id in stream_threads:
        return False  # Already running

    stop_flags[stream_id] = threading.Event()
    thread = threading.Thread(target=target_func, args=(*args, stop_flags[stream_id]))
    thread.start()
    stream_threads[stream_id] = thread
    return True

def stop_stream(stream_id):
    if stream_id in stop_flags:
        stop_flags[stream_id].set()
        return True
    return False

def is_stream_running(stream_id):
    return stream_id in stream_threads and stream_threads[stream_id].is_alive()
