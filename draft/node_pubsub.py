"""
Minimal Peer Node - Auto-discovery + PUB/SUB status updates
"""
import json
import socket
import threading
import time
import uuid
from datetime import datetime

import zmq

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


NODE_ID = f"{socket.gethostname()}-{uuid.uuid4().hex[:6]}"


def subscriber_loop(context, peers_info):
    sub_socket = context.socket(zmq.SUB)
    sub_socket.setsockopt_string(zmq.SUBSCRIBE, "")
    
    connected_peers = set()
    
    while True:
        try:
            for peer_id, info in peers_info.items():
                if peer_id not in connected_peers:
                    sub_socket.connect(f"tcp://{info['ip']}:{info['port']}")
                    connected_peers.add(peer_id)
                    print(f"[SUB:{NODE_ID}] Subscribed to {peer_id} at {info['ip']}:{info['port']}")
            
            if sub_socket.poll(1000):
                message = sub_socket.recv_json()
                print(f"[SUB:{NODE_ID}] Received: {message}")
        except Exception:
            pass


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

    # PUB socket - publish status updates
    pub_socket = context.socket(zmq.PUB)
    pub_socket.bind(f"tcp://*:{NODE_PORT}")

    # Start subscriber thread
    sub_thread = threading.Thread(
        target=subscriber_loop, args=(context, peers_info), daemon=True
    )
    sub_thread.start()

    # Start discovery thread
    discovery_thread = threading.Thread(
        target=discovery_loop, args=(stop_event, peers_info), daemon=True
    )
    discovery_thread.start()

    try:
        time.sleep(2)

        while True:
            status = {
                "node_id": NODE_ID,
                "ip": get_local_ip(),
                "status": "online",
                "ts": datetime.now().isoformat(),
            }

            pub_socket.send_json(status)
            print(f"[PUB:{NODE_ID}] Published: {status}")

            time.sleep(2)

    except Exception:
        pass
    finally:
        stop_event.set()
        pub_socket.close()
        context.term()


if __name__ == "__main__":
    main()
