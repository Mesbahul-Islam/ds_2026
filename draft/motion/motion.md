
# Motion Detection on RTSP Streams (motion.md)

This document provides a **detailed, practical explanation** of:

1. Motion detection **algorithms / techniques**
2. Motion detection **libraries / frameworks**
3. Step-by-step **processing pipelines**
4. Performance trade-offs for **embedded systems (Raspberry Pi / UAV cameras)**

This guide is optimized for **CPU-light, real-time edge systems** like SIYI camera + Raspberry Pi.

---

## 📌 PART 1 — MOTION DETECTION TECHNIQUES

---

## 1. Frame Differencing

### 📖 Description
Frame differencing detects motion by subtracting the current video frame from the previous frame and thresholding the pixel differences. Any significant change indicates motion.

This is the **simplest and fastest** motion detection method and is ideal for:
- Embedded devices
- Raspberry Pi
- Low-latency pipelines
- Static or slowly moving cameras

---

### 🧠 Algorithm Steps

1. Capture frame N
2. Convert to grayscale
3. Blur to reduce noise
4. Subtract from frame N-1
5. Apply threshold
6. Count changed pixels
7. Trigger motion if ratio exceeds threshold

---

### 🔁 Processing Flow

```
RTSP Stream
     ↓
Frame Capture
     ↓
Grayscale Conversion
     ↓
Noise Reduction (Blur)
     ↓
Absolute Frame Difference
     ↓
Thresholding
     ↓
Pixel Count / Area Check
     ↓
Motion Detected
```

---

### ⚡ Pros / Cons

| Pros | Cons |
|------|------|
| Extremely fast | Sensitive to lighting changes |
| Very low CPU | Poor with moving cameras |
| Easy to implement | No object separation |

---

### 🎯 Best Use Cases
- Embedded surveillance
- Motion-triggered recording
- UAV ground station feeds
- Smart doorbells

---

## 2. Background Subtraction

### 📖 Description
Background subtraction builds a statistical model of the scene over time and identifies deviations as foreground motion. Common algorithms include **MOG2** and **KNN**.

Unlike frame differencing, this method adapts to gradual changes and detects stationary objects after motion.

---

### 🧠 Algorithm Steps

1. Initialize background model
2. Read frame
3. Update background statistics
4. Subtract background
5. Threshold foreground mask
6. Morphological cleanup
7. Motion detection

---

### 🔁 Processing Flow

```
RTSP Stream
     ↓
Frame Capture
     ↓
Background Model Update
     ↓
Foreground Extraction
     ↓
Thresholding
     ↓
Morphology
     ↓
Motion Detected
```

---

### ⚡ Pros / Cons

| Pros | Cons |
|------|------|
| Handles slow motion | Higher CPU usage |
| Robust to noise | Breaks with camera motion |
| Detects stopped objects | Requires warm-up time |

---

### 🎯 Best Use Cases
- Indoor surveillance
- Static outdoor cameras
- Traffic cameras

---

## 3. Optical Flow

### 📖 Description
Optical flow computes pixel motion vectors between frames, allowing detection of motion direction and magnitude. Common methods include **Lucas-Kanade** and **Farneback**.

It works even when the camera itself moves, making it suitable for robotics and UAVs.

---

### 🧠 Algorithm Steps

1. Capture frame N and N-1
2. Extract feature points or dense pixel grid
3. Track movement vectors
4. Filter by magnitude
5. Aggregate motion vectors
6. Trigger motion

---

### 🔁 Processing Flow

```
RTSP Stream
     ↓
Frame Capture
     ↓
Feature Extraction / Dense Grid
     ↓
Motion Vector Computation
     ↓
Vector Magnitude Thresholding
     ↓
Motion Detected
```

---

### ⚡ Pros / Cons

| Pros | Cons |
|------|------|
| Works with moving camera | Very CPU intensive |
| Direction-aware motion | Hard to tune |
| Useful for navigation | Complex implementation |

---

### 🎯 Best Use Cases
- UAV navigation
- Robotics
- Autonomous vehicles
- SLAM systems

---

## 4. Deep Learning Temporal Models

### 📖 Description
Neural networks analyze sequences of frames to learn motion patterns, often combining object detection with temporal embeddings. Examples include 3D CNNs, LSTMs, and transformer-based video models.

---

### 🧠 Algorithm Steps

1. Decode video frames
2. Preprocess frames
3. Feed frame sequence to neural network
4. Predict motion probability or region
5. Post-process output

---

### 🔁 Processing Flow

```
RTSP Stream
     ↓
Frame Capture
     ↓
Neural Network Inference
     ↓
Temporal Feature Modeling
     ↓
Motion Prediction
```

---

### ⚡ Pros / Cons

| Pros | Cons |
|------|------|
| Highly robust | Requires GPU/NPU |
| Works in complex scenes | High latency |
| Learns semantics | Training required |

---

### 🎯 Best Use Cases
- Smart cameras
- Autonomous vehicles
- Advanced surveillance analytics

---

## 📌 PART 2 — MOTION DETECTION LIBRARIES / FRAMEWORKS

---

## 1. OpenCV

### 📖 Description
OpenCV is the most widely used computer vision library. It provides built-in implementations for:
- Frame differencing
- Background subtraction (MOG2, KNN)
- Optical flow
- Morphology and contour extraction

It supports C++, Python, CUDA, and runs on almost all platforms.

---

### 🔁 Typical OpenCV Motion Pipeline

```
RTSP Stream
     ↓
cv::VideoCapture
     ↓
Grayscale + Blur
     ↓
Frame Difference / Background Subtraction
     ↓
Threshold
     ↓
Morphology
     ↓
Contours
     ↓
Motion Detection
```

---

### ⚡ Pros / Cons

| Pros | Cons |
|------|------|
| Huge ecosystem | RTSP decoding can be unstable |
| Easy prototyping | Higher CPU overhead |
| Many algorithms | Heavy dependency footprint |

---

### 🎯 Best Use Cases
- Research
- Rapid prototyping
- Desktop systems

---

## 2. GStreamer

### 📖 Description
GStreamer is a multimedia pipeline framework optimized for real-time streaming and decoding. It excels at RTSP handling and can integrate with Python, C, or CUDA.

It does not provide motion detection itself but efficiently feeds frames to your algorithms.

---

### 🔁 Typical GStreamer Motion Pipeline

```
RTSP Stream
     ↓
GStreamer Decoder
     ↓
Frame Buffer
     ↓
Grayscale Conversion
     ↓
Frame Difference / Thresholding
     ↓
Motion Detection
```

---

### ⚡ Pros / Cons

| Pros | Cons |
|------|------|
| Extremely stable RTSP | More complex API |
| Low latency | No built-in vision algorithms |
| Hardware decode support | Steep learning curve |

---

### 🎯 Best Use Cases
- Embedded systems
- Production RTSP pipelines
- Jetson / Raspberry Pi

---

## 3. FFmpeg

### 📖 Description
FFmpeg is a lightweight, extremely fast multimedia decoding framework. It can pipe raw video frames directly to Python, C, or other programs.

Like GStreamer, it does not implement motion detection but is excellent for RTSP ingestion.

---

### 🔁 Typical FFmpeg Motion Pipeline

```
RTSP Stream
     ↓
FFmpeg Decoder
     ↓
Raw Frame Pipe
     ↓
Frame Difference
     ↓
Thresholding
     ↓
Motion Detection
```

---

### ⚡ Pros / Cons

| Pros | Cons |
|------|------|
| Very low CPU usage | No native vision functions |
| Simple CLI integration | No built-in visualization |
| Excellent RTSP stability | Manual buffer handling |

---

### 🎯 Best Use Cases
- Raspberry Pi motion detection
- Embedded surveillance
- Lightweight pipelines

---

## 4. NVIDIA VPI

### 📖 Description
NVIDIA Vision Programming Interface (VPI) is a GPU/PVA-accelerated vision library optimized for Jetson devices. It provides hardware-accelerated:
- Optical flow
- Background subtraction
- Image filtering

---

### 🔁 Typical VPI Motion Pipeline

```
RTSP Stream
     ↓
Hardware Decoder
     ↓
CUDA/PVA Vision Operators
     ↓
Optical Flow / Background Subtraction
     ↓
Motion Detection
```

---

### ⚡ Pros / Cons

| Pros | Cons |
|------|------|
| Very fast | Jetson-only |
| Hardware accelerated | Requires CUDA |
| Low latency | Not portable |

---

### 🎯 Best Use Cases
- Autonomous UAVs
- Robotics
- Real-time AI pipelines

---

## 5. MediaPipe

### 📖 Description
MediaPipe is Google’s real-time perception framework. It provides GPU-accelerated graphs for:
- Optical flow
- Hand tracking
- Pose estimation

Motion detection is indirect, based on vector flow or object movement.

---

### 🔁 Typical MediaPipe Motion Pipeline

```
RTSP Stream
     ↓
MediaPipe Graph
     ↓
Optical Flow / Tracking
     ↓
Motion Estimation
```

---

### ⚡ Pros / Cons

| Pros | Cons |
|------|------|
| GPU optimized | Heavy framework |
| Modular pipelines | Harder to customize |
| Real-time capable | Not lightweight |

---

### 🎯 Best Use Cases
- Gesture recognition
- Smart cameras
- Mobile vision apps

---

## 📌 PART 3 — RECOMMENDED TECHNIQUE BY PLATFORM

| Platform | Best Technique | Best Library |
|----------|----------------|--------------|
| Raspberry Pi + RTSP | Frame differencing | FFmpeg |
| Embedded surveillance | Background subtraction | OpenCV |
| UAV moving camera | Optical flow | VPI |
| AI cameras | Deep learning | PyTorch / TensorRT |
| Desktop research | Any | OpenCV |

---

## 📌 PART 4 — LIGHTWEIGHT EMBEDDED PIPELINE (RECOMMENDED)

### 🎯 Optimal Raspberry Pi Pipeline

```
RTSP Stream
     ↓
FFmpeg Decode
     ↓
Grayscale Frame
     ↓
Frame Difference
     ↓
Threshold
     ↓
Pixel Ratio Check
     ↓
Motion Event
```

This pipeline:
- Uses <10% CPU on Raspberry Pi 4
- Has sub-frame latency
- Requires no OpenCV or GPU

---

## 📌 PART 5 — TECHNIQUE COMPARISON SUMMARY

| Method | CPU Cost | Robustness | Moving Camera | Embedded Friendly |
|--------|----------|------------|---------------|------------------|
| Frame Differencing | ⭐⭐⭐⭐⭐ | ⭐⭐ | ❌ | ✅ |
| Background Subtraction | ⭐⭐⭐ | ⭐⭐⭐⭐ | ❌ | ⚠️ |
| Optical Flow | ⭐ | ⭐⭐⭐⭐⭐ | ✅ | ❌ |
| Deep Learning | ⭐ | ⭐⭐⭐⭐⭐ | ✅ | ❌ |

---

## 📌 FINAL RECOMMENDATION (SIYI + Raspberry Pi)

Use:

> ✅ **FFmpeg + Frame Differencing + Thresholding**

Because:
- Lowest CPU usage
- Lowest latency
- Simplest pipeline
- Works reliably on embedded systems

---

## 📌 Want More?

If needed, this document can be extended with:
- Mathematical formulas
- Code examples (Python/C++)
- Noise robustness improvements
- Camera motion compensation
- Region-of-interest (ROI) detection
- Multi-zone motion alerts

