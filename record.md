# Video Recorder

## Overview

`record.py` is a Python script that acts as a video recorder node in the distributed system. It subscribes to motion detection flags via ZeroMQ and automatically records video clips from a specified RTSP stream when motion is detected. Recordings are saved as MP4 files, and the process is logged to `log.log`.

## Features

- **Motion-Based Recording**: Starts recording when a motion flag (flag=1) is received.
- **FFmpeg Integration**: Uses FFmpeg to capture and encode video clips.
- **Automatic Directory Creation**: Creates a `recordings/` directory if it doesn't exist.
- **Logging**: Logs recording events and errors to file and console.
- **Discovery**: Inherits discovery capabilities from `BaseNode` for network awareness.

## Dependencies

- `ffmpeg`: For video recording and encoding.
- `zmq`: For ZeroMQ messaging.
- `config.py`: Imports `MOTION_FLAG_PORT`, `MOTION_URL`, `RECORD_DURATION`, `RECORD_FPS`.
- `utils.py`: Provides `BaseNode` class with logging and discovery.

## Configuration

- `MOTION_FLAG_PORT`: Port to subscribe to motion flags (default from config).
- `MOTION_URL`: RTSP URL of the video stream to record from.
- `RECORD_DURATION`: Length of each recording clip in seconds.
- `RECORD_FPS`: Frame rate for the recorded video.

## Usage

Run the script with Python:

```bash
python record.py
```

The script starts discovery, subscribes to motion flags, and waits for events. It runs indefinitely until interrupted with Ctrl+C.

## Output

- **Recordings**: Saved in `recordings/record_YYYY-MM-DDTHH-MM-SS.mp4` (timestamp sanitized).
- **Logs**: Events like "Started recording on motion at {ts}" and "Saved recording: {filename}" are logged to `log.log` and console.

## Functions

- `__init__()`: Initializes the recorder, sets up ZeroMQ subscriber.
- `record_clip(start_ts)`: Records a video clip starting from the given timestamp.
- `subscriber_loop()`: Listens for motion flag messages and triggers recordings.
- `handle_flag(msg)`: Processes motion flag messages.
- `run()`: Starts discovery, subscriber thread, and main loop.

## Notes

- Only one recording can be active at a time (prevents overlapping clips).
- Uses `subprocess` to run FFmpeg commands.
- Recordings are overwritten if a file with the same timestamp exists (due to `-y` flag).
- If FFmpeg fails, an error is logged but the script continues.
