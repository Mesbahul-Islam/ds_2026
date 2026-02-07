#!/usr/bin/env python3
"""System resource monitor using psutil."""

import argparse
import csv
import subprocess
import time
from typing import Optional

import psutil


def get_temperature() -> Optional[float]:
	"""Get CPU temperature in Celsius."""
	try:
		temps = psutil.sensors_temperatures()
		if temps:
			for name, entries in temps.items():
				if entries:
					return entries[0].current
	except (AttributeError, OSError):
		pass
	
	# Fallback for Raspberry Pi
	try:
		with open("/sys/class/thermal/thermal_zone0/temp", "r") as f:
			return float(f.read().strip()) / 1000.0
	except (FileNotFoundError, ValueError):
		pass
	
	return None


def get_gpu_usage() -> Optional[float]:
	"""Get GPU usage percentage (Raspberry Pi specific)."""
	try:
		result = subprocess.run(
			["vcgencmd", "measure_temp"],
			capture_output=True,
			text=True,
			timeout=1
		)
		if result.returncode == 0:
			# vcgencmd returns: temp=47.2'C
			temp_str = result.stdout.strip()
			if "temp=" in temp_str:
				return float(temp_str.split("=")[1].split("'")[0])
	except (FileNotFoundError, subprocess.TimeoutExpired, ValueError):
		pass
	
	return None


def parse_args() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description="Monitor system resources.")
	parser.add_argument("--interval", type=float, default=1.0, help="Seconds between samples.")
	parser.add_argument("--count", type=int, default=0, help="Number of samples (0 = forever).")
	parser.add_argument("--csv", type=str, default="", help="Optional CSV output path.")
	return parser.parse_args()


def main() -> int:
	args = parse_args()
	interval = max(args.interval, 0.1)

	# Initial readings for rate calculations
	prev_disk = psutil.disk_io_counters()
	prev_net = psutil.net_io_counters()
	prev_time = time.time()

	csv_handle = None
	csv_writer = None
	if args.csv:
		csv_handle = open(args.csv, "w", newline="", encoding="ascii")
		csv_writer = csv.writer(csv_handle)

	headers = [
		"timestamp",
		"cpu_percent",
		"mem_percent",
		"temp_c",
		"disk_read_mb_s",
		"disk_write_mb_s",
		"net_rx_mb_s",
		"net_tx_mb_s"
	]
	print("\t".join(headers))
	if csv_writer:
		csv_writer.writerow(headers)

	samples = 0
	try:
		while True:
			time.sleep(interval)
			cur_time = time.time()
			time_delta = cur_time - prev_time

			# Collect metrics
			cpu_pct = psutil.cpu_percent(interval=0)
			mem = psutil.virtual_memory()
			temp = get_temperature()
			
			cur_disk = psutil.disk_io_counters()
			cur_net = psutil.net_io_counters()
			
			# Calculate rates
			disk_read_mb_s = (cur_disk.read_bytes - prev_disk.read_bytes) / time_delta / (1024 * 1024)
			disk_write_mb_s = (cur_disk.write_bytes - prev_disk.write_bytes) / time_delta / (1024 * 1024)
			net_rx_mb_s = (cur_net.bytes_recv - prev_net.bytes_recv) / time_delta / (1024 * 1024)
			net_tx_mb_s = (cur_net.bytes_sent - prev_net.bytes_sent) / time_delta / (1024 * 1024)

			row = [
				time.strftime("%Y-%m-%d %H:%M:%S"),
				f"{cpu_pct:.2f}",
				f"{mem.percent:.2f}",
				f"{temp:.2f}" if temp is not None else "N/A",
				f"{disk_read_mb_s:.2f}",
				f"{disk_write_mb_s:.2f}",
				f"{net_rx_mb_s:.4f}",
				f"{net_tx_mb_s:.4f}"
			]

			print("\t".join(row))
			if csv_writer:
				csv_writer.writerow(row)
				csv_handle.flush()

			# Update previous values
			prev_disk = cur_disk
			prev_net = cur_net
			prev_time = cur_time

			samples += 1
			if args.count > 0 and samples >= args.count:
				break
	finally:
		if csv_handle:
			csv_handle.close()
	
	return 0


if __name__ == "__main__":
	raise SystemExit(main())