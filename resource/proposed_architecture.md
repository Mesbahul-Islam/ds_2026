## Hardware Overview
- **SIYI A8 Mini IP Camera:** Compact IP camera supporting RTSP/ONVIF for video streaming/control.
- **Raspberry Pi (x3):** Affordable single-board computers running Linux-based OS for distributed tasks.
- **Router/Switch:** Networking devices connecting Pis and IP camera to LAN/internet.

## Software Overview
- **Raspbian OS:** Official OS for Raspberry Pi (Debian-based).
- **OpenCV:** Real-time image processing/computer vision library.
- **Motion:** Software motion detector for video streams.
- **YOLO:** Real-time object detection system.
- **ZeroMQ:**  High-performance messaging library for distributed communication.
- **Flask/Django:** Python web frameworks for APIs/web apps.
- **Node-RED:** Visual programming tool for IoT.
- **Docker:** Container platform for portable deployments.

## Distributed Tasks Overview
- **Task 1: Frame Grabbing & Motion Detection**
	- **Input:** Live video stream from RTSP camera
	- **Task:** Continuously grab frames and perform motion detection (OpenCV/Motion)
	- **Output:** Detected frames, timestamps, flags

- **Task 2: Object Detection**
	- **Input:** Detected frames from motion detection
	- **Task:** Run YOLO object detection model on detected frames
	- **Output:** Object classes, bounding boxes, confidence scores, flags

- **Task 3: Alarming & Notifications**
	- **Input:** Detected object classes/events from object detection
	- **Task:** Send alarms to users (email, SMS, push notifications)
	- **Output:** Alarm notifications, logs, flags

- **Task 4: Recording & Storing**
	- **Input:** Motion Events from Task 1
	- **Task:** Record video clips, store images/metadata locally and on networked storage
	- **Output:** Video files, (opt.  images, metadata logs)



### Additional Possible Tasks
- **Edge Analytics:** Count objects, generate heatmaps, etc.
- **Local Storage Management:** Manage storage, delete old files as needed.
- **Network Health Monitoring:** Monitor connectivity and performance.
<!-- - **Real-Time Streaming Relay:** Relay video streams to central server/cloud. -->
- **System Self-Diagnostics:** Monitor health/performance of Raspberry Pis.
- **Remote Firmware/Software Updates:** Enable remote updates for Pis.


## Communication Layer Overview
- **Protocols:** ZeroMQ, HTTPS, WebSockets for secure data transmission.
- **Event Transmission:** Only motion/object-triggered events (video clips, images, metadata, alarms) sent to central server/cloud.
- **Task Coordination:** Lightweight messaging for distributed task management and status updates.


