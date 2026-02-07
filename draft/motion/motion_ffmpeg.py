import ffmpeg
import numpy as np
import cv2
import time

# Constants
url = 'rtsp://192.168.0.181:8554/stream'
motion_threshold = 0.2  # Fraction of pixels that must change to trigger motion
pixel_diff_threshold = 25  # Minimum pixel difference to count as change
blur_sigma = 1.5  # Sigma for Gaussian blur to reduce noise
kernel_size = 5

# Function for Gaussian blur using OpenCV
def gaussian_blur(image, kernel_size, sigma):
    return cv2.GaussianBlur(image, (kernel_size, kernel_size), sigma)

# Function for motion detection
def detect_motion(prev_frame, current_frame, pixel_diff_threshold):
    if prev_frame is None:
        return None
    
    diff = np.abs(current_frame - prev_frame)
    changed_pixels = (diff > pixel_diff_threshold).astype(np.float32)
    change_ratio = np.mean(changed_pixels)
    
    return change_ratio


# Main setup
probe = ffmpeg.probe(url)
video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
width = int(video_info['width'])
height = int(video_info['height'])

process = (ffmpeg
    .input(url, rtsp_transport='udp')
    .output('pipe:', format='rawvideo', pix_fmt='gray8')
    .global_args('-loglevel', 'quiet')
    .run_async(pipe_stdout=True))

bytes_per_frame = width * height
prev_blurred_frame = None

print("Starting motion detection... Press Ctrl+C to stop.")

try:
    while True:
        start_time = time.perf_counter()
        
        in_bytes = process.stdout.read(bytes_per_frame)
        
        if len(in_bytes) != bytes_per_frame:
            print("Incomplete frame received. Try again...")
            break
        
        frame = np.frombuffer(in_bytes, np.uint8).reshape((height, width))
        
        blurred_frame = gaussian_blur(frame, kernel_size, blur_sigma)
        
        change_ratio = detect_motion(prev_blurred_frame, blurred_frame, pixel_diff_threshold)
        
        end_time = time.perf_counter()
        latency = (end_time - start_time) * 1000  # Convert to milliseconds
        
        if change_ratio is not None:
            if change_ratio > motion_threshold:
                print(f"Change ratio: {change_ratio:.4f} Motion 1! Latency: {latency:.2f}ms")
                # time.sleep(1)
            else:
                print(f"Change ratio: {change_ratio:.4f} Motion 0! Latency: {latency:.2f}ms")
                
        prev_blurred_frame = blurred_frame

except KeyboardInterrupt:
    print("Stopping motion detection.")
finally:
    process.terminate()