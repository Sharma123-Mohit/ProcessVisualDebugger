import psutil
import pandas as pd
from datetime import datetime
import time
import threading
import streamlit as st

class ProcessCollector:
    def __init__(self):
        """Initialize the process collector with system history tracking"""
        self.system_history = {
            'timestamps': [],
            'cpu_percent': [],
            'memory_percent': []
        }
        # Start system metrics collection in background
        self.start_system_metrics_collection()
    
    def get_process_data(self):
        """Collect current process information"""
        try:
            process_list = []
            for proc in psutil.process_iter(['pid', 'name', 'username', 'status', 'cpu_percent', 'memory_percent', 'create_time', 'cmdline']):
                try:
                    pinfo = proc.info
                    # Get additional process information
                    pinfo['cpu_percent'] = proc.cpu_percent(interval=0.1)
                    pinfo['memory_percent'] = proc.memory_percent()
                    
                    # Format create time as readable datetime
                    if pinfo['create_time']:
                        pinfo['create_time'] = datetime.fromtimestamp(pinfo['create_time']).strftime('%Y-%m-%d %H:%M:%S')
                    
                    # Join command line arguments
                    if pinfo['cmdline']:
                        pinfo['cmdline'] = ' '.join(pinfo['cmdline'])
                    else:
                        pinfo['cmdline'] = 'N/A'
                    
                    process_list.append(pinfo)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            # Convert to DataFrame for easier manipulation
            df = pd.DataFrame(process_list)
            
            # Handle missing values and data cleanup
            df['cpu_percent'] = df['cpu_percent'].fillna(0).round(1)
            df['memory_percent'] = df['memory_percent'].fillna(0).round(1)
            df['username'] = df['username'].fillna('unknown')
            df['status'] = df['status'].fillna('unknown')
            df['name'] = df['name'].fillna('unknown')
            
            return df
        
        except Exception as e:
            st.error(f"Error collecting process data: {e}")
            return pd.DataFrame()  # Return empty DataFrame on error
    
    def get_process_details(self, pid):
        """Get detailed information about a specific process"""
        try:
            proc = psutil.Process(pid)
            details = {
                'pid': pid,
                'name': proc.name(),
                'status': proc.status(),
                'cpu_percent': proc.cpu_percent(interval=0.1),
                'memory_percent': proc.memory_percent(),
                'create_time': datetime.fromtimestamp(proc.create_time()).strftime('%Y-%m-%d %H:%M:%S'),
                'username': proc.username(),
                'cmdline': ' '.join(proc.cmdline()) if proc.cmdline() else 'N/A',
                'exe': proc.exe(),
                'cwd': proc.cwd(),
                'num_threads': proc.num_threads(),
                'connections': len(proc.connections()),
                'open_files': len(proc.open_files())
            }
            return details
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
            st.error(f"Error getting process details: {e}")
            return None
    
    def get_child_processes(self, pid):
        """Get all child processes of a given process"""
        try:
            proc = psutil.Process(pid)
            children = proc.children(recursive=True)
            
            child_info = []
            for child in children:
                try:
                    info = {
                        'pid': child.pid,
                        'name': child.name(),
                        'status': child.status(),
                        'cpu_percent': child.cpu_percent(interval=0.1),
                        'memory_percent': child.memory_percent(),
                        'create_time': datetime.fromtimestamp(child.create_time()).strftime('%Y-%m-%d %H:%M:%S')
                    }
                    child_info.append(info)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            return pd.DataFrame(child_info) if child_info else pd.DataFrame()
        
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            return pd.DataFrame()
    
    def get_system_metrics(self):
        """Get current system-wide resource metrics"""
        return {
            'cpu_percent': psutil.cpu_percent(interval=0.1),
            'memory_percent': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'boot_time': datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S'),
            'load_avg': psutil.getloadavg()
        }
    
    def start_system_metrics_collection(self):
        """Start collecting system metrics in the background"""
        # This is a simplified version - for a real app, we would use a proper
        # background thread with proper lifecycle management
        self.collect_system_metrics()
    
    def collect_system_metrics(self):
        """Collect system metrics and store in history"""
        now = datetime.now()
        
        # Get current metrics
        try:
            metrics = self.get_system_metrics()
            
            # Store in history
            self.system_history['timestamps'].append(now)
            self.system_history['cpu_percent'].append(metrics['cpu_percent'])
            self.system_history['memory_percent'].append(metrics['memory_percent'])
            
            # Keep history at a reasonable size
            max_history = 300  # 5 minutes at 1 second intervals
            if len(self.system_history['timestamps']) > max_history:
                self.system_history['timestamps'] = self.system_history['timestamps'][-max_history:]
                self.system_history['cpu_percent'] = self.system_history['cpu_percent'][-max_history:]
                self.system_history['memory_percent'] = self.system_history['memory_percent'][-max_history:]
        
        except Exception as e:
            st.error(f"Error collecting system metrics: {e}")
        
        # Schedule the next collection
        threading.Timer(1.0, self.collect_system_metrics).start()
    
    def get_system_history(self):
        """Get the system metrics history"""
        return self.system_history
