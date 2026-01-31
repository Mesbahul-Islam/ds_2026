"""
Minimal Peer Node - Auto-discovery + status updates
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


def server_loop(context):
    socket = context.socket(zmq.REP)
    socket.bind(f"tcp://*:{NODE_PORT}")

    while True:
        try:
            socket.recv_json()
            socket.send_json({"ok": True})
        except Exception:
            continue

    socket.close()


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
            print(f"[Discovery:{NODE_ID}] Broadcasted discovery message")

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
                        print(f"[Discovery:{NODE_ID}] Sent announce message to {addr[0]}:{DISCOVERY_PORT}")
        except Exception:
            pass
        
        time.sleep(2)

    sock.close()


def main():
    context = zmq.Context()

    peers_info = {}
    stop_event = threading.Event()

    # Start server thread to receive messages
    server_thread = threading.Thread(target=server_loop, args=(context,), daemon=True)
    server_thread.start()

    # Start discovery thread
    discovery_thread = threading.Thread(
        target=discovery_loop, args=(stop_event, peers_info), daemon=True
    )
    discovery_thread.start()

    peer_sockets = {}

    try:
        time.sleep(2)

        while True:
            for peer_id, info in peers_info.items():
                if peer_id not in peer_sockets:
                    sock = context.socket(zmq.REQ)
                    sock.setsockopt(zmq.RCVTIMEO, 1000)
                    sock.setsockopt(zmq.SNDTIMEO, 1000)
                    sock.setsockopt(zmq.LINGER, 0)
                    sock.connect(f"tcp://{info['ip']}:{info['port']}")
                    peer_sockets[peer_id] = sock
                    print(
                        f"[Client:{NODE_ID}] Connected to {peer_id} at {info['ip']}:{info['port']}"
                    )

            status = {
                "node_id": NODE_ID,
                "ip": get_local_ip(),
                "status": "online",
                "ts": datetime.now().isoformat(),
            }

            for sock in peer_sockets.values():
                try:
                    sock.send_json({"status": status})
                    sock.recv_json()
                except Exception:
                    pass

            time.sleep(2)

    except Exception:
        pass
    finally:
        stop_event.set()
        for sock in peer_sockets.values():
            sock.close()
        context.term()


if __name__ == "__main__":
    main()
