"""
Image Publisher - Publish images via ZeroMQ PUB/SUB
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

import zmq

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


# NODE_ID = f"{socket.gethostname()}-{uuid.uuid4().hex[:6]}"
NODE_ID = f"{socket.gethostname()}"

IMG_PATH = os.path.join(os.path.dirname(__file__), "bus.jpg")

def image_to_base64(image_path):
    """Convert image file to base64 string"""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

def base64_to_image(base64_data, output_path):
    """Convert base64 string back to image file"""
    with open(output_path, "wb") as img_file:
        img_file.write(base64.b64decode(base64_data))

def publish_image(pub_socket, image_path, node_id):
    """Publish an image through ZeroMQ"""
    try:
        filename = os.path.basename(image_path)
        file_size = os.path.getsize(image_path)
        
        print(f"[PUB:{node_id}] Reading image: {filename} ({file_size} bytes)")
        
        # Convert image to base64
        image_data = image_to_base64(image_path)
        
        # Create message with metadata including publish timestamp
        message = {
            "type": "image",
            "node_id": node_id,
            "filename": filename,
            "size": file_size,
            "image_data": image_data,
            "publish_ts": datetime.now().isoformat(),
            "ts": datetime.now().isoformat(),  # Keep for compatibility
        }
        
        # Send via PUB socket
        pub_socket.send_json(message)
        print(f"[PUB:{node_id}] Published: {filename} at {message['publish_ts']}")
        
    except Exception as e:
        print(f"[PUB:{node_id}] Error publishing image: {e}")

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

    # PUB socket - publish images
    pub_socket = context.socket(zmq.PUB)
    pub_socket.bind(f"tcp://*:{NODE_PORT}")
    
    print(f"[PUB:{NODE_ID}] Starting Image Publisher")
    print(f"[PUB:{NODE_ID}] Listening on tcp://*:{NODE_PORT}")
    print(f"[PUB:{NODE_ID}] Local IP: {get_local_ip()}\n")

    # Start discovery thread
    discovery_thread = threading.Thread(
        target=discovery_loop, args=(stop_event, peers_info), daemon=True
    )
    discovery_thread.start()

    try:
        time.sleep(2)
        
        # Example: Publish an image every 10 seconds
        # Replace with your actual image path
        test_image = IMG_PATH
        
        if os.path.exists(test_image):
            print(f"[PUB:{NODE_ID}] Found image: {test_image}")
            print(f"[PUB:{NODE_ID}] Starting infinite publishing loop...\n")
            
            while True:
                publish_image(pub_socket, test_image, NODE_ID)
                time.sleep(2)
        else:
            print(f"[PUB:{NODE_ID}] Image '{test_image}' not found in current directory.")
            print(f"[PUB:{NODE_ID}] Exiting...")
            return

    except KeyboardInterrupt:
        print("\n[INFO] Shutting down...")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        stop_event.set()
        pub_socket.close()
        context.term()


if __name__ == "__main__":
    main()
