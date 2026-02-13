import zmq
import json
import logging
import sys
from datetime import datetime

# Add parent directory to path to import config
sys.path.append('.')

from config import SYSTEM_MONITOR_PORT

# Configure logging
logging.basicConfig(
    filename='server.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
# Add console handler
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(message)s')
logging.getLogger('').addHandler(console)

def main():
    # Create ZeroMQ context and SUB socket
    context = zmq.Context()
    socket = context.socket(zmq.SUB)

    # Connect to the system monitor publisher
    socket.connect(f"tcp://localhost:{SYSTEM_MONITOR_PORT}")

    # Subscribe to all messages (empty string means subscribe to everything)
    socket.setsockopt_string(zmq.SUBSCRIBE, "")

    logging.info(f"Server listening for system monitor packets on tcp://localhost:{SYSTEM_MONITOR_PORT}")

    try:
        while True:
            # Receive message
            message = socket.recv_json()

            # Log the received packet
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logging.info(f"[{timestamp}] Received system status: {json.dumps(message, indent=2)}")

            # Print to console for immediate feedback
            print(f"[{timestamp}] Received system status from {message.get('node_id', 'unknown')}:")
            print(f"  CPU: {message.get('cpu', 'N/A')}%")
            print(f"  Memory: {message.get('memory_used_gb', 0):.2f}/{message.get('memory_total_gb', 0):.2f} GB ({message.get('memory_percent', 0)}%)")
            print(f"  Disk I/O: R {message.get('disk_read_kbs', 0):.2f} KB/s, W {message.get('disk_write_kbs', 0):.2f} KB/s")
            print(f"  Network I/O: U {message.get('network_send_kbs', 0):.2f} KB/s, D {message.get('network_recv_kbs', 0):.2f} KB/s")
            print(f"  Temperature: {message.get('temperature', 'N/A')}")
            print(f"  GPU: {message.get('gpu', 'N/A')}")
            print("-" * 50)

    except KeyboardInterrupt:
        logging.info("Server stopped by user")
    except Exception as e:
        logging.error(f"Error in server: {e}")
    finally:
        socket.close()
        context.term()

if __name__ == "__main__":
    main()
