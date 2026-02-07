"""
Image Subscriber - Receive and save images from ZeroMQ PUB
"""
import json
import os
import sys
import socket
import threading
import time
import uuid
import base64
from datetime import datetime

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


NODE_ID = f"{socket.gethostname()}"


def base64_to_image(base64_data, output_path):
    """Convert base64 string back to image file"""
    with open(output_path, "wb") as img_file:
        img_file.write(base64.b64decode(base64_data))


def subscriber_loop(context, peers_info, stop_event, output_dir="received_images"):
    """Subscribe to and receive images from peers"""
    sub_socket = context.socket(zmq.SUB)
    sub_socket.setsockopt_string(zmq.SUBSCRIBE, "")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    connected_peers = set()
    image_count = 0
    
    while not stop_event.is_set():
        try:
            for peer_id, info in peers_info.items():
                if peer_id not in connected_peers:
                    sub_socket.connect(f"tcp://{info['ip']}:{info['port']}")
                    connected_peers.add(peer_id)
                    print(f"[SUB:{NODE_ID}] Connected to {peer_id} at {info['ip']}:{info['port']}")
            
            if sub_socket.poll(1000):
                message = sub_socket.recv_json()
                
                if message.get("type") == "image":
                    filename = message.get("filename")
                    image_data = message.get("image_data")
                    sender = message.get("node_id")
                    size = message.get("size")
                    publish_ts = message.get("publish_ts") or message.get("ts")  # Fallback for compatibility
                    
                    # Calculate delay
                    receive_time = datetime.now()
                    if publish_ts:
                        publish_time = datetime.fromisoformat(publish_ts)
                        delay_ms = (receive_time - publish_time).total_seconds() * 1000
                    else:
                        delay_ms = 0
                    
                    # Save received image with sender info in filename
                    output_path = os.path.join(output_dir, f"{sender}_{filename}")
                    base64_to_image(image_data, output_path)
                    image_count += 1
                    
                    print(f"\n✓ Received image #{image_count}: {filename}")
                    print(f"  From: {sender} | Size: {size} bytes")
                    print(f"  Published: {publish_ts}")
                    print(f"  Received:  {receive_time.isoformat()}")
                    print(f"  Delay:     {delay_ms:.2f} ms")
                    print(f"  Saved:     {output_path}\n")
                    
        except zmq.error.ContextTerminated:
            break
        except Exception as e:
            if not stop_event.is_set():
                print(f"[SUB:{NODE_ID}] Error: {e}")
            connected_peers.clear()  # Reconnect on error
    
    sub_socket.close()


def discovery_loop(stop_event, peers_info):
    """Discover and announce this node to peers"""
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

    print(f"Starting Image Subscriber: {NODE_ID}")
    print(f"Local IP: {get_local_ip()}\n")

    # Start subscriber thread
    sub_thread = threading.Thread(
        target=subscriber_loop, args=(context, peers_info, stop_event), daemon=True
    )
    sub_thread.start()

    # Start discovery thread
    discovery_thread = threading.Thread(
        target=discovery_loop, args=(stop_event, peers_info), daemon=True
    )
    discovery_thread.start()

    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n[INFO] Shutting down...")
    finally:
        stop_event.set()
        context.term()


if __name__ == "__main__":
    main()
