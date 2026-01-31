"""
Simple Server - Run this on the Raspberry Pi
"""
import zmq
import time
from datetime import datetime

def main():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:5555")
    
    print("[Server] Raspberry Pi server started on port 5555")
    print("[Server] Waiting for messages from laptop...\n")
    print("-" * 50)
    
    try:
        while True:
            # Wait for request from client
            message = socket.recv_json()
            print(f"\n[Server] Received message:")
            print(f"  From: {message.get('from')}")
            print(f"  Data: {message.get('data')}")
            print(f"  Timestamp: {message.get('timestamp')}")
            
            # Prepare response
            response = {
                "from": "Raspberry Pi",
                "data": f"Echo: {message.get('data')}",
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            }
            
            # Small delay to simulate processing
            time.sleep(0.5)
            
            # Send reply
            socket.send_json(response)
            print(f"[Server] Sent response back")
            print("-" * 50)
            
    except KeyboardInterrupt:
        print("\n[Server] Shutting down...")
    finally:
        socket.close()
        context.term()

if __name__ == "__main__":
    main()