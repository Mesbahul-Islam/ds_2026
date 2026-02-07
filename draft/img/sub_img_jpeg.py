"""
Image Subscriber - Receive and save images from ZeroMQ PUB
"""
import base64
import json
import os
import sys
import socket
import threading
import time
from datetime import datetime

import zmq

# Add parent directory to path to import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config import (
    DISCOVERY_BROADCAST,
    DISCOVERY_PORT,
)


def get_local_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"


NODE_ID = f"{socket.gethostname()}"
MOTION_PORT = 5555


def save_jpeg_bytes(jpeg_bytes, output_path):
    """Save raw JPEG bytes to a file"""
    with open(output_path, "wb") as img_file:
        img_file.write(jpeg_bytes)


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
                    time.sleep(0.2)
            
            if sub_socket.poll(1000):
                message = sub_socket.recv_json()
                receive_time = datetime.now()

                if message.get("type") == "image":
                    image_b64 = message.get("image_data")
                    sender = message.get("node_id", "unknown")
                    publish_ts_str = message.get("publish_ts")
                    
                    if image_b64:
                        jpeg_bytes = base64.b64decode(image_b64)
                        filename = f"{sender}_motion_{receive_time.strftime('%Y%m%d_%H%M%S_%f')}.jpg"
                        output_path = os.path.join(output_dir, filename)
                        save_jpeg_bytes(jpeg_bytes, output_path)
                        image_count += 1

                        # Calculate latency if publish timestamp is available
                        latency_info = ""
                        if publish_ts_str:
                            try:
                                publish_time = datetime.fromisoformat(publish_ts_str)
                                latency = (receive_time - publish_time).total_seconds() * 1000  # in milliseconds
                                latency_info = f"  Latency:  {latency:.2f} ms"
                            except (ValueError, TypeError):
                                latency_info = "  Latency:  N/A"

                        print(f"\n✓ Motion image #{image_count}")
                        print(f"  From:     {sender}")
                        print(f"  Received: {receive_time.isoformat()}")
                        print(f"  Saved:    {output_path}")
                        if latency_info:
                            print(latency_info)
                        print()
                elif message.get("type") == "motion_flag":
                    flag = message.get("flag")
                    if flag == 1:
                        print(f"[SUB:{NODE_ID}] Motion started at {receive_time.isoformat()}")
                    elif flag == 0:
                        print(f"[SUB:{NODE_ID}] Motion ended at {receive_time.isoformat()}")
                    
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
