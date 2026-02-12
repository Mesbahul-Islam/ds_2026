# Motion Detection System

## Overview

The motion detection system is a core component of the distributed surveillance network. It processes video streams from RTSP sources, detects motion using frame differencing, and publishes motion events and images via ZeroMQ for other nodes to consume.

## Architecture

### Components
- **MotionDetector Class**: Main class handling video processing, motion detection, and publishing
- **ZeroMQ Publishers**: Separate sockets for motion flags and images
- **UDP Discovery**: Peer discovery for distributed communication
- **FFmpeg Integration**: Video stream processing
- **OpenCV Processing**: Image manipulation and motion analysis

### Ports
- **Motion Flag Port**: `5556` - Publishes motion start/end flags
- **Motion Image Port**: `5557` - Publishes JPEG images when motion is detected
- **Discovery Port**: `50000` - UDP broadcast for peer discovery

## Configuration

All motion detection parameters are centralized in `config.py`:

```python
# Motion detection ports
MOTION_FLAG_PORT = 5556
MOTION_IMAGE_PORT = 5557

# Motion detection settings
MOTION_URL = 'rtsp://127.0.0.1:8554/stream'
MOTION_THRESHOLD = 0.33
PIXEL_DIFF_THRESHOLD = 50
BLUR_SIGMA = 1.5
KERNEL_SIZE = 5
```

## Motion Detection Algorithm

### Process Flow
1. **Video Input**: Reads frames from RTSP stream at 10 FPS
2. **Preprocessing**: Converts to grayscale and applies Gaussian blur
3. **Motion Detection**: Frame differencing with threshold filtering
4. **Event Publishing**: Sends flags and images based on motion state changes

### Algorithm Details
- **Gaussian Blur**: Reduces noise with kernel size 5 and sigma 1.5
- **Frame Differencing**: Compares current blurred frame with previous
- **Thresholding**: Pixel differences > 50 are considered motion
- **Ratio Calculation**: Percentage of pixels showing motion
- **Motion Trigger**: Ratio > 0.33 triggers motion detection

## Message Formats

### Motion Flag Message
```json
{
  "type": "motion_flag",
  "node_id": "hostname-motion",
  "flag": 1,  // 1=start, 0=end
  "timestamp": "15:11:11.186105"
}
```

### Motion Image Message
```json
{
  "type": "motion_image",
  "node_id": "hostname-motion",
  "image_data": "base64_encoded_jpeg",
  "timestamp": "15:11:11.186105"
}
```

## Usage

### Running the Motion Detector
```bash
cd /path/to/project
python motion.py
```

### Output
```
[FLAG_PUB:hostname-motion] Listening on tcp://*:5556
[IMAGE_PUB:hostname-motion] Listening on tcp://*:5557
[PUB:hostname-motion] Local IP: 192.168.1.100
Starting motion detection... Press Ctrl+C to stop.
Motion ratio: 0.2543 - No motion
Motion ratio: 0.3879 - MOTION DETECTED
hostname-motion triggered motion event at 15:11:11.186105 and published image (80.35 KB)
Motion ratio: 0.2489 - No motion
Motion ended: sent flag 0
```

## Recent Updates

### Version History
- **v1.0**: Initial implementation with basic motion detection
- **v1.1**: Added separate ports for flags and images
- **v1.2**: Modularized code into MotionDetector class
- **v1.3**: Centralized configuration in config.py
- **v1.4**: Fixed flag logic bug (prevented repeated end flags during motion)

### Bug Fixes
- **Flag Logic Issue**: Previously sent "motion ended" flag on every frame after motion start. Fixed to send only when motion actually stops.

## Dependencies

- `ffmpeg-python`: Video stream processing
- `opencv-python`: Image processing
- `pyzmq`: ZeroMQ messaging
- `numpy`: Array operations

## Integration

The motion detector integrates with:
- **YOLO Detection**: Subscribes to motion images for object detection
- **Monitoring**: Publishes events for system monitoring
- **Peer Discovery**: Announces presence via UDP broadcast

