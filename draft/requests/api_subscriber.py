import requests
import json
import socket
import threading
import time
import logging
from datetime import datetime
import zmq
import sys

sys.path.append('../..')
from config import (
    DISCOVERY_BROADCAST,
    DISCOVERY_PORT,
    NODE_PORT,
)

# Configure logging
logging.basicConfig(
    filename='api_subscriber.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
# Add console handler
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

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

def send_to_api(message, api_url):
    """Send the message to the local REST API."""
    try:
        response = requests.post(api_url, json=message)
        if response.status_code == 200:
            logging.info(f"Successfully sent message to API: {message.get('type')}")
        else:
            logging.error(f"Failed to send message to API: {response.status_code} - {response.text}")
    except Exception as e:
        logging.error(f"Error sending to API: {e}")

def subscriber_loop(context, peers_info, stop_event, api_url):
    sub_socket = context.socket(zmq.SUB)
    sub_socket.setsockopt_string(zmq.SUBSCRIBE, "")

    connected_peers = set()
    message_count = 0
    current_event = None

    while not stop_event.is_set():
        try:
            for peer_id, info in peers_info.items():
                if peer_id not in connected_peers:
                    sub_socket.connect(f"tcp://{info['ip']}:{info['port']}")
                    connected_peers.add(peer_id)
                    print(f"[SUB] Connected to {peer_id} at {info['ip']}:{info['port']}")
                    time.sleep(0.2)

            if sub_socket.poll(1000):
                recv_ts = datetime.now().isoformat()
                message = sub_socket.recv_json()
                message_count += 1
                sender = message.get("node_id", "unknown")
                print(f"[SUB] Received message #{message_count} from {sender}: {message.get('type')}")

                # Add receive timestamp
                message["recv_ts"] = recv_ts

                if message.get('type') == 'motion_flag':
                    if message.get('flag') == 1:
                        current_event = message
                    # Ignore flag == 0
                elif message.get('type') == 'image' and current_event:
                    # Combine and send
                    combined = {
                        'event': {
                            'motion_flag': current_event,
                            'image': message,
                            'metadata': {
                                'node_id': sender,
                                'event_ts': current_event.get('ts'),
                                'image_ts': message.get('ts')
                            }
                        }
                    }
                    send_to_api(combined, api_url)
                    current_event = None

        except zmq.error.ContextTerminated:
            break
        except Exception as e:
            if not stop_event.is_set():
                print(f"[SUB] Error: {e}")
            connected_peers.clear()

    sub_socket.close()

if __name__ == "__main__":
    api_url = "http://localhost:8000/api/data"  # Adjust the URL as needed for your local server
    node_id = f"{socket.gethostname()}-api-sub"

    context = zmq.Context()
    peers_info = {}
    stop_event = threading.Event()

    sub_thread = threading.Thread(
        target=subscriber_loop,
        args=(context, peers_info, stop_event, api_url),
        daemon=True,
    )
    sub_thread.start()

    discovery_thread = threading.Thread(
        target=discovery_loop,
        args=(stop_event, peers_info, node_id, NODE_PORT),
        daemon=True,
    )
    discovery_thread.start()

    print(f"[SUB:{node_id}] Subscribing to messages on port {NODE_PORT}")
    print(f"[SUB:{node_id}] Local IP: {get_local_ip()}")
    print(f"[SUB:{node_id}] Sending data to {api_url}\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[INFO] Shutting down...")
    finally:
        stop_event.set()
        context.term()

