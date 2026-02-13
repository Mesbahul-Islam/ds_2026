import ffmpeg
import json
import os
import sys
import threading
import logging
import zmq
import subprocess

# Add parent directory to path to import config
sys.path.append('.')

from config import (
    MOTION_FLAG_PORT,
    MOTION_URL,
    RECORD_DURATION,
    RECORD_FPS,
)
from utils import ZMQNode

class Recorder(ZMQNode):
    def __init__(self):
        super().__init__('recorder')
        self.sub = self.context.socket(zmq.SUB)
        self.sub.connect(f"tcp://localhost:{MOTION_FLAG_PORT}")
        self.sub.setsockopt_string(zmq.SUBSCRIBE, "")
        self.is_recording = False

    def record_clip(self, start_ts):
        """Record a 15-second clip using FFmpeg."""
        os.makedirs("recordings", exist_ok=True)
        safe_ts = start_ts.replace(":", "-")
        filename = f"recordings/record_{safe_ts}.mp4"

        cmd = [
            'ffmpeg',
            '-i', MOTION_URL,
            '-t', str(RECORD_DURATION),
            '-r', str(RECORD_FPS),
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-y', filename
        ]

        try:
            subprocess.run(cmd, check=True)
            logging.info(f"Saved recording: {filename}")
        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to record: {e}")
        finally:
            self.is_recording = False

    def subscriber_loop(self):
        """Listen for motion flags and trigger recordings."""
        while not self.stop_event.is_set():
            try:
                if self.sub.poll(1000):
                    msg = self.sub.recv_json()
                    if msg.get("type") == "motion_flag":
                        self.handle_flag(msg)
            except zmq.error.ContextTerminated:
                break

    def handle_flag(self, msg):
        """Handle motion flag messages."""
        flag = msg["flag"]
        ts = msg["ts"]
        if flag == 1 and not self.is_recording:
            self.is_recording = True
            threading.Thread(target=self.record_clip, args=(ts,), daemon=True).start()
            logging.info(f"Started recording on motion at {ts}")

    def run(self):
        # Start discovery if needed
        self.start_discovery()

        logging.info(f"[RECORDER:{self.node_id}] Listening on motion flags")
        logging.info(f"[RECORDER:{self.node_id}] Local IP: {self.get_local_ip()}")

        print(f"[RECORDER:{self.node_id}] Recorder started")
        print(f"[RECORDER:{self.node_id}] Local IP: {self.get_local_ip()}\n")

        try:
            self.subscriber_loop()
        except KeyboardInterrupt:
            logging.info("User stopped recorder with Ctrl+C.")
        finally:
            self.sub.close()
            self.cleanup()

if __name__ == "__main__":
    recorder = Recorder()
    recorder.run()
