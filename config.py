# Simple configuration for testing ZeroMQ communication

# Gateway IP address - change this to your gateway Raspberry Pi's IP
GATEWAY_IP = "192.168.1.100"  # Update this!

# Ports for communication
TASK_PORT = 5555    # Gateway sends tasks here
RESULT_PORT = 5556  # Gateway receives results here

# Edge device IDs
EDGE_DEVICES = ["edge_1", "edge_2", "edge_3"]
