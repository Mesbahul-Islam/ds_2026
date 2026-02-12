import socket
import threading
import time
import json
import logging
import zmq
import sys
from datetime import datetime

# Add parent directory to path to import config
sys.path.append('.')

from config import (
    DISCOVERY_BROADCAST,
    DISCOVERY_PORT,
)

# Configure logging
logging.basicConfig(
    filename='log.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
# Add console handler
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(message)s')
logging.getLogger('').addHandler(console)

class BaseNode:
    def __init__(self, node_suffix):
        self.node_id = f"{socket.gethostname()}-{node_suffix}"
        self.context = zmq.Context()
        self.peers_info = {}
        self.stop_event = threading.Event()

    def get_local_ip(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except OSError:
            return "127.0.0.1"

    def discovery_loop(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        try:
            sock.bind(("", DISCOVERY_PORT))
        except OSError as e:
            logging.warning(f"Discovery port {DISCOVERY_PORT} already in use: {e}. Skipping discovery.")
            sock.close()
            return
        sock.settimeout(1.0)

        while not self.stop_event.is_set():
            try:
                sock.sendto(
                    json.dumps(
                        {
                            "type": "discover",
                            "node_id": self.node_id,
                            "ip": self.get_local_ip(),
                            "port": getattr(self, 'pub_port', 0),  # Subclass should set this
                        }
                    ).encode("utf-8"),
                    (DISCOVERY_BROADCAST, DISCOVERY_PORT),
                )

                data, addr = sock.recvfrom(4096)
                message = json.loads(data.decode("utf-8"))

                if message.get("node_id") != self.node_id and message.get("type") in {"discover", "announce"}:
                    peer_id = message.get("node_id")
                    if peer_id:
                        self.peers_info[peer_id] = {
                            "ip": message.get("ip") or addr[0],
                            "port": message.get("port", 0),
                        }

                        if message.get("type") == "discover":
                            sock.sendto(
                                json.dumps({
                                    "type": "announce",
                                    "node_id": self.node_id,
                                    "ip": self.get_local_ip(),
                                    "port": getattr(self, 'pub_port', 0),
                                }).encode("utf-8"), (addr[0], DISCOVERY_PORT)
                            )
            except Exception:
                pass

            if self.peers_info:
                print(f"[Discovery:{self.node_id}] Known peers: {list(self.peers_info.keys())}")
            time.sleep(15 if self.peers_info else 2)

        sock.close()

    def start_discovery(self):
        discovery_thread = threading.Thread(target=self.discovery_loop, daemon=True)
        discovery_thread.start()

    def cleanup(self):
        self.stop_event.set()
        self.context.term()