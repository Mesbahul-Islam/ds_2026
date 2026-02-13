"""
Run with: streamlit run server.py

"""
import zmq
import threading
import sys
import time
from datetime import datetime
from config import SYSTEM_MONITOR_PORT, SYSTEM_MONITOR_INTERVAL
from collections import deque
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# Add parent directory to path to import config
sys.path.append('.')

# --- Backend: Data Collection (Cached Resource) ---
@st.cache_resource
class DataCollector:
    def __init__(self):
        self.data = deque(maxlen=60)
        self.lock = threading.Lock()
        self.running = True
        self.thread = threading.Thread(target=self._subscriber_thread, daemon=True)
        self.thread.start()
        print("DataCollector started")

    def _subscriber_thread(self):
        context = zmq.Context()
        socket = context.socket(zmq.SUB)
        try:
            socket.connect(f"tcp://localhost:{SYSTEM_MONITOR_PORT}")
            socket.setsockopt_string(zmq.SUBSCRIBE, "")
            print(f"Listening on {SYSTEM_MONITOR_PORT}")
            
            while self.running:
                try:
                    if socket.poll(1000):
                        msg = socket.recv_json()
                        with self.lock:
                            self.data.append(msg)
                except Exception as e:
                    print(f"Error accessing socket: {e}")
                    time.sleep(1)
        except Exception as e:
            print(f"Connection error: {e}")
        finally:
            socket.close()
            context.term()

    def get_dataframe(self):
        with self.lock:
            if not self.data:
                return pd.DataFrame()
            df = pd.DataFrame(list(self.data))
            if not df.empty and 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp'], format='mixed')
                df['numeric_gpu'] = df['gpu'].apply(lambda x: float(x.rstrip('%')) if isinstance(x, str) and x.endswith('%') and x != 'N/A' else float('nan'))
                df['numeric_temp'] = df['temperature'].apply(lambda x: float(x.rstrip('°C')) if isinstance(x, str) and x.endswith('°C') and 'not available' not in x.lower() else float('nan'))
            return df
            
    def get_latest(self):
        with self.lock:
             return self.data[-1] if self.data else None

# Initialize the collector (singleton)
collector = DataCollector()

# --- Frontend: Dashboard ---
def run_dashboard():
    st.set_page_config(page_title="System Monitor", page_icon="📊", layout="wide")
    st.title("📊 Live System Monitor (Last 60s)")
    
    # Get data
    df = collector.get_dataframe()
    latest = collector.get_latest()

    if df.empty:
        st.warning("Waiting for data... Ensure system_monitor.py is running.")
        time.sleep(1)
        st.rerun()
        return

    st.subheader(f"Node ID: {latest.get('node_id', 'Unknown')}")

    # Metrics Row
    cols = st.columns(4)
    cols[0].metric("CPU", f"{latest.get('cpu', 0):.1f}%")
    cols[1].metric("Memory", f"{latest.get('memory_used_gb', 0):.1f}/{latest.get('memory_total_gb', 0):.1f} GB")
    cols[2].metric("Temp", f"{latest.get('temperature', 'N/A')}")
    cols[3].metric("GPU", f"{latest.get('gpu', 'N/A')}")

    st.divider()

    # I/O Metrics Row
    cols2 = st.columns(4)
    cols2[0].metric("Disk Read", f"{latest.get('disk_read_kbs', 0):.1f} KB/s")
    cols2[1].metric("Disk Write", f"{latest.get('disk_write_kbs', 0):.1f} KB/s")
    cols2[2].metric("Net Recv", f"{latest.get('network_recv_kbs', 0):.1f} KB/s")
    cols2[3].metric("Net Send", f"{latest.get('network_send_kbs', 0):.1f} KB/s")

    # Charts Row
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("System Metrics")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['cpu'], name='CPU %'))
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['memory_percent'], name='RAM %'))
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['numeric_gpu'], name='GPU %'))
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['numeric_temp'], name='Temp °C'))
        fig.update_layout(
            yaxis=dict(title='Usage (%) / Temp (°C)', range=[0, 100]),
            height=300, margin=dict(l=0, r=0, t=30, b=0)
        )
        st.plotly_chart(fig, width='stretch')

    with col2:
        st.subheader("I/O Metrics (KB/s)")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['network_recv_kbs'], name='Net Recv'))
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['network_send_kbs'], name='Net Send'))
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['disk_read_kbs'], name='Disk Read', yaxis='y2'))
        fig.add_trace(go.Scatter(x=df['timestamp'], y=df['disk_write_kbs'], name='Disk Write', yaxis='y2'))
        fig.update_layout(
            yaxis=dict(title='Network (KB/s)'),
            yaxis2=dict(title='Disk (KB/s)', overlaying='y', side='right'),
            height=300, margin=dict(l=0, r=0, t=30, b=0)
        )
        st.plotly_chart(fig, width='stretch')

    # Auto-refresh loop
    time.sleep(SYSTEM_MONITOR_INTERVAL)
    st.rerun()

if __name__ == "__main__":
    if 'streamlit' in sys.modules:
        run_dashboard()
    else:
        # CLI starter
        import subprocess
        print("Starting Dashboard...")
        subprocess.run(["streamlit", "run", __file__, "--server.headless", "true", "--server.port", "8501"])
