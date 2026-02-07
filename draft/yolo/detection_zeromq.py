from ultralytics import YOLO
import base64
import json
import os
import socket
import threading
import time
from datetime import datetime

import cv2
import numpy as np
import zmq

import sys

# Add parent directory to path to import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config import (
    DISCOVERY_BROADCAST,
    DISCOVERY_PORT,
)

def load_model(model_path):
    """Load the YOLO model from the given path."""
    return YOLO(model_path)

def run_inference(model, image):
    """Run inference on the image using the model."""
    return model(image)

def print_results(results, model):
    """Print the detection results to the console."""
    print("Detections:")
    for result in results:
        for box in result.boxes:
            class_id = int(box.cls)
            confidence = float(box.conf)
            bbox = box.xyxy.tolist()[0]  # [x1, y1, x2, y2]
            class_name = model.names[class_id]
            print(f"Class: {class_name}, Confidence: {confidence:.2f}, BBox: {bbox}")

def save_results(results, model, output_dir, base_name):
    """Save the detection results to a text file and annotated image."""
    os.makedirs(output_dir, exist_ok=True)
    # txt_file = os.path.join(output_dir, f"{base_name}.txt")
    img_file = os.path.join(output_dir, f"{base_name}.jpg")

    # with open(txt_file, "w") as f:
    #     f.write("Detections:\n")
    #     for result in results:
    #         for box in result.boxes:
    #             class_id = int(box.cls)
    #             confidence = float(box.conf)
    #             bbox = box.xyxy.tolist()[0]
    #             class_name = model.names[class_id]
    #             f.write(f"Class: {class_name}, Confidence: {confidence:.2f}, BBox: {bbox}\n")

    for result in results:
        result.save(filename=img_file)

    # print(f"Results saved to {txt_file} and {img_file}")


def get_local_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"


def discovery_loop(stop_event, peers_info, node_id, port):
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
                        "node_id": node_id,
                        "ip": get_local_ip(),
                        "port": port,
                    }
                ).encode("utf-8"),
                (DISCOVERY_BROADCAST, DISCOVERY_PORT),
            )

            data, addr = sock.recvfrom(4096)
            message = json.loads(data.decode("utf-8"))

            if message.get("node_id") != node_id and message.get("type") in {"discover", "announce"}:
                peer_id = message.get("node_id")
                if peer_id:
                    peers_info[peer_id] = {
                        "ip": message.get("ip") or addr[0],
                        "port": message.get("port", port),
                    }

                    if message.get("type") == "discover":
                        sock.sendto(
                            json.dumps({
                                "type": "announce",
                                "node_id": node_id,
                                "ip": get_local_ip(),
                                "port": port,
                            }).encode("utf-8"), (addr[0], DISCOVERY_PORT)
                        )
        except Exception:
            pass

        if peers_info:
            print(f"[Discovery:{node_id}] Known peers: {list(peers_info.keys())}")
        time.sleep(15 if peers_info else 2)

    sock.close()


def subscriber_loop(context, peers_info, stop_event, model, output_dir):
    sub_socket = context.socket(zmq.SUB)
    sub_socket.setsockopt_string(zmq.SUBSCRIBE, "")

    connected_peers = set()
    image_count = 0

    while not stop_event.is_set():
        try:
            for peer_id, info in peers_info.items():
                if peer_id not in connected_peers:
                    sub_socket.connect(f"tcp://{info['ip']}:{info['port']}")
                    connected_peers.add(peer_id)
                    print(f"[SUB] Connected to {peer_id} at {info['ip']}:{info['port']}")
                    time.sleep(0.2)

            if sub_socket.poll(1000):
                message = sub_socket.recv_json()
                if message.get("type") != "image":
                    continue

                image_b64 = message.get("image_data")
                sender = message.get("node_id", "unknown")
                if not image_b64:
                    continue

                jpeg_bytes = base64.b64decode(image_b64)
                frame = cv2.imdecode(np.frombuffer(jpeg_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
                if frame is None:
                    print("[SUB] Failed to decode image")
                    continue

                image_count += 1
                start = time.time()
                results = run_inference(model, frame)
                latency = time.time() - start

                ts = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                base_name = f"{sender}_{ts}"
                print(f"[SUB] Inference #{image_count} from {sender} in {latency:.3f}s")
                save_results(results, model, output_dir, base_name)

        except zmq.error.ContextTerminated:
            break
        except Exception as e:
            if not stop_event.is_set():
                print(f"[SUB] Error: {e}")
            connected_peers.clear()

    sub_socket.close()

if __name__ == "__main__":
    model_path = os.path.join(os.path.dirname(__file__), "yolo26n_ncnn_model")
    output_dir = os.path.join(os.path.dirname(__file__), "detections")
    node_id = f"{socket.gethostname()}-yolo"
    motion_port = 5555

    model = load_model(model_path)

    context = zmq.Context()
    peers_info = {}
    stop_event = threading.Event()

    sub_thread = threading.Thread(
        target=subscriber_loop,
        args=(context, peers_info, stop_event, model, output_dir),
        daemon=True,
    )
    sub_thread.start()

    discovery_thread = threading.Thread(
        target=discovery_loop,
        args=(stop_event, peers_info, node_id, motion_port),
        daemon=True,
    )
    discovery_thread.start()

    print(f"[SUB:{node_id}] Listening for images on port {motion_port}")
    print(f"[SUB:{node_id}] Local IP: {get_local_ip()}\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[INFO] Shutting down...")
    finally:
        stop_event.set()
        context.term()
