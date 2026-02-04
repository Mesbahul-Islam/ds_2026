import cv2
import numpy as np

def detect_motion():
    print("Debug: Starting motion detection")
    subtractor = cv2.createBackgroundSubtractorMOG2(history=100, varThreshold=50, detectShadows=True)
    
    valid_frames = 0
    for i in range(30):  # Check 30 frames
        frame = get_frame()
        if frame is None:
            print(f"Debug: Frame {i+1} is None, skipping")
            continue
        
        valid_frames += 1
        
        fg_mask = subtractor.apply(frame)
        fg_mask[fg_mask == 127] = 0
        
        kernel = np.ones((5, 5), np.uint8)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
        
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        motion_contours = [c for c in contours if cv2.contourArea(c) > THRESHOLD]
        if motion_contours:
            print(f"Debug: Motion detected on frame {i+1} with {len(motion_contours)} contours")
            return 1
    
    if valid_frames < 5:
        print(f"Debug: Insufficient frames ({valid_frames}/30), stream may be unavailable")
        return -1
    
    print("Debug: No motion detected in 30 frames")
    return 0

def preview_motion():
    cap = cv2.VideoCapture(RTSP_URL, cv2.CAP_FFMPEG)
    if not cap.isOpened():
        print("Error: Could not open webcam")
        return
    
    # Initialize background subtractor
    subtractor = cv2.createBackgroundSubtractorMOG2(history=100, varThreshold=50, detectShadows=True)
    
    print("Motion detection started. Press 'q' to quit.")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame")
            break
        
        # Apply background subtraction
        fg_mask = subtractor.apply(frame)
        
        # Remove shadows
        fg_mask[fg_mask == 127] = 0
        
        # Apply morphological operations to clean up the mask
        kernel = np.ones((5, 5), np.uint8)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Draw bounding boxes around moving objects
        for contour in contours:
            if cv2.contourArea(contour) > 500:  # Filter small contours
                x, y, w, h = cv2.boundingRect(contour)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        
        # Display the result
        cv2.imshow('Motion Detection', frame)
        cv2.imshow('Foreground Mask', fg_mask)
        
        # Exit on 'q' key
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Release resources
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    detect_motion()
