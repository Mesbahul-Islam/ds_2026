import psutil
import time
from config import SYSTEM_MONITOR_INTERVAL, SYSTEM_MONITOR_PORT
from datetime import datetime
import socket
import glob
from typing import Dict, Optional, Tuple
import logging
import sys
import zmq

# Add parent directory to path to import config
sys.path.append('.')

from utils import ZMQNode

def get_cpu_status():
    """Get CPU usage percentage."""
    return psutil.cpu_percent(interval=SYSTEM_MONITOR_INTERVAL)

def get_memory_status():
    """Get memory usage."""
    mem = psutil.virtual_memory()
    return {
        'total': mem.total,
        'available': mem.available,
        'percent': mem.percent,
        'used': mem.used
    }

def get_disk_status_static():
    """Get disk usage (static, no speed)."""
    disk = psutil.disk_usage('/')
    return {
        'total': disk.total,
        'used': disk.used,
        'free': disk.free,
        'percent': disk.percent
    }

def get_network_status_static(net_counters):
    """Get network I/O statistics (static, no speed)."""
    return {
        'bytes_sent': net_counters.bytes_sent,
        'bytes_recv': net_counters.bytes_recv,
        'packets_sent': net_counters.packets_sent,
        'packets_recv': net_counters.packets_recv
    }

def get_temperature_status():
    """Get system temperatures."""
    try:
        temps = psutil.sensors_temperatures()
        if temps:
            # Return the first available temperature sensor
            for sensor, readings in temps.items():
                if readings:
                    temp_value = readings[0].current
                    return f"{temp_value}°C"
        return "Temperature sensors not available"
    except Exception as e:
        return f"Error getting temperature: {e}"

def _find_gpu_stats_path() -> Optional[str]:
    candidates = [
        "/sys/class/drm/renderD128/device/gpu_stats",
    ]
    candidates += sorted(glob.glob("/sys/class/drm/renderD*/device/gpu_stats"))
    candidates += sorted(glob.glob("/sys/class/drm/card*/device/gpu_stats"))
    for path in candidates:
        try:
            with open(path, "r", encoding="utf-8") as f:
                f.readline()
            return path
        except OSError:
            continue
    return None

def _read_gpu_stats(path: str) -> Optional[Tuple[int, Dict[str, int]]]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = [ln.rstrip("\n") for ln in f if ln.strip()]
    except OSError:
        return None

    if len(lines) < 2:
        return None

    header = lines[0].split("\t")
    idx = {name: i for i, name in enumerate(header)}
    if "queue" not in idx or "timestamp" not in idx or "runtime" not in idx:
        return None

    timestamp: Optional[int] = None
    runtimes: Dict[str, int] = {}
    for line in lines[1:]:
        cols = line.split("\t")
        try:
            queue = cols[idx["queue"]]
            timestamp = int(cols[idx["timestamp"]])
            runtime = int(cols[idx["runtime"]])
        except (IndexError, ValueError):
            continue
        runtimes[queue] = runtime

    if timestamp is None or not runtimes:
        return None
    return timestamp, runtimes

def _gpu_busy_percent(prev: Tuple[int, Dict[str, int]], curr: Tuple[int, Dict[str, int]]) -> Optional[float]:
    t0, r0 = prev
    t1, r1 = curr
    dt = t1 - t0
    if dt <= 0:
        return None

    busy = 0
    for queue, runtime1 in r1.items():
        if queue == "cpu":
            continue
        busy += max(0, runtime1 - r0.get(queue, 0))

    pct = 100.0 * (busy / dt)
    if pct < 0:
        pct = 0.0
    if pct > 100:
        pct = 100.0
    return pct

def get_speeds():
    """Get disk and network I/O speeds over SYSTEM_MONITOR_INTERVAL."""
    # Get initial counters for speed calculations
    io1 = psutil.disk_io_counters()
    net1 = psutil.net_io_counters()

    gpu_stats_path = _find_gpu_stats_path()
    gpu1 = _read_gpu_stats(gpu_stats_path) if gpu_stats_path else None
    
    # Sleep for interval
    time.sleep(SYSTEM_MONITOR_INTERVAL)
    
    # Get final counters
    io2 = psutil.disk_io_counters()
    net2 = psutil.net_io_counters()

    gpu2 = _read_gpu_stats(gpu_stats_path) if gpu_stats_path else None
    
    # Calculate speeds
    if io1 and io2:
        read_speed = (io2.read_bytes - io1.read_bytes) / SYSTEM_MONITOR_INTERVAL
        write_speed = (io2.write_bytes - io1.write_bytes) / SYSTEM_MONITOR_INTERVAL
    else:
        read_speed = 0
        write_speed = 0
    
    if net1 and net2:
        send_speed = (net2.bytes_sent - net1.bytes_sent) / SYSTEM_MONITOR_INTERVAL
        recv_speed = (net2.bytes_recv - net1.bytes_recv) / SYSTEM_MONITOR_INTERVAL
    else:
        send_speed = 0
        recv_speed = 0

    gpu_usage_percent = None
    if gpu1 is not None and gpu2 is not None:
        gpu_usage_percent = _gpu_busy_percent(gpu1, gpu2)
    
    return {
        'read_speed': read_speed,
        'write_speed': write_speed,
        'send_speed': send_speed,
        'recv_speed': recv_speed,
        'gpu_usage_percent': gpu_usage_percent,
    }

class SystemMonitor(ZMQNode):
    def __init__(self):
        super().__init__('system_monitor')
        self.pub_port = SYSTEM_MONITOR_PORT  # For discovery
        self.status_pub = self.context.socket(zmq.PUB)
        self.status_pub.bind(f"tcp://*:{SYSTEM_MONITOR_PORT}")

    def publish_status(self, speeds, cpu_usage, mem, temp, gpu):
        """Publish system status via ZeroMQ."""
        timestamp = datetime.now().isoformat()
        
        status_data = {
            'type': 'system_status',
            'node_id': self.node_id,
            'timestamp': timestamp,
            'cpu': cpu_usage,
            'memory_used_gb': mem['used'] / (1024**3),
            'memory_total_gb': mem['total'] / (1024**3),
            'memory_percent': mem['percent'],
            'disk_read_kbs': speeds['read_speed'] / 1024,
            'disk_write_kbs': speeds['write_speed'] / 1024,
            'network_send_kbs': speeds['send_speed'] / 1024,
            'network_recv_kbs': speeds['recv_speed'] / 1024,
            'temperature': temp,
            'gpu': gpu
        }
        
        self.status_pub.send_json(status_data)
        
        # Also log locally
        message = (
            f"[{timestamp}] Node ID: {self.node_id}, "
            f"CPU: {cpu_usage}%, "
            f"Memory: {mem['used'] / (1024**3):.2f}/{mem['total'] / (1024**3):.2f} GB ({mem['percent']}%), "
            f"Disk R/W: {speeds['read_speed'] / 1024:.2f}/{speeds['write_speed'] / 1024:.2f} KB/s, "
            f"Network U/D: {speeds['send_speed'] / 1024:.2f}/{speeds['recv_speed'] / 1024:.2f} KB/s, "
            f"Temp: {temp}, "
            f"GPU: {gpu}"
        )
        logging.info(message)

    def run(self):
        # Start discovery thread
        self.start_discovery()

        logging.info(f"[STATUS_PUB:{self.node_id}] Listening on tcp://*:{SYSTEM_MONITOR_PORT}")
        logging.info(f"[PUB:{self.node_id}] Local IP: {self.get_local_ip()}")

        logging.info("Starting system monitoring... Press Ctrl+C to stop.")

        try:
            while True:
                # Get speeds (includes sleep)
                speeds = get_speeds()
                
                # Get other stats
                cpu = psutil.cpu_percent(interval=0)
                mem = get_memory_status()
                temp = get_temperature_status()
                gpu_pct = speeds.get("gpu_usage_percent")
                gpu = f"{gpu_pct:.1f}%" if isinstance(gpu_pct, (int, float)) else "N/A"
                
                self.publish_status(speeds, cpu, mem, temp, gpu)

        except KeyboardInterrupt:
            logging.info("User stopped system monitoring with Ctrl+C.")
        finally:
            self.status_pub.close()
            self.cleanup()


if __name__ == "__main__":
    monitor = SystemMonitor()
    monitor.run()
