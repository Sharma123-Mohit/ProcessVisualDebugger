import streamlit as st
import psutil
import platform
import time
import pandas as pd
from datetime import datetime

def load_css():
    """Load custom CSS for the app (currently not used as we're sticking with Streamlit's default styling)"""
    # This function is a placeholder in case custom styling is needed in the future
    pass

def format_bytes(bytes, suffix="B"):
    """Format bytes to human-readable format"""
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f} {unit}{suffix}"
        bytes /= factor

def get_os_info():
    """Get basic OS information"""
    return {
        'system': platform.system(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'uptime': time.time() - psutil.boot_time()
    }

def format_uptime(seconds):
    """Format uptime in seconds to a readable format"""
    days, remainder = divmod(seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if days > 0:
        return f"{int(days)}d {int(hours)}h {int(minutes)}m"
    elif hours > 0:
        return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
    else:
        return f"{int(minutes)}m {int(seconds)}s"

def detect_anomalies(df, cpu_threshold=90, memory_threshold=90):
    """Detect processes with high resource usage"""
    anomalies = []
    
    # Detect high CPU usage
    high_cpu = df[df['cpu_percent'] > cpu_threshold]
    for _, proc in high_cpu.iterrows():
        anomalies.append({
            'type': 'CPU',
            'pid': proc['pid'],
            'name': proc['name'],
            'value': proc['cpu_percent'],
            'threshold': cpu_threshold
        })
    
    # Detect high memory usage
    high_memory = df[df['memory_percent'] > memory_threshold]
    for _, proc in high_memory.iterrows():
        anomalies.append({
            'type': 'Memory',
            'pid': proc['pid'],
            'name': proc['name'],
            'value': proc['memory_percent'],
            'threshold': memory_threshold
        })
    
    return anomalies

def process_exists(pid):
    """Check if a process with the given PID exists"""
    try:
        process = psutil.Process(pid)
        return True
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return False

def log_process_event(pid, event_type, details=""):
    """Create a log entry for a process event"""
    try:
        process = psutil.Process(pid)
        process_name = process.name()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"[{timestamp}] Process {process_name} (PID: {pid}) {event_type} {details}"
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return f"[{timestamp}] Unknown Process (PID: {pid}) {event_type} {details}"
