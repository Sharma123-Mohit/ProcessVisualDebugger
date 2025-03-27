import psutil
import os
import signal
import platform
import streamlit as st

class ProcessDebugger:
    def __init__(self):
        """Initialize the process debugger"""
        self.os_type = platform.system()
    
    def terminate_process(self, pid):
        """Terminate a process by PID"""
        try:
            process = psutil.Process(pid)
            process_name = process.name()
            
            # Terminate the process
            process.terminate()
            
            # Wait for the process to terminate (with timeout)
            try:
                process.wait(timeout=3)
                return True, f"Process {process_name} (PID: {pid}) terminated successfully"
            except psutil.TimeoutExpired:
                # If timeout, try to kill forcefully
                process.kill()
                return True, f"Process {process_name} (PID: {pid}) killed forcefully"
                
        except psutil.NoSuchProcess:
            return False, f"Process with PID {pid} not found"
        except psutil.AccessDenied:
            return False, f"Permission denied to terminate process {pid}"
        except Exception as e:
            return False, f"Error terminating process: {str(e)}"
    
    def suspend_resume_process(self, pid):
        """Suspend or resume a process by PID"""
        try:
            process = psutil.Process(pid)
            process_name = process.name()
            
            # Check if process is already suspended (varies by OS)
            if self.os_type == 'Windows':
                # For Windows, check process status
                if process.status() == psutil.STATUS_STOPPED:
                    process.resume()
                    return True, f"Process {process_name} (PID: {pid}) resumed"
                else:
                    process.suspend()
                    return True, f"Process {process_name} (PID: {pid}) suspended"
            else:
                # For Unix/Linux/MacOS, send SIGSTOP/SIGCONT signals
                try:
                    # Check if process is stopped
                    status = process.status()
                    
                    if status == psutil.STATUS_STOPPED:
                        # Resume with SIGCONT
                        os.kill(pid, signal.SIGCONT)
                        return True, f"Process {process_name} (PID: {pid}) resumed"
                    else:
                        # Suspend with SIGSTOP
                        os.kill(pid, signal.SIGSTOP)
                        return True, f"Process {process_name} (PID: {pid}) suspended"
                except Exception as e:
                    return False, f"Error: {str(e)}"
                
        except psutil.NoSuchProcess:
            return False, f"Process with PID {pid} not found"
        except psutil.AccessDenied:
            return False, f"Permission denied to suspend/resume process {pid}"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def get_process_logs(self, pid, lines=50):
        """Get logs related to a process (implementation depends on OS)"""
        try:
            process = psutil.Process(pid)
            process_name = process.name()
            
            # This is a simplified implementation
            # In a real-world scenario, you would need to access specific log files
            # or use system utilities to get process logs
            
            # For demonstration, we'll just return some process info
            process_info = {
                'pid': pid,
                'name': process_name,
                'status': process.status(),
                'created': process.create_time(),
                'cpu_times': process.cpu_times(),
                'memory_info': process.memory_info(),
                'num_threads': process.num_threads(),
                'connections': process.connections(),
                'open_files': process.open_files()
            }
            
            # Convert process info to log-like format
            logs = []
            logs.append(f"Process Information for {process_name} (PID: {pid})")
            logs.append("-" * 50)
            logs.append(f"Status: {process_info['status']}")
            logs.append(f"Created: {process_info['created']}")
            logs.append(f"CPU User Time: {process_info['cpu_times'].user}")
            logs.append(f"CPU System Time: {process_info['cpu_times'].system}")
            logs.append(f"Memory RSS: {process_info['memory_info'].rss / (1024*1024):.2f} MB")
            logs.append(f"Memory VMS: {process_info['memory_info'].vms / (1024*1024):.2f} MB")
            logs.append(f"Threads: {process_info['num_threads']}")
            logs.append("-" * 50)
            
            # Add connection info
            logs.append("Network Connections:")
            for i, conn in enumerate(process_info['connections']):
                logs.append(f"  Connection {i+1}: {conn}")
            
            # Add open files
            logs.append("Open Files:")
            for i, file in enumerate(process_info['open_files']):
                logs.append(f"  File {i+1}: {file.path}")
            
            return logs
        
        except psutil.NoSuchProcess:
            return [f"Process with PID {pid} not found"]
        except psutil.AccessDenied:
            return [f"Permission denied to access process {pid} information"]
        except Exception as e:
            return [f"Error getting process logs: {str(e)}"]
    
    def set_process_priority(self, pid, priority_level):
        """Set process priority level"""
        try:
            process = psutil.Process(pid)
            process_name = process.name()
            
            # Priority mapping (varies by OS)
            if self.os_type == 'Windows':
                # Windows priorities
                priorities = {
                    'low': psutil.BELOW_NORMAL_PRIORITY_CLASS,
                    'normal': psutil.NORMAL_PRIORITY_CLASS,
                    'high': psutil.ABOVE_NORMAL_PRIORITY_CLASS,
                    'realtime': psutil.REALTIME_PRIORITY_CLASS
                }
                
                if priority_level in priorities:
                    process.nice(priorities[priority_level])
                    return True, f"Priority for {process_name} (PID: {pid}) set to {priority_level}"
            else:
                # Unix priorities (nice values)
                priorities = {
                    'low': 10,
                    'normal': 0,
                    'high': -10,
                    'realtime': -20
                }
                
                if priority_level in priorities:
                    process.nice(priorities[priority_level])
                    return True, f"Priority for {process_name} (PID: {pid}) set to {priority_level}"
            
            return False, f"Invalid priority level: {priority_level}"
            
        except psutil.NoSuchProcess:
            return False, f"Process with PID {pid} not found"
        except psutil.AccessDenied:
            return False, f"Permission denied to set priority for process {pid}"
        except Exception as e:
            return False, f"Error setting process priority: {str(e)}"
