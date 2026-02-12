# Detection Processor

The Detection Processor is a component of the distributed surveillance system that performs real-time object detection on motion-triggered images using YOLO (You Only Look Once) models.

## Overview

The `DetectionProcessor` class extends `BaseNode` and implements a ZeroMQ-based pub-sub architecture to:

1. Subscribe to motion-detected images from the motion detection system
2. Run YOLO inference on received images
3. Publish detection results containing identified objects and confidence scores
4. Optionally save annotated result images to disk

## Dependencies

- `ultralytics` - YOLO model implementation
- `opencv-python` (cv2) - Image processing
- `pyzmq` - ZeroMQ messaging
- `numpy` - Numerical operations
- `base64` - Image encoding/decoding

## Configuration

The detection processor uses the following configuration parameters from `config.py`:

- `MOTION_IMAGE_PORT` - Port to subscribe to motion images
- `DETECTION_PORT` - Port to publish detection results
- `MODEL_PATH` - Path to the YOLO model file

## Architecture

### Class Structure

```python
class DetectionProcessor(BaseNode):
    def __init__(self, model_path)
    def load_model(self)
    def run_inference(self, image)
    def save_image(self, results, sender, timestamp)
    def publish_detection_results(self, detections, timestamp, sender)
    def subscriber_loop(self)
    def run(self)
```

### ZeroMQ Sockets

- **Subscriber Socket**: Connects to motion image publisher on `tcp://127.0.0.1:{MOTION_IMAGE_PORT}`
- **Publisher Socket**: Binds to `tcp://*:{DETECTION_PORT}` for publishing detection results

### Message Format

#### Input (from Motion Processor)
```json
{
    "type": "image",
    "node_id": "motion_node_id",
    "image_data": "base64_encoded_jpeg",
    "ts": "timestamp"
}
```

#### Output (Detection Results)
```json
{
    "type": "detection_results",
    "node_id": "detection_node_id",
    "sender": "motion_node_id",
    "detections": [
        {
            "class": "person",
            "confidence": 0.85
        }
    ],
    "ts": "detection_timestamp"
}
```

## Usage

### Running the Detection Processor

```bash
python detection.py
```

The processor will:
1. Load the YOLO model from `MODEL_PATH`
2. Connect to the motion image publisher
3. Start listening for incoming images
4. Process each image and publish results
5. Continue running until interrupted with Ctrl+C

### Model Requirements

- Supports YOLO models in various formats (.pt, .onnx, etc.)
- Currently configured for NCNN optimized models
- Model should be placed at the path specified in `MODEL_PATH`

## Processing Flow

1. **Image Reception**: Receives base64-encoded JPEG images via ZeroMQ SUB socket
2. **Decoding**: Converts base64 string to OpenCV image frame
3. **Inference**: Runs YOLO model inference on the image
4. **Result Extraction**: Parses detection results into structured format
5. **Publishing**: Sends detection results via ZeroMQ PUB socket
6. **Optional Saving**: Can save annotated images (currently disabled)

## Logging and Monitoring

The processor logs:
- Connection establishment
- Image processing counts
- Detection results
- Timestamps for send/receive/detection operations
- Error conditions

## Performance Considerations

- Processes images sequentially as received
- No batching implemented
- Image saving is optional and disabled by default
- Uses threading for subscriber loop to avoid blocking

## Error Handling

- Continues processing on individual image decode failures
- Logs exceptions but doesn't terminate on errors
- Graceful shutdown on KeyboardInterrupt

## Integration

The detection processor integrates with:
- **Motion Processor**: Receives images when motion is detected
- **Monitoring System**: Publishes results for further processing or alerting
- **Storage System**: Can save annotated images for review

## Configuration Options

### Model Path
```python
model_path = MODEL_PATH  # From config.py
```

### Ports
- Motion images: `MOTION_IMAGE_PORT`
- Detection results: `DETECTION_PORT`

### Image Saving
Uncomment the `save_image` call in `subscriber_loop()` to enable:
```python
self.save_image(results, sender, detection_ts)
```

Images are saved to `detection_images/` directory with format: `{sender}_{timestamp}.jpg`