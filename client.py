"""
Simple Client - Run this on your laptop
"""
import zmq
import time
from datetime import datetime
from config import GATEWAY_IP

def main():
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    
    # Connect to Raspberry Pi
    raspberry_pi_ip = GATEWAY_IP  # Use the IP from config.py
    socket.connect(f"tcp://{raspberry_pi_ip}:5555")
    
    print(f"[Client] Connected to Raspberry Pi at {raspberry_pi_ip}:5555")
    print("[Client] Starting communication test...\\n")
    print("-" * 50)
    
    try:
        # Send 5 test messages
        for i in range(5):
            message = {
                "from": "Laptop",
                "data": f"Hello Raspberry Pi! Message #{i + 1}",
                "timestamp": datetime.now().isoformat()
            }
            
            print(f"\n[Client] Sending message {i + 1}...")
            socket.send_json(message)
            
            # Wait for response
            response = socket.recv_json()
            print(f"[Client] Received response:")
            print(f"  From: {response.get('from')}")
            print(f"  Data: {response.get('data')}")
            print(f"  Status: {response.get('status')}")
            print("-" * 50)
            
            time.sleep(1)
        
        print("\n" + "=" * 50)
        print("[Client] ✓ Communication test successful!")
        print("=" * 50)
        
    except KeyboardInterrupt:
        print("\n[Client] Stopping...")
    except Exception as e:
        print(f"\n[Client] Error: {e}")
        print("Make sure the Raspberry Pi server is running and the IP address is correct!")
    finally:
        socket.close()
        context.term()

if __name__ == "__main__":
    main()
