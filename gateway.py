"""
Simple Gateway - Test ZeroMQ communication with 3 edge devices
"""
import zmq
import time
from datetime import datetime
from config import TASK_PORT, RESULT_PORT

def main():
    context = zmq.Context()
    
    # PUSH socket - send tasks to edge devices
    sender = context.socket(zmq.PUSH)
    sender.bind(f"tcp://*:{TASK_PORT}")
    print(f"[Gateway] Sending tasks on port {TASK_PORT}")
    
    # PULL socket - receive results from edge devices
    receiver = context.socket(zmq.PULL)
    receiver.bind(f"tcp://*:{RESULT_PORT}")
    print(f"[Gateway] Receiving results on port {RESULT_PORT}")
    
    # Give sockets time to establish
    time.sleep(1)
    
    print("\n[Gateway] Starting communication test...")
    print("-" * 50)
    
    try:
        # Send 3 test messages (one for each device)
        for i in range(3):
            message = {
                "message_id": i + 1,
                "timestamp": datetime.now().isoformat(),
                "data": f"Test message {i + 1} from Gateway"
            }
            sender.send_json(message)
            print(f"[Gateway] Sent: Message {i + 1}")
            time.sleep(0.5)
        
        print("\n[Gateway] Waiting for responses from edge devices...")
        print("-" * 50)
        
        # Receive 3 responses
        for i in range(3):
            response = receiver.recv_json()
            print(f"\n[Gateway] Received response {i + 1}:")
            print(f"  From: {response.get('device_id')}")
            print(f"  Message ID: {response.get('message_id')}")
            print(f"  Data: {response.get('data')}")
            print(f"  Timestamp: {response.get('timestamp')}")
        
        print("\n" + "=" * 50)
        print("[Gateway] ✓ Communication test successful!")
        print("=" * 50)
        
    except KeyboardInterrupt:
        print("\n[Gateway] Shutting down...")
    finally:
        sender.close()
        receiver.close()
        context.term()

if __name__ == "__main__":
    main()
