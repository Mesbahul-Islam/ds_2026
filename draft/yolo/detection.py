### https://docs.ultralytics.com/guides/raspberry-pi/

"""
Image Subscriber with YOLO Detection - Subscribe to images, decode, apply YOLO detection, and measure latency
"""
import json
import os
import sys
import socket
import threading
import time
import uuid
from datetime import datetime
import base64
import cv2
import numpy as np
from PIL import Image
from io import BytesIO

import zmq
from ultralytics import YOLO

# Add parent directory to path to import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config import (
    DISCOVERY_BROADCAST,
    DISCOVERY_PORT,
    NODE_PORT,
)

def get_local_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"

NODE_ID = f"{socket.gethostname()}-sub"

def base64_to_image(base64_data):
    """Convert base64 string to PIL Image"""
    image_data = base64.b64decode(base64_data)
    image = Image.open(BytesIO(image_data))
    return image

def pil_to_cv2(pil_image):
    """Convert PIL Image to OpenCV format"""
    open_cv_image = np.array(pil_image)
    # Convert RGB to BGR
    open_cv_image = open_cv_image[:, :, ::-1].copy()
    return open_cv_image

def detect_objects(image, model):
    """Apply YOLO detection on the image"""
    results = model(image)
    return results

def process_image(message, model):
    """Process received image: decode, detect, measure latency"""
    try:
        # Decode base64 to image
        pil_image = base64_to_image(message['image_data'])
        cv_image = pil_to_cv2(pil_image)

        # Get publish timestamp
        publish_ts = datetime.fromisoformat(message['publish_ts'])
        receive_ts = datetime.now()

        # Run YOLO detection
        detection_start = time.time()
        results = detect_objects(cv_image, model)
        detection_end = time.time()

        # Calculate latencies
        receive_latency = (receive_ts - publish_ts).total_seconds() * 1000  # ms
        detection_latency = (detection_end - detection_start) * 1000  # ms

        # Print results
        print(f"[SUB:{NODE_ID}] Received: {message['filename']} ({message['size']} bytes)")
        print(f"[SUB:{NODE_ID}] Receive latency: {receive_latency:.2f} ms")
        print(f"[SUB:{NODE_ID}] Detection latency: {detection_latency:.2f} ms")

        # Print detection results
        for result in results:
            boxes = result.boxes
            if boxes is not None:
                for box in boxes:
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    class_name = model.names[cls]
                    print(f"[SUB:{NODE_ID}] Detected: {class_name} with confidence {conf:.2f}")

        print()

    except Exception as e:
        print(f"[SUB:{NODE_ID}] Error processing image: {e}")

def discovery_loop(stop_event, peers_info):
    """Discover peers on the network"""
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
                        "port": NODE_PORT,
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
                        "port": message.get("port", NODE_PORT),
                    }

                    if message.get("type") == "discover":
                        sock.sendto(
                            json.dumps({
                                "type": "announce",
                                "node_id": NODE_ID,
                                "ip": get_local_ip(),
                                "port": NODE_PORT,
                            }).encode("utf-8"), (addr[0], DISCOVERY_PORT)
                        )
        except Exception:
            pass

        if peers_info:
            print(f"[Discovery:{NODE_ID}] Known peers: {list(peers_info.keys())}")
        time.sleep(15 if peers_info else 2)

    sock.close()

def main():
    context = zmq.Context()

    peers_info = {}
    stop_event = threading.Event()

    # SUB socket - subscribe to images
    sub_socket = context.socket(zmq.SUB)
    sub_socket.setsockopt_string(zmq.SUBSCRIBE, "")  # Subscribe to all topics
    sub_socket.connect(f"tcp://localhost:{NODE_PORT}")  # Connect to publisher

    print(f"[SUB:{NODE_ID}] Starting Image Subscriber with YOLO Detection")
    print(f"[SUB:{NODE_ID}] Connected to tcp://localhost:{NODE_PORT}")
    print(f"[SUB:{NODE_ID}] Local IP: {get_local_ip()}\n")

    # Load YOLO model
    print("[SUB:{NODE_ID}] Loading YOLO model...")
    model = YOLO('yolov8n.pt')  # You can change to other models like 'yolov8s.pt', 'yolov8m.pt', etc.
    print("[SUB:{NODE_ID}] YOLO model loaded.\n")

    # Start discovery thread
    discovery_thread = threading.Thread(
        target=discovery_loop, args=(stop_event, peers_info), daemon=True
    )
    discovery_thread.start()

    try:
        while True:
            # Receive message
            message = sub_socket.recv_json()
            if message.get('type') == 'image':
                process_image(message, model)

    except KeyboardInterrupt:
        print("\n[INFO] Shutting down...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        stop_event.set()
        sub_socket.close()
        context.term()

if __name__ == "__main__":
    main()
