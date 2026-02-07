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
from datetime import datetime

# Add parent directory to path to import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config import (
    DISCOVERY_BROADCAST,
    DISCOVERY_PORT,
)

# Constants
url = 'rtsp://192.168.144.25:8554/main.264' #'rtsp://192.168.0.181:8554/stream'
motion_threshold = 0.2  # Fraction of pixels that must change to trigger motion
pixel_diff_threshold = 25  # Minimum pixel difference to count as change
blur_sigma = 1.5  # Sigma for Gaussian blur to reduce noise
kernel_size = 5
MOTION_PORT = 5555
NODE_ID = f"{socket.gethostname()}-motion-{uuid.uuid4().hex[:6]}"

def get_local_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"

# Function for Gaussian blur using OpenCV
def gaussian_blur(image, kernel_size, sigma):
    return cv2.GaussianBlur(image, (kernel_size, kernel_size), sigma)

# Function for motion detection
def detect_motion(prev_frame, current_frame, pixel_diff_threshold):
    if prev_frame is None:
        return None
    
    diff = np.abs(current_frame - prev_frame)
    changed_pixels = (diff > pixel_diff_threshold).astype(np.float32)
    change_ratio = np.mean(changed_pixels)
    
    return change_ratio


def discovery_loop(stop_event, peers_info):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind(("", DISCOVERY_PORT))
    sock.settimeout(1.0)

    while not stop_event.is_set():
        try:
            sock.sendto(
                json.dumps(
                    {
                        "type": "discover",
                        "node_id": NODE_ID,
                        "ip": get_local_ip(),
                        "port": MOTION_PORT,
                    }
                ).encode("utf-8"),
                (DISCOVERY_BROADCAST, DISCOVERY_PORT),
            )

            data, addr = sock.recvfrom(4096)
            message = json.loads(data.decode("utf-8"))

            if message.get("node_id") != NODE_ID and message.get("type") in {"discover", "announce"}:
                peer_id = message.get("node_id")
                if peer_id:
                    peers_info[peer_id] = {
                        "ip": message.get("ip") or addr[0],
                        "port": message.get("port", MOTION_PORT),
                    }

                    if message.get("type") == "discover":
                        sock.sendto(
                            json.dumps({
                                "type": "announce",
                                "node_id": NODE_ID,
                                "ip": get_local_ip(),
                                "port": MOTION_PORT,
                            }).encode("utf-8"), (addr[0], DISCOVERY_PORT)
                        )
        except Exception:
            pass

        if peers_info:
            print(f"[Discovery:{NODE_ID}] Known peers: {list(peers_info.keys())}")
        time.sleep(15 if peers_info else 2)

    sock.close()


# ZeroMQ setup
context = zmq.Context()
pub_socket = context.socket(zmq.PUB)
pub_socket.bind(f"tcp://*:{MOTION_PORT}")
peers_info = {}
stop_event = threading.Event()

discovery_thread = threading.Thread(
    target=discovery_loop, args=(stop_event, peers_info), daemon=True
)
discovery_thread.start()

print(f"[PUB:{NODE_ID}] Listening on tcp://*:{MOTION_PORT}")
print(f"[PUB:{NODE_ID}] Local IP: {get_local_ip()}\n")

# Main setup
probe = ffmpeg.probe(url)
video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
width = int(video_info['width'])
height = int(video_info['height'])

process = (ffmpeg
    .input(url, rtsp_transport='udp')
    # .filter('fps', fps=1)  # Limit to 1 FPS for processing
    .output('pipe:', format='rawvideo', pix_fmt='gray8')
    .global_args('-loglevel', 'quiet')
    .run_async(pipe_stdout=True))

bytes_per_frame = width * height
prev_blurred_frame = None
last_motion_state = 0

print("Starting motion detection... Press Ctrl+C to stop.")

try:
    while True:
        start_time = time.perf_counter()
        
        in_bytes = process.stdout.read(bytes_per_frame)
        
        if len(in_bytes) != bytes_per_frame:
            print("Incomplete frame received. Try again...")
            break
        
        frame = np.frombuffer(in_bytes, np.uint8).reshape((height, width))
        
        blurred_frame = gaussian_blur(frame, kernel_size, blur_sigma)
        
        change_ratio = detect_motion(prev_blurred_frame, blurred_frame, pixel_diff_threshold)
        
        end_time = time.perf_counter()
        latency = (end_time - start_time) * 1000  # Convert to milliseconds
        
        motion_detected = change_ratio is not None and change_ratio > motion_threshold

        if motion_detected:
            if last_motion_state == 0:
                pub_socket.send_json({
                    "type": "motion_flag",
                    "node_id": NODE_ID,
                    "flag": 1,
                    "ts": datetime.now().isoformat(),
                })
                print("Motion detected: sent flag 1 with image")

            # Encode frame as JPEG
            success, encoded_img = cv2.imencode('.jpg', frame)
            if success:
                image_bytes = encoded_img.tobytes()
                image_b64 = base64.b64encode(image_bytes).decode("ascii")
                message = {
                    "type": "image",
                    "node_id": NODE_ID,
                    "filename": "motion.jpg",
                    "size": len(image_bytes),
                    "image_data": image_b64,
                    "publish_ts": datetime.now().isoformat(),
                    "ts": datetime.now().isoformat(),
                }
                pub_socket.send_json(message)
            else:
                print("Failed to encode image")
        elif last_motion_state == 1:
            # Send a single 0 when motion ends to avoid repeated traffic
            pub_socket.send_json({
                "type": "motion_flag",
                "node_id": NODE_ID,
                "flag": 0,
                "ts": datetime.now().isoformat(),
            })
            print("Motion ended: sent flag 0")
        
        prev_blurred_frame = blurred_frame
        last_motion_state = 1 if motion_detected else 0

except KeyboardInterrupt:
    print("Stopping motion detection.")
finally:
    stop_event.set()
    process.terminate()
    pub_socket.close()
    context.term()