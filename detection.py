import base64
import json
import os
import socket
import threading
import time
import logging
from datetime import datetime
import cv2
import numpy as np
import zmq
import sys
from ultralytics import YOLO

# Add parent directory to path to import config
sys.path.append('.')

from config import (
    MOTION_IMAGE_PORT,
    DETECTION_PORT,
    MODEL_PATH,
)
from utils import ZMQNode

class DetectionProcessor(ZMQNode):
    def __init__(self, model_path):
        super().__init__('detection')
        self.pub_port = DETECTION_PORT
        self.model_path = model_path
        self.model = self.load_model()
        self.sub_socket = self.context.socket(zmq.SUB)
        self.sub_socket.setsockopt_string(zmq.SUBSCRIBE, "")
        self.det_pub = self.context.socket(zmq.PUB)
        self.det_pub.bind(f"tcp://*:{DETECTION_PORT}")
        self.image_count = 0
        self.motion_source_endpoint = f"tcp://127.0.0.1:{MOTION_IMAGE_PORT}"

    def load_model(self):
        """Load the YOLO model from the given path."""
        return YOLO(self.model_path)

    def run_inference(self, image):
        """Run inference on the image using the model."""
        return self.model(image)

    def save_image(self, results, sender, timestamp):
        """Save YOLO-annotated result image to disk."""
        output_dir = "detection_images"
        os.makedirs(output_dir, exist_ok=True)
        safe_ts = timestamp.replace(":", "-")
        image_path = os.path.join(output_dir, f"{sender}_{safe_ts}.jpg")
        if not results:
            return
        annotated_image = results[0].plot()
        cv2.imwrite(image_path, annotated_image)
        logging.info(f"Saved result image: {image_path}")

    def publish_detection_results(self, detections, timestamp, sender):
        """Publish detection results via ZeroMQ."""
        message = {
            "type": "detection_results",
            "node_id": self.node_id,
            "sender": sender,
            "detections": detections,
            "ts": timestamp,
        }
        self.det_pub.send_json(message)
        logging.info(f"Detection results published: {detections}")

    def subscriber_loop(self):
        self.sub_socket.connect(self.motion_source_endpoint)
        print(f"[SUB] Connected to {self.motion_source_endpoint}")

        while not self.stop_event.is_set():
            try:
                if self.sub_socket.poll(1000):
                    recv_ts = datetime.now().isoformat()
                    message = self.sub_socket.recv_json()
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

                    self.image_count += 1
                    results = self.run_inference(frame)
                    detection_ts = datetime.now().isoformat()

                    # Optional: uncomment to save each annotated result image
                    # self.save_image(results, sender, detection_ts)

                    print(f"[SUB] Inference #{self.image_count} from {sender}")

                    # Prepare detection results
                    detections = []
                    for result in results:
                        for box in result.boxes:
                            class_id = int(box.cls)
                            confidence = float(box.conf)
                            class_name = self.model.names[class_id]
                            detections.append({
                                "class": class_name,
                                "confidence": confidence
                            })

                    send_ts = message.get("ts", "unknown")
                    logging.info(f"Image from {sender} - Send TS: {send_ts} - Recv TS: {recv_ts} - Detect TS: {detection_ts} - Results: {len(detections)} detections")

                    # Publish detection results
                    self.publish_detection_results(detections, detection_ts, sender)

            except zmq.error.ContextTerminated:
                break
            except Exception as e:
                if not self.stop_event.is_set():
                    print(f"[SUB] Error: {e}")

        self.sub_socket.close()

    def run(self):
        # Discovery disabled; using fixed local endpoint for motion images

        # Start subscriber thread
        sub_thread = threading.Thread(target=self.subscriber_loop, daemon=True)
        sub_thread.start()

        logging.info(f"[DET_PUB:{self.node_id}] Listening on tcp://*:{DETECTION_PORT}")
        logging.info(f"[SUB:{self.node_id}] Subscribing to motion images on port {MOTION_IMAGE_PORT}")
        logging.info(f"[PUB:{self.node_id}] Local IP: {self.get_local_ip()}")

        print(f"[DET:{self.node_id}] Detection processor started")
        print(f"[DET:{self.node_id}] Local IP: {self.get_local_ip()}\n")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logging.info("User stopped detection processor with Ctrl+C.")
        finally:
            self.det_pub.close()
            self.cleanup()

if __name__ == "__main__":
    # Model path - NCNN model in root dir
    model_path = MODEL_PATH

    processor = DetectionProcessor(model_path)
    processor.run()
