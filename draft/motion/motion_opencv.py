import time
from typing import Optional, Tuple

import cv2


RTSP_URL = "rtsp://192.168.192.110:31554/nvstream/opt/store/nvstreamer_videos/4228660-hd_1920_1080_25fps.mp4"
WIDTH = 640
HEIGHT = 360
FPS = 15
THRESHOLD = 25
MOTION_RATIO_TRIGGER = 0.02


def build_capture(rtsp_url: str, width: int, height: int, fps: int) -> cv2.VideoCapture:
	cap = cv2.VideoCapture(rtsp_url)
	if width > 0:
		cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
	if height > 0:
		cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
	if fps > 0:
		cap.set(cv2.CAP_PROP_FPS, fps)
	return cap


def read_frame(cap: cv2.VideoCapture) -> Optional[cv2.Mat]:
	ok, frame = cap.read()
	if not ok or frame is None:
		return None
	return frame


def preprocess_frame(frame: cv2.Mat) -> cv2.Mat:
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	blurred = cv2.GaussianBlur(gray, (5, 5), 0)
	return blurred


def compute_motion_ratio(prev: cv2.Mat, curr: cv2.Mat, threshold: int) -> Tuple[float, cv2.Mat]:
	diff = cv2.absdiff(prev, curr)
	_, thresh = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY)
	changed = cv2.countNonZero(thresh)
	total = thresh.shape[0] * thresh.shape[1]
	ratio = changed / total if total else 0.0
	return ratio, thresh


def process_stream(
	rtsp_url: str,
	width: int,
	height: int,
	fps: int,
	threshold: int,
	motion_ratio_trigger: float,
) -> None:
	cap = build_capture(rtsp_url, width, height, fps)
	if not cap.isOpened():
		raise RuntimeError("Failed to open video stream")

	prev = None
	try:
		while True:
			t0 = time.perf_counter()
			frame = read_frame(cap)
			if frame is None:
				time.sleep(0.1)
				continue

			curr = preprocess_frame(frame)
			motion_ratio = 0.0

			if prev is not None:
				motion_ratio, _ = compute_motion_ratio(prev, curr, threshold)
				# if motion_ratio >= motion_ratio_trigger:
					# print(f"motion_detected ratio={motion_ratio:.4f}")

			prev = curr
			t1 = time.perf_counter()
			latency_ms = (t1 - t0) * 1000.0
			print(f"latency_ms={latency_ms:.2f} motion_ratio={motion_ratio:.4f}")
	finally:
		cap.release()


def main() -> None:
	process_stream(
		rtsp_url=RTSP_URL,
		width=WIDTH,
		height=HEIGHT,
		fps=FPS,
		threshold=THRESHOLD,
		motion_ratio_trigger=MOTION_RATIO_TRIGGER,
	)


if __name__ == "__main__":
	main()
