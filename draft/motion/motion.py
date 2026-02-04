import cv2
import numpy as np

THRESHOLD = 25
FPS = 10

RTSP_URL = "rtsp://localhost:8554/stream"

# Global video capture object
_video_cap = None

def get_frame():
    global _video_cap
    if _video_cap is None or not _video_cap.isOpened():
        _video_cap = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)
        if not _video_cap.isOpened():
            return None
        _video_cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        _video_cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        _video_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
    
    ret, frame = _video_cap.read()
    if not ret:
        _video_cap = None
        return None
    
    return frame

def detect_motion(frame, subtractor=None):
    if frame is None:
        return -1
    
    if subtractor is None:
        return 0
    
    # Resize frame for faster processing
    small_frame = cv2.resize(frame, (160, 120))
    
    fg_mask = subtractor.apply(small_frame)
    
    # Simple threshold check - count white pixels
    white_pixels = cv2.countNonZero(fg_mask)
    
    if white_pixels > 100:  # Simplified threshold
        return 1
    
    return 0

def preview_motion(frame, motion_result=None, subtractor=None):
    if frame is None:
        return True
    
    # Just show the frame without processing for speed
    cv2.imshow('Motion Detection Preview', frame)
    
    # Exit on 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        return False
    
    return True

if __name__ == "__main__":
    subtractor = cv2.createBackgroundSubtractorMOG2(history=20, varThreshold=30, detectShadows=False)
    print("Starting motion detection. Press 'q' in preview window to quit.")
    
    frame_count = 0
    motion = 0
    try:
        while True:
            frame = get_frame()
            if frame is None:
                continue
            
            # Only detect motion every 3rd frame to reduce processing
            if frame_count % 3 == 0:
                motion = detect_motion(frame, subtractor)
            
            if not preview_motion(frame, motion, subtractor):
                break
                
            # Print motion status every 30 frames
            frame_count += 1
            if frame_count % 30 == 0:
                status = "YES" if motion == 1 else "NO" if motion == 0 else "ERROR"
                print(f"Motion: {status}")
                
    except KeyboardInterrupt:
        print("\nStopped by user")
    finally:
        cv2.destroyAllWindows()
        if '_video_cap' in globals() and _video_cap is not None:
            _video_cap.release()
