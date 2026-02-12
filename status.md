# Status Monitor

## Overview

`status.py` is a Python script that continuously monitors and logs system status information for a node in the distributed system. It collects metrics such as CPU usage, memory usage, disk I/O speeds, network I/O speeds, CPU temperature, and GPU usage percentage. The data is logged to both a file (`log.log`) and the console.

## Features

- **CPU Usage**: Percentage of CPU utilization.
- **Memory Usage**: Used and total memory in GB, along with usage percentage.
- **Disk I/O**: Read and write speeds in KB/s.
- **Network I/O**: Send (upload) and receive (download) speeds in KB/s.
- **CPU Temperature**: System temperature from available sensors.
- **GPU Usage**: GPU utilization percentage (if available).

## Dependencies

- `psutil`: For system and hardware monitoring.
- `config.py`: Imports `STATUS_INTERVAL` for the monitoring interval.

## Configuration

- `STATUS_INTERVAL`: Defined in `config.py`, specifies the time interval (in seconds) over which speeds are calculated. The script sleeps for this duration to measure I/O rates.

## Usage

Run the script with Python:

```bash
python status.py
```

The script runs in an infinite loop, logging status updates at intervals based on `STATUS_INTERVAL`. Use Ctrl+C to stop.

## Output

Logs are written in the following format:

```
[timestamp] Node ID: hostname, CPU: x%, Memory: used/total GB (%), Disk R/W: read/write KB/s, Network U/D: send/recv KB/s, Temp: x°C, GPU: x%
```

- **File**: `log.log` in the current directory.
- **Console**: Also printed to stdout with timestamps.

## Functions

- `get_cpu_status()`: Retrieves CPU usage percentage.
- `get_memory_status()`: Gets memory statistics.
- `get_disk_status_static()`: Static disk usage (not used in main loop).
- `get_network_status_static()`: Static network counters (not used in main loop).
- `get_temperature_status()`: Fetches CPU temperature.
- `get_speeds()`: Calculates I/O speeds over `STATUS_INTERVAL`.
- `log_status()`: Formats and logs all status information.

## Notes

- GPU stats are read from `/sys/class/drm/renderD*/device/gpu_stats` if available.
- If sensors are not available, temperature and GPU may show "N/A" or error messages.
- The script uses ZeroMQ context implicitly through imports, but not directly in this file.
