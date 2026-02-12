import ffmpeg
import base64
import json
import os
import sys
import socket
import threading
import uuid
import numpy as np
import cv2
import time
import zmq
import logging
from datetime import datetime

# Add parent directory to path to import config
sys.path.append('.')

from config import (
    DISCOVERY_BROADCAST,
    DISCOVERY_PORT,
    MOTION_FLAG_PORT,
    MOTION_IMAGE_PORT,
    MOTION_URL,
    MOTION_THRESHOLD,
    PIXEL_DIFF_THRESHOLD,
    BLUR_SIGMA,
    KERNEL_SIZE,
)

# Configure logging
logging.basicConfig(
    filename='log.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
# Add console handler
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(message)s')
logging.getLogger('').addHandler(console)

# Constants
NODE_ID = f"{socket.gethostname()}-motion"

def get_video_dimensions(url):
    """Probe the video stream and return width and height."""
    probe = ffmpeg.probe(MOTION_URL)
    video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    width = int(video_info['width'])
    height = int(video_info['height'])
    return width, height

class MotionDetector:
    def __init__(self):
        self.context = zmq.Context()
        self.flag_pub = self.context.socket(zmq.PUB)
        self.flag_pub.bind(f"tcp://*:{MOTION_FLAG_PORT}")
        self.image_pub = self.context.socket(zmq.PUB)
        self.image_pub.bind(f"tcp://*:{MOTION_IMAGE_PORT}")
        self.peers_info = {}
        self.stop_event = threading.Event()
        self.prev_blurred_frame = None
        self.last_motion_state = 0

    def get_local_ip(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except OSError:
            return "127.0.0.1"

    def gaussian_blur(self, image, kernel_size, sigma):
        return cv2.GaussianBlur(image, (kernel_size, kernel_size), sigma)

    def detect_motion(self, prev_frame, current_frame, pixel_diff_threshold):
        if prev_frame is None:
            return None
        
        diff = np.abs(current_frame - prev_frame)
        changed_pixels = (diff > pixel_diff_threshold).astype(np.float32)
        change_ratio = np.mean(changed_pixels)
        
        return change_ratio

    def discovery_loop(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.bind(("", DISCOVERY_PORT))
        sock.settimeout(1.0)

        while not self.stop_event.is_set():
            try:
                sock.sendto(
                    json.dumps(
                        {
                            "type": "discover",
                            "node_id": NODE_ID,
                            "ip": self.get_local_ip(),
                            "flag_port": MOTION_FLAG_PORT,
                            "image_port": MOTION_IMAGE_PORT,
                        }
                    ).encode("utf-8"),
                    (DISCOVERY_BROADCAST, DISCOVERY_PORT),
                )

                data, addr = sock.recvfrom(4096)
                message = json.loads(data.decode("utf-8"))

                if message.get("node_id") != NODE_ID and message.get("type") in {"discover", "announce"}:
                    peer_id = message.get("node_id")
                    if peer_id:
                        self.peers_info[peer_id] = {
                            "ip": message.get("ip") or addr[0],
                            "flag_port": message.get("flag_port", MOTION_FLAG_PORT),
                            "image_port": message.get("image_port", MOTION_IMAGE_PORT),
                        }

                        if message.get("type") == "discover":
                            sock.sendto(
                                json.dumps({
                                    "type": "announce",
                                    "node_id": NODE_ID,
                                    "ip": self.get_local_ip(),
                                    "flag_port": MOTION_FLAG_PORT,
                                    "image_port": MOTION_IMAGE_PORT,
                                }).encode("utf-8"), (addr[0], DISCOVERY_PORT)
                            )
            except Exception:
                pass

            if self.peers_info:
                print(f"[Discovery:{NODE_ID}] Known peers: {list(self.peers_info.keys())}")
            time.sleep(15 if self.peers_info else 2)

        sock.close()

    def publish_motion_flag(self, flag, timestamp):
        self.flag_pub.send_json({
            "type": "motion_flag",
            "node_id": NODE_ID,
            "flag": flag,
            "ts": timestamp,
        })

    def publish_motion_image(self, frame, timestamp):
        success, encoded_img = cv2.imencode('.jpg', frame)
        if success:
            image_bytes = encoded_img.tobytes()
            image_b64 = base64.b64encode(image_bytes).decode("ascii")
            image_size_kb = len(image_bytes) / 1024
            message = {
                "type": "image",
                "node_id": NODE_ID,
                "size": f"{image_size_kb:.2f} KB",
                "image_data": image_b64,
                "ts": timestamp,
            }
            self.image_pub.send_json(message)
            logging.info(f"{NODE_ID} triggered motion event at {timestamp} and published image ({image_size_kb:.2f} KB)")
        else:
            logging.error("Failed to encode image")

    def run(self):
        # Start discovery thread
        discovery_thread = threading.Thread(target=self.discovery_loop, daemon=True)
        discovery_thread.start()

        logging.info(f"[FLAG_PUB:{NODE_ID}] Listening on tcp://*:{MOTION_FLAG_PORT}")
        logging.info(f"[IMAGE_PUB:{NODE_ID}] Listening on tcp://*:{MOTION_IMAGE_PORT}")
        logging.info(f"[PUB:{NODE_ID}] Local IP: {self.get_local_ip()}")

        width, height = get_video_dimensions(MOTION_URL)

        process = (ffmpeg
            .input(MOTION_URL, rtsp_transport='udp')
            .filter('fps', fps=10)  # Limit to 10 FPS for processing
            .output('pipe:', format='rawvideo', pix_fmt='bgr24')
            .global_args('-loglevel', 'quiet')
            .run_async(pipe_stdout=True))

        bytes_per_frame = width * height * 3

        logging.info("Starting motion detection... Press Ctrl+C to stop.")

        try:
            while True:
                in_bytes = process.stdout.read(bytes_per_frame)
                
                if len(in_bytes) != bytes_per_frame:
                    logging.warning("Incomplete frame received. Try again...")
                    break
                
                frame = np.frombuffer(in_bytes, np.uint8).reshape((height, width, 3))

                frame_gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
                
                blurred_frame = self.gaussian_blur(frame_gray, KERNEL_SIZE, BLUR_SIGMA)
                
                change_ratio = self.detect_motion(self.prev_blurred_frame, blurred_frame, PIXEL_DIFF_THRESHOLD)
                
                motion_detected = change_ratio is not None and change_ratio > MOTION_THRESHOLD

                if motion_detected and self.last_motion_state == 0:
                    event_ts = datetime.now().time().isoformat()
                    self.publish_motion_flag(1, event_ts)
                    self.publish_motion_image(frame, event_ts)
                elif not motion_detected and self.last_motion_state == 1:
                    event_ts = datetime.now().time().isoformat()
                    self.publish_motion_flag(0, event_ts)
                    print("Motion ended: sent flag 0")

                self.prev_blurred_frame = blurred_frame
                self.last_motion_state = 1 if motion_detected else 0

                if change_ratio is not None:
                    print(f"Motion ratio: {change_ratio:.4f} - {'MOTION DETECTED' if motion_detected else 'No motion'}")

        except KeyboardInterrupt:
            logging.info("User stopped motion detection with Ctrl+C.")
        finally:
            self.stop_event.set()
            process.terminate()
            self.flag_pub.close()
            self.image_pub.close()
            self.context.term()

if __name__ == "__main__":
    detector = MotionDetector()
    detector.run()
