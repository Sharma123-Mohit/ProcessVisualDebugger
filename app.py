import streamlit as st
import time
import pandas as pd
from datetime import datetime
import threading

# Import custom modules
from process_collector import ProcessCollector
from process_visualizer import ProcessVisualizer
from process_debugger import ProcessDebugger
from utils import load_css

# Set up page config
st.set_page_config(
    page_title="OS Process Debugger",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state variables if they don't exist
if 'process_data' not in st.session_state:
    st.session_state['process_data'] = pd.DataFrame()
if 'process_history' not in st.session_state:
    st.session_state['process_history'] = {}
if 'event_log' not in st.session_state:
    st.session_state['event_log'] = []
if 'paused' not in st.session_state:
    st.session_state['paused'] = False
if 'selected_process' not in st.session_state:
    st.session_state['selected_process'] = None
if 'selected_pid' not in st.session_state:
    st.session_state['selected_pid'] = None
if 'update_interval' not in st.session_state:
    st.session_state['update_interval'] = 2.0  # default update interval in seconds
if 'last_update_time' not in st.session_state:
    st.session_state['last_update_time'] = datetime.now()

# Initialize our components
collector = ProcessCollector()
visualizer = ProcessVisualizer()
debugger = ProcessDebugger()

# Title and description
st.title("OS Process Debugging Toolkit")
st.markdown("""
This toolkit provides real-time visualization and debugging capabilities for OS processes.
Monitor resource usage, detect anomalies, and interact with processes directly through the interface.
""")

# Sidebar controls
with st.sidebar:
    st.header("Controls")
    
    # Update interval selector
    update_interval = st.slider(
        "Update Interval (seconds)", 
        min_value=1.0, 
        max_value=10.0, 
        value=st.session_state['update_interval'],
        step=0.5
    )
    st.session_state['update_interval'] = update_interval
    
    # Pause/Resume button
    if st.session_state['paused']:
        if st.button("Resume Monitoring"):
            st.session_state['paused'] = False
    else:
        if st.button("Pause Monitoring"):
            st.session_state['paused'] = True
    
    # Filters
    st.subheader("Filters")
    cpu_threshold = st.slider("Show processes above CPU %", 0.0, 100.0, 0.0)
    memory_threshold = st.slider("Show processes above Memory %", 0.0, 100.0, 0.0)
    search_term = st.text_input("Search by name:")
    
    st.subheader("View Options")
    view_option = st.radio(
        "Display Mode",
        ("Overview", "Detailed Process View", "System Timeline")
    )
    
    # Refresh button
    if st.button("Force Refresh"):
        st.session_state['last_update_time'] = datetime.now()
        st.rerun()

# Main content area
def update_process_data():
    """Update process data in the session state"""
    if not st.session_state['paused']:
        # Get new process data
        processes = collector.get_process_data()
        
        # Apply filters
        filtered_processes = processes
        if cpu_threshold > 0:
            filtered_processes = filtered_processes[filtered_processes['cpu_percent'] >= cpu_threshold]
        if memory_threshold > 0:
            filtered_processes = filtered_processes[filtered_processes['memory_percent'] >= memory_threshold]
        if search_term:
            filtered_processes = filtered_processes[filtered_processes['name'].str.contains(search_term, case=False)]
        
        # Store the filtered data
        st.session_state['process_data'] = filtered_processes
        
        # Update process history for tracking state changes
        for _, process in filtered_processes.iterrows():
            pid = process['pid']
            if pid not in st.session_state['process_history']:
                st.session_state['process_history'][pid] = {
                    'states': [process['status']],
                    'timestamps': [datetime.now()],
                    'cpu_history': [process['cpu_percent']],
                    'memory_history': [process['memory_percent']]
                }
            else:
                # Check for state changes
                if process['status'] != st.session_state['process_history'][pid]['states'][-1]:
                    # Log the state change
                    log_event(
                        f"Process {process['name']} (PID: {pid}) changed state from "
                        f"{st.session_state['process_history'][pid]['states'][-1]} to {process['status']}"
                    )
                
                # Update the history
                st.session_state['process_history'][pid]['states'].append(process['status'])
                st.session_state['process_history'][pid]['timestamps'].append(datetime.now())
                st.session_state['process_history'][pid]['cpu_history'].append(process['cpu_percent'])
                st.session_state['process_history'][pid]['memory_history'].append(process['memory_percent'])
                
                # Keep history at a reasonable size
                if len(st.session_state['process_history'][pid]['states']) > 100:
                    st.session_state['process_history'][pid]['states'] = st.session_state['process_history'][pid]['states'][-100:]
                    st.session_state['process_history'][pid]['timestamps'] = st.session_state['process_history'][pid]['timestamps'][-100:]
                    st.session_state['process_history'][pid]['cpu_history'] = st.session_state['process_history'][pid]['cpu_history'][-100:]
                    st.session_state['process_history'][pid]['memory_history'] = st.session_state['process_history'][pid]['memory_history'][-100:]
        
        # Check for anomalies (high resource usage)
        for _, process in filtered_processes.iterrows():
            if process['cpu_percent'] > 90:  # Arbitrary threshold for demonstration
                log_event(f"⚠️ High CPU usage detected: {process['name']} (PID: {process['pid']}) at {process['cpu_percent']:.1f}%")
            if process['memory_percent'] > 80:  # Arbitrary threshold for demonstration
                log_event(f"⚠️ High memory usage detected: {process['name']} (PID: {process['pid']}) at {process['memory_percent']:.1f}%")
        
        # Update the last update time
        st.session_state['last_update_time'] = datetime.now()

def log_event(message):
    """Add an event to the log with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    st.session_state['event_log'].append(f"[{timestamp}] {message}")
    # Keep log at a reasonable size
    if len(st.session_state['event_log']) > 100:
        st.session_state['event_log'] = st.session_state['event_log'][-100:]

# Update data periodically
elapsed = (datetime.now() - st.session_state['last_update_time']).total_seconds()
if elapsed >= st.session_state['update_interval'] or st.session_state['process_data'].empty:
    update_process_data()

# Display different views based on selection
if view_option == "Overview":
    # Display CPU and Memory usage overview
    st.subheader("System Resource Usage")
    col1, col2 = st.columns(2)
    
    with col1:
        cpu_fig = visualizer.create_cpu_usage_chart(st.session_state['process_data'])
        st.plotly_chart(cpu_fig, use_container_width=True)
    
    with col2:
        memory_fig = visualizer.create_memory_usage_chart(st.session_state['process_data'])
        st.plotly_chart(memory_fig, use_container_width=True)
    
    # Display process table with interactive elements
    st.subheader("Active Processes")
    
    # Create an interactive table with selection
    if not st.session_state['process_data'].empty:
        # Display only the most useful columns in the table
        display_df = st.session_state['process_data'][['pid', 'name', 'status', 'cpu_percent', 'memory_percent']]
        display_df = display_df.sort_values(by='cpu_percent', ascending=False)
        
        # Add color highlighting based on resource usage
        st.dataframe(
            display_df.style.apply(
                lambda row: [
                    f"background-color: rgba(255, 0, 0, {min(row['cpu_percent']/100, 0.7)})" if col == 'cpu_percent' else
                    f"background-color: rgba(0, 0, 255, {min(row['memory_percent']/100, 0.7)})" if col == 'memory_percent' else
                    "" for col in display_df.columns
                ], axis=1
            ),
            height=400,
            use_container_width=True
        )
        
        # Process selection
        pid_list = display_df['pid'].tolist()
        pid_names = [f"{pid} - {display_df[display_df['pid'] == pid]['name'].values[0]}" for pid in pid_list]
        
        selected_process = st.selectbox(
            "Select a process for detailed view or actions:",
            options=pid_names,
            index=0 if pid_names else None
        )
        
        if selected_process:
            selected_pid = int(selected_process.split(' - ')[0])
            st.session_state['selected_pid'] = selected_pid
            
            # Debug actions
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("View Details"):
                    st.session_state['selected_process'] = selected_pid
                    # Switch to detailed view
                    st.rerun()
            
            with col2:
                if st.button("Terminate Process"):
                    success, message = debugger.terminate_process(selected_pid)
                    if success:
                        log_event(f"Process {selected_pid} terminated successfully")
                        st.success(message)
                    else:
                        log_event(f"Failed to terminate process {selected_pid}: {message}")
                        st.error(message)
                    time.sleep(1)  # Give some time for the UI to update
                    st.rerun()
            
            with col3:
                if st.button("Suspend/Resume Process"):
                    process_info = display_df[display_df['pid'] == selected_pid]
                    process_name = process_info['name'].values[0] if not process_info.empty else "Unknown"
                    
                    success, message = debugger.suspend_resume_process(selected_pid)
                    if success:
                        log_event(f"Process {process_name} (PID: {selected_pid}) {message}")
                        st.success(message)
                    else:
                        log_event(f"Failed to suspend/resume process {selected_pid}: {message}")
                        st.error(message)
                    time.sleep(1)  # Give some time for the UI to update
                    st.rerun()

elif view_option == "Detailed Process View":
    if st.session_state['selected_pid'] is not None:
        selected_pid = st.session_state['selected_pid']
        process_info = st.session_state['process_data'][st.session_state['process_data']['pid'] == selected_pid]
        
        if not process_info.empty:
            process_name = process_info['name'].values[0]
            st.subheader(f"Detailed View: {process_name} (PID: {selected_pid})")
            
            # Process info card
            st.info(f"""
            **Status:** {process_info['status'].values[0]}  
            **User:** {process_info['username'].values[0]}  
            **Created:** {process_info['create_time'].values[0]}  
            **Command:** {process_info['cmdline'].values[0]}
            """)
            
            # Resource usage over time
            if selected_pid in st.session_state['process_history']:
                history = st.session_state['process_history'][selected_pid]
                
                st.subheader("Resource Usage History")
                history_fig = visualizer.create_process_history_chart(
                    history['timestamps'], 
                    history['cpu_history'], 
                    history['memory_history'],
                    process_name
                )
                st.plotly_chart(history_fig, use_container_width=True)
                
                # State changes
                st.subheader("State Changes")
                state_changes = []
                for i in range(1, len(history['states'])):
                    if history['states'][i] != history['states'][i-1]:
                        state_changes.append({
                            'Time': history['timestamps'][i].strftime("%H:%M:%S"),
                            'From': history['states'][i-1],
                            'To': history['states'][i]
                        })
                
                if state_changes:
                    st.table(pd.DataFrame(state_changes))
                else:
                    st.info("No state changes detected yet.")
            
            # Child processes
            children = collector.get_child_processes(selected_pid)
            if not children.empty:
                st.subheader("Child Processes")
                st.dataframe(
                    children[['pid', 'name', 'status', 'cpu_percent', 'memory_percent']],
                    use_container_width=True
                )
            
            # Back button
            if st.button("Back to Overview"):
                st.session_state['selected_process'] = None
                st.session_state['selected_pid'] = None
                st.rerun()
        else:
            st.warning(f"Process with PID {selected_pid} is no longer available.")
            if st.button("Back to Overview"):
                st.session_state['selected_process'] = None
                st.session_state['selected_pid'] = None
                st.rerun()
    else:
        st.info("Select a process from the Overview to see detailed information.")
        if st.button("Go to Overview"):
            st.rerun()

elif view_option == "System Timeline":
    st.subheader("System Process Timeline")
    
    # Create a timeline visualization of processes
    timeline_fig = visualizer.create_process_timeline(st.session_state['process_data'])
    st.plotly_chart(timeline_fig, use_container_width=True)
    
    # System-wide CPU and memory history
    st.subheader("System Resource Utilization")
    system_metrics = collector.get_system_metrics()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("CPU Usage", f"{system_metrics['cpu_percent']:.1f}%")
    with col2:
        st.metric("Memory Usage", f"{system_metrics['memory_percent']:.1f}%")
    
    # Resource history chart
    system_history_fig = visualizer.create_system_history_chart(
        collector.get_system_history()
    )
    st.plotly_chart(system_history_fig, use_container_width=True)

# Event log at the bottom
with st.expander("Event Log", expanded=False):
    for event in reversed(st.session_state['event_log']):
        st.text(event)

# Display last update time and stats
st.sidebar.markdown("---")
st.sidebar.text(f"Last updated: {st.session_state['last_update_time'].strftime('%H:%M:%S')}")
if not st.session_state['process_data'].empty:
    st.sidebar.text(f"Processes shown: {len(st.session_state['process_data'])}")
st.sidebar.text(f"Total events logged: {len(st.session_state['event_log'])}")

# Auto-refresh the app
if not st.session_state['paused']:
    time_to_next_update = max(0, st.session_state['update_interval'] - 
                            (datetime.now() - st.session_state['last_update_time']).total_seconds())
    if time_to_next_update <= 0:
        st.rerun()
