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
    MOTION_FLAG_PORT,
    MOTION_IMAGE_PORT,
    MOTION_URL,
    MOTION_THRESHOLD,
    MOTION_FPS,
    PIXEL_DIFF_THRESHOLD,
    BLUR_SIGMA,
    KERNEL_SIZE,
)
from utils import ZMQNode

def get_video_dimensions(url):
    """Probe the video stream and return width and height."""
    probe = ffmpeg.probe(MOTION_URL)
    video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    width = int(video_info['width'])
    height = int(video_info['height'])
    return width, height

class MotionDetector(ZMQNode):
    def __init__(self):
        super().__init__('motion')
        self.pub_port = MOTION_IMAGE_PORT  # For discovery
        self.flag_pub = self.context.socket(zmq.PUB)
        self.flag_pub.bind(f"tcp://*:{MOTION_FLAG_PORT}")
        self.image_pub = self.context.socket(zmq.PUB)
        self.image_pub.bind(f"tcp://*:{MOTION_IMAGE_PORT}")
        self.prev_blurred_frame = None
        self.last_motion_state = 0

    def gaussian_blur(self, image, kernel_size, sigma):
        return cv2.GaussianBlur(image, (kernel_size, kernel_size), sigma)

    def detect_motion(self, prev_frame, current_frame, pixel_diff_threshold):
        if prev_frame is None:
            return None
        
        diff = np.abs(current_frame - prev_frame)
        changed_pixels = (diff > pixel_diff_threshold).astype(np.float32)
        change_ratio = np.mean(changed_pixels)
        
        return change_ratio

    def publish_motion_flag(self, flag, timestamp):
        self.flag_pub.send_json({
            "type": "motion_flag",
            "node_id": self.node_id,
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
                "node_id": self.node_id,
                "size": f"{image_size_kb:.2f} KB",
                "image_data": image_b64,
                "ts": timestamp,
            }
            self.image_pub.send_json(message)
            logging.info(f"{self.node_id} triggered motion event at {timestamp} and published image ({image_size_kb:.2f} KB)")
        else:
            logging.error("Failed to encode image")

    def run(self):
        # Start discovery thread
        self.start_discovery()

        logging.info(f"[FLAG_PUB:{self.node_id}] Listening on tcp://*:{MOTION_FLAG_PORT}")
        logging.info(f"[IMAGE_PUB:{self.node_id}] Listening on tcp://*:{MOTION_IMAGE_PORT}")
        logging.info(f"[PUB:{self.node_id}] Local IP: {self.get_local_ip()}")

        width, height = get_video_dimensions(MOTION_URL)

        process = (ffmpeg
            .input(MOTION_URL, rtsp_transport='udp')
            .filter('fps', fps=MOTION_FPS)  # Limit to MOTION_FPS FPS for processing
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
            process.terminate()
            self.flag_pub.close()
            self.image_pub.close()
            self.cleanup()

if __name__ == "__main__":
    detector = MotionDetector()
    detector.run()
