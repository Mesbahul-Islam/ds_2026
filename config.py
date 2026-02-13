# Simple configuration for peer discovery

# All nodes listen on this ZeroMQ port
NODE_PORT = 5555

# UDP discovery settings (same subnet)
DISCOVERY_PORT = 50000
DISCOVERY_BROADCAST = "255.255.255.255"
DISCOVERY_INTERVAL = 2  # seconds between broadcast pings

# System monitor update interval (seconds)
SYSTEM_MONITOR_INTERVAL = 1

# System monitor port
SYSTEM_MONITOR_PORT = 5559
    
# Motion detection ports
MOTION_FLAG_PORT = 5556
MOTION_IMAGE_PORT = 5557

# Detection results port
DETECTION_PORT = 5558

# Motion detection settings
MOTION_URL = 'rtsp://127.0.0.1:8554/stream'
MOTION_THRESHOLD = 0.33
PIXEL_DIFF_THRESHOLD = 50
BLUR_SIGMA = 1.5
KERNEL_SIZE = 5
MOTION_FPS = 10

# YOLO model path
MODEL_PATH = "yolo26n_ncnn_model"

# Recording settings
RECORD_DURATION = 15
RECORD_FPS = 10
