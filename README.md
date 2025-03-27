# OS Process Debugging Toolkit

An immersive toolkit for debugging and visualizing operating system processes with real-time analytics and interactive features.

![Process Debugger](generated-icon.png)

## Overview

The OS Process Debugging Toolkit provides developers and system administrators with a powerful, intuitive interface for monitoring and debugging system processes in real-time. Built with Streamlit and psutil, this application offers comprehensive visualization of system states, resource usage tracking, and interactive debugging capabilities.

## Features

### Real-Time Monitoring
- **Process Overview**: View all active processes with CPU and memory usage statistics
- **Resource Visualization**: Interactive charts displaying top processes by CPU and memory consumption
- **System Timeline**: Visual representation of process states and resource utilization over time
- **Anomaly Detection**: Automatic alerts for processes with unusually high resource usage

### Interactive Debugging
- **Process Control**: Terminate, suspend, or resume processes directly from the interface
- **Detailed Process View**: In-depth information about specific processes including:
  - Resource usage history
  - State changes over time
  - Child processes
  - Process logs and details

### Customizable Interface
- **Filtering Options**: Filter processes by name, CPU usage, or memory consumption
- **Update Intervals**: Adjust data refresh rate based on your needs
- **View Modes**: Switch between overview, detailed process view, and system timeline

## Architecture

The application is built with a modular architecture consisting of three main components:

1. **Process Collector (`process_collector.py`)**
   - Collects real-time data about system processes
   - Tracks system metrics history
   - Manages background data collection

2. **Process Visualizer (`process_visualizer.py`)**
   - Creates interactive visualizations for process data
   - Generates charts for CPU and memory usage
   - Visualizes process timelines and history

3. **Process Debugger (`process_debugger.py`)**
   - Provides tools to interact with processes
   - Handles process termination, suspension, and resumption
   - Retrieves detailed process information

## Getting Started

### Prerequisites
- Python 3.6+
- Required Python packages (see requirements below)

### Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/os-process-debugger.git
cd os-process-debugger
```

2. Install required packages:
```bash
pip install streamlit pandas plotly psutil numpy
```

3. Run the application:
```bash
streamlit run app.py
```

The application will be available at http://localhost:5000 by default.

## Usage Guide

### Main Dashboard
The main dashboard provides an overview of system processes with interactive charts showing CPU and memory usage. From here, you can:

- Select processes for detailed analysis
- Filter the process list using the sidebar controls
- Pause/resume monitoring to inspect specific system states
- Access debugging tools to interact with processes

### Detailed Process View
When selecting a process for detailed view, you'll see:

- Resource usage history over time
- State changes and transitions
- Child processes and their resource usage
- Process details including command line, creation time, and status

### System Timeline
The system timeline view provides a broader perspective on system state, showing:

- Process relationships and activity
- System-wide resource utilization over time
- Process state transitions

## Technical Details

### Data Collection
The toolkit collects process data using Python's `psutil` library, which provides:
- Cross-platform process information
- Resource usage metrics (CPU, memory, disk, network)
- Process relationships and hierarchies

### Visualization
Interactive visualizations are created with Plotly, offering:
- Real-time updating charts
- Interactive tooltips and zooming
- Color-coded status indicators

### Process Interaction
The toolkit interacts with system processes through `psutil` and OS-specific commands, allowing:
- Safe process termination with proper signal handling
- Process suspension and resumption
- Priority adjustment (where permissions allow)

## Limitations

- Some operations require administrator/root privileges
- Process suspension may not work on all operating systems
- Detailed logs are limited to what the OS exposes via standard interfaces

## Contributing

Contributions to improve the toolkit are welcome! Please feel free to submit pull requests or open issues to suggest improvements or report bugs.

## License

This project is licensed under the MIT License - see the LICENSE file for details.