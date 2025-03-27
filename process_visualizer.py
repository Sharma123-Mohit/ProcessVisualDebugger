import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st

class ProcessVisualizer:
    def __init__(self):
        """Initialize the process visualizer with color schemes"""
        # Define color schemes
        self.status_colors = {
            'running': '#2ECC71',
            'sleeping': '#F39C12',
            'stopped': '#E74C3C',
            'zombie': '#8E44AD',
            'disk-sleep': '#3498DB',
            'tracing-stop': '#1ABC9C',
            'dead': '#7F8C8D',
            'wake-kill': '#D35400',
            'waking': '#27AE60',
            'parked': '#2980B9',
            'idle': '#95A5A6',
            'locked': '#E67E22',
            'waiting': '#3498DB',
            'suspended': '#9B59B6'
        }
        
        # Ensure all statuses have a color, even if not in our predefined map
        for status in ['unknown']:
            if status.lower() not in self.status_colors:
                self.status_colors[status.lower()] = '#BDC3C7'  # Default color
    
    def create_cpu_usage_chart(self, df):
        """Create a bar chart of processes by CPU usage"""
        if df.empty:
            # Create an empty figure if no data
            fig = go.Figure()
            fig.update_layout(
                title="No process data available",
                xaxis_title="CPU Usage %",
                yaxis_title="Process",
                height=400
            )
            return fig
        
        # Sort and take top 15 processes by CPU usage
        top_processes = df.sort_values('cpu_percent', ascending=False).head(15)
        
        # Create horizontal bar chart
        fig = go.Figure()
        
        # Add bars colored by status
        for status in top_processes['status'].unique():
            status_df = top_processes[top_processes['status'] == status]
            
            # Get color for this status (use lowercase to match our color map)
            color = self.status_colors.get(status.lower(), '#BDC3C7')
            
            fig.add_trace(go.Bar(
                x=status_df['cpu_percent'],
                y=status_df['name'],
                orientation='h',
                name=status,
                marker_color=color,
                text=[f"PID: {pid}" for pid in status_df['pid']],
                customdata=status_df[['pid', 'username']],
                hovertemplate='<b>%{y}</b><br>CPU: %{x:.1f}%<br>PID: %{customdata[0]}<br>User: %{customdata[1]}<br>Status: ' + status + '<extra></extra>'
            ))
        
        # Layout configuration
        fig.update_layout(
            title="Top Processes by CPU Usage",
            xaxis_title="CPU Usage %",
            yaxis_title="",
            barmode='stack',
            height=400,
            legend_title="Process Status",
        )
        
        return fig
    
    def create_memory_usage_chart(self, df):
        """Create a bar chart of processes by memory usage"""
        if df.empty:
            # Create an empty figure if no data
            fig = go.Figure()
            fig.update_layout(
                title="No process data available",
                xaxis_title="Memory Usage %",
                yaxis_title="Process",
                height=400
            )
            return fig
        
        # Sort and take top 15 processes by memory usage
        top_processes = df.sort_values('memory_percent', ascending=False).head(15)
        
        # Create horizontal bar chart
        fig = go.Figure()
        
        # Add bars colored by status
        for status in top_processes['status'].unique():
            status_df = top_processes[top_processes['status'] == status]
            
            # Get color for this status (use lowercase to match our color map)
            color = self.status_colors.get(status.lower(), '#BDC3C7')
            
            fig.add_trace(go.Bar(
                x=status_df['memory_percent'],
                y=status_df['name'],
                orientation='h',
                name=status,
                marker_color=color,
                text=[f"PID: {pid}" for pid in status_df['pid']],
                customdata=status_df[['pid', 'username']],
                hovertemplate='<b>%{y}</b><br>Memory: %{x:.1f}%<br>PID: %{customdata[0]}<br>User: %{customdata[1]}<br>Status: ' + status + '<extra></extra>'
            ))
        
        # Layout configuration
        fig.update_layout(
            title="Top Processes by Memory Usage",
            xaxis_title="Memory Usage %",
            yaxis_title="",
            barmode='stack',
            height=400,
            legend_title="Process Status",
        )
        
        return fig
    
    def create_process_history_chart(self, timestamps, cpu_history, memory_history, process_name):
        """Create a line chart showing CPU and memory history for a process"""
        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # Add CPU usage trace
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=cpu_history,
                name="CPU Usage",
                line=dict(color="#2ECC71", width=2),
                hovertemplate='CPU: %{y:.1f}%<br>Time: %{x}<extra></extra>'
            ),
            secondary_y=False,
        )
        
        # Add memory usage trace
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=memory_history,
                name="Memory Usage",
                line=dict(color="#3498DB", width=2),
                hovertemplate='Memory: %{y:.1f}%<br>Time: %{x}<extra></extra>'
            ),
            secondary_y=True,
        )
        
        # Format the layout
        fig.update_layout(
            title=f"{process_name} Resource Usage Over Time",
            xaxis_title="Time",
            hovermode="x unified",
            height=400,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
        )
        
        # Update y-axes titles
        fig.update_yaxes(title_text="CPU Usage %", secondary_y=False)
        fig.update_yaxes(title_text="Memory Usage %", secondary_y=True)
        
        return fig
    
    def create_process_timeline(self, df):
        """Create a timeline visualization of processes"""
        if df.empty:
            # Create an empty figure if no data
            fig = go.Figure()
            fig.update_layout(
                title="No process data available",
                height=500
            )
            return fig
        
        # Sort processes by CPU usage for visualization
        sorted_df = df.sort_values('cpu_percent', ascending=False).head(20)
        
        # Create figure
        fig = go.Figure()
        
        # Add a trace for each process status
        for i, (index, process) in enumerate(sorted_df.iterrows()):
            status = process['status'].lower()
            color = self.status_colors.get(status, '#BDC3C7')
            
            # Create a trace for each process
            fig.add_trace(go.Scatter(
                x=[0, process['cpu_percent']],  # Use CPU % for width
                y=[i, i],
                mode='lines',
                line=dict(color=color, width=20),
                name=f"{process['name']} ({process['pid']})",
                hoverinfo='text',
                text=f"PID: {process['pid']}<br>Name: {process['name']}<br>Status: {status}<br>CPU: {process['cpu_percent']:.1f}%<br>Memory: {process['memory_percent']:.1f}%"
            ))
        
        # Create legend for process status
        for status, color in self.status_colors.items():
            if status in df['status'].str.lower().values:
                fig.add_trace(go.Scatter(
                    x=[None],
                    y=[None],
                    mode='markers',
                    marker=dict(size=10, color=color),
                    name=status.capitalize(),
                    showlegend=True
                ))
        
        # Update layout
        fig.update_layout(
            title="Process Status Timeline",
            xaxis_title="CPU Usage %",
            yaxis=dict(
                showticklabels=True,
                tickmode='array',
                tickvals=list(range(len(sorted_df))),
                ticktext=[f"{row['name']} ({row['pid']})" for _, row in sorted_df.iterrows()]
            ),
            height=500,
            legend_title="Process Status",
            hovermode="closest"
        )
        
        return fig
    
    def create_system_history_chart(self, system_history):
        """Create a line chart showing CPU and memory history for the entire system"""
        if not system_history['timestamps']:
            # Create an empty figure if no data
            fig = go.Figure()
            fig.update_layout(
                title="No system history data available",
                height=400
            )
            return fig
        
        # Create figure with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": False}]])
        
        # Add CPU usage trace
        fig.add_trace(
            go.Scatter(
                x=system_history['timestamps'],
                y=system_history['cpu_percent'],
                name="CPU Usage",
                line=dict(color="#2ECC71", width=2),
                hovertemplate='CPU: %{y:.1f}%<br>Time: %{x}<extra></extra>'
            )
        )
        
        # Add memory usage trace
        fig.add_trace(
            go.Scatter(
                x=system_history['timestamps'],
                y=system_history['memory_percent'],
                name="Memory Usage",
                line=dict(color="#3498DB", width=2),
                hovertemplate='Memory: %{y:.1f}%<br>Time: %{x}<extra></extra>'
            )
        )
        
        # Format the layout
        fig.update_layout(
            title="System Resource Usage Over Time",
            xaxis_title="Time",
            yaxis_title="Usage %",
            hovermode="x unified",
            height=400,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
        )
        
        return fig
