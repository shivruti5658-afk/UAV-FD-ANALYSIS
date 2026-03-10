import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, Any, List, Optional, Tuple
import json


def create_3d_flight_path(df: pd.DataFrame,
                         lat_col: str = 'gps_lat',
                         lon_col: str = 'gps_lon',
                         alt_col: str = 'altitude_m',
                         time_col: str = 'timestamp',
                         color_col: Optional[str] = None) -> go.Figure:
    """
    Create a 3D visualization of the UAV flight path.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        lat_col (str): Name of the latitude column
        lon_col (str): Name of the longitude column
        alt_col (str): Name of the altitude column
        time_col (str): Name of the timestamp column
        color_col (str, optional): Column to use for color coding
        
    Returns:
        go.Figure: Plotly 3D figure
    """
    # Check required columns
    required_cols = [lat_col, lon_col, alt_col]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    # Prepare data
    plot_data = df[required_cols].copy()
    
    # Handle missing values
    plot_data = plot_data.dropna()
    
    if plot_data.empty:
        raise ValueError("No valid GPS data available for 3D visualization")
    
    # Determine color scale
    if color_col and color_col in df.columns:
        colors = df.loc[plot_data.index, color_col]
        colorbar_title = color_col.replace('_', ' ').title()
    else:
        colors = plot_data[alt_col]
        colorbar_title = 'Altitude (m)'
    
    # Create 3D scatter plot
    fig = go.Figure(data=go.Scatter3d(
        x=plot_data[lon_col],
        y=plot_data[lat_col],
        z=plot_data[alt_col],
        mode='markers+lines',
        marker=dict(
            size=4,
            color=colors,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title=colorbar_title)
        ),
        line=dict(
            color=colors,
            colorscale='Viridis',
            width=2
        ),
        text=[f"Alt: {alt:.1f}m" for alt in plot_data[alt_col]],
        hovertemplate='<b>Latitude</b>: %{y:.6f}<br>' +
                     '<b>Longitude</b>: %{x:.6f}<br>' +
                     '<b>Altitude</b>: %{z:.1f}m<br>' +
                     '<extra></extra>'
    ))
    
    # Update layout
    fig.update_layout(
        title='UAV Flight Path - 3D Digital Twin',
        scene=dict(
            xaxis_title='Longitude',
            yaxis_title='Latitude',
            zaxis_title='Altitude (m)',
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=0.5)
            )
        ),
        width=800,
        height=600
    )
    
    return fig


def create_2d_flight_map(df: pd.DataFrame,
                        lat_col: str = 'gps_lat',
                        lon_col: str = 'gps_lon',
                        alt_col: str = 'altitude_m',
                        time_col: str = 'timestamp',
                        color_col: Optional[str] = None) -> go.Figure:
    """
    Create a 2D map visualization of the UAV flight path.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        lat_col (str): Name of the latitude column
        lon_col (str): Name of the longitude column
        alt_col (str): Name of the altitude column
        time_col (str): Name of the timestamp column
        color_col (str, optional): Column to use for color coding
        
    Returns:
        go.Figure: Plotly 2D map figure
    """
    # Check required columns
    required_cols = [lat_col, lon_col]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    # Prepare data
    plot_data = df[required_cols].copy()
    if alt_col in df.columns:
        plot_data[alt_col] = df[alt_col]
    
    # Handle missing values
    plot_data = plot_data.dropna()
    
    if plot_data.empty:
        raise ValueError("No valid GPS data available for 2D visualization")
    
    # Determine color scale
    if color_col and color_col in df.columns:
        colors = df.loc[plot_data.index, color_col]
        colorbar_title = color_col.replace('_', ' ').title()
    elif alt_col in df.columns:
        colors = plot_data[alt_col]
        colorbar_title = 'Altitude (m)'
    else:
        colors = range(len(plot_data))
        colorbar_title = 'Time Sequence'
    
    # Create 2D scatter plot
    fig = go.Figure(data=go.Scattermapbox(
        lat=plot_data[lat_col],
        lon=plot_data[lon_col],
        mode='markers+lines',
        marker=dict(
            size=6,
            color=colors,
            colorscale='Viridis',
            showscale=True,
            colorbar=dict(title=colorbar_title)
        ),
        line=dict(width=3, color=colors),
        text=[f"Alt: {alt:.1f}m" for alt in plot_data[alt_col]] if alt_col in plot_data.columns else None,
        hovertemplate='<b>Latitude</b>: %{lat:.6f}<br>' +
                     '<b>Longitude</b>: %{lon:.6f}<br>' +
                     ('<b>Altitude</b>: %{text}<br>' if alt_col in plot_data.columns else '') +
                     '<extra></extra>'
    ))
    
    # Update layout with mapbox
    center_lat = plot_data[lat_col].mean()
    center_lon = plot_data[lon_col].mean()
    
    fig.update_layout(
        title='UAV Flight Path - 2D Map',
        mapbox=dict(
            style='open-street-map',
            center=dict(lat=center_lat, lon=center_lon),
            zoom=13
        ),
        width=800,
        height=600
    )
    
    return fig


def create_altitude_profile(df: pd.DataFrame,
                           alt_col: str = 'altitude_m',
                           time_col: str = 'timestamp',
                           distance_col: Optional[str] = None) -> go.Figure:
    """
    Create an altitude profile visualization.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        alt_col (str): Name of the altitude column
        time_col (str): Name of the timestamp column
        distance_col (str, optional): Name of the distance column
        
    Returns:
        go.Figure: Plotly altitude profile figure
    """
    if alt_col not in df.columns:
        raise ValueError(f"Altitude column '{alt_col}' not found")
    
    # Determine x-axis
    if distance_col and distance_col in df.columns:
        x_axis = df[distance_col]
        x_title = 'Distance (m)'
    elif time_col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[time_col]):
            x_axis = df[time_col]
            x_title = 'Time'
        else:
            x_axis = df[time_col]
            x_title = 'Time Index'
    else:
        x_axis = df.index
        x_title = 'Data Point Index'
    
    # Create altitude profile
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=x_axis,
        y=df[alt_col],
        mode='lines',
        name='Altitude',
        line=dict(color='blue', width=2),
        fill='tozeroy',
        fillcolor='rgba(0, 100, 200, 0.2)'
    ))
    
    # Update layout
    fig.update_layout(
        title='UAV Altitude Profile',
        xaxis_title=x_title,
        yaxis_title='Altitude (m)',
        width=800,
        height=400,
        showlegend=False
    )
    
    return fig


def create_attitude_visualization(df: pd.DataFrame,
                                 roll_col: str = 'roll_deg',
                                 pitch_col: str = 'pitch_deg',
                                 yaw_col: str = 'yaw_deg',
                                 time_col: str = 'timestamp') -> go.Figure:
    """
    Create attitude (roll, pitch, yaw) visualization.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        roll_col (str): Name of the roll column
        pitch_col (str): Name of the pitch column
        yaw_col (str): Name of the yaw column
        time_col (str): Name of the timestamp column
        
    Returns:
        go.Figure: Plotly attitude figure
    """
    attitude_cols = {'roll': roll_col, 'pitch': pitch_col, 'yaw': yaw_col}
    available_cols = {name: col for name, col in attitude_cols.items() if col in df.columns}
    
    if not available_cols:
        raise ValueError("No attitude columns found")
    
    # Determine x-axis
    if time_col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[time_col]):
            x_axis = df[time_col]
            x_title = 'Time'
        else:
            x_axis = df[time_col]
            x_title = 'Time Index'
    else:
        x_axis = df.index
        x_title = 'Data Point Index'
    
    # Create subplots
    fig = make_subplots(
        rows=len(available_cols), cols=1,
        subplot_titles=list(available_cols.keys()),
        vertical_spacing=0.05
    )
    
    colors = {'roll': 'red', 'pitch': 'green', 'yaw': 'blue'}
    
    for i, (name, col) in enumerate(available_cols.items(), 1):
        fig.add_trace(
            go.Scatter(
                x=x_axis,
                y=df[col],
                mode='lines',
                name=name.capitalize(),
                line=dict(color=colors.get(name, 'blue'), width=1.5)
            ),
            row=i, col=1
        )
    
    # Update layout
    fig.update_layout(
        title='UAV Attitude Data',
        height=200 * len(available_cols),
        showlegend=False
    )
    
    # Update y-axes
    for i in range(1, len(available_cols) + 1):
        fig.update_yaxes(title_text='Degrees', row=i, col=1)
    
    fig.update_xaxes(title_text=x_title, row=len(available_cols), col=1)
    
    return fig


def create_speed_visualization(df: pd.DataFrame,
                             speed_col: str = 'speed_mps',
                             time_col: str = 'timestamp') -> go.Figure:
    """
    Create speed visualization.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        speed_col (str): Name of the speed column
        time_col (str): Name of the timestamp column
        
    Returns:
        go.Figure: Plotly speed figure
    """
    if speed_col not in df.columns:
        raise ValueError(f"Speed column '{speed_col}' not found")
    
    # Determine x-axis
    if time_col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[time_col]):
            x_axis = df[time_col]
            x_title = 'Time'
        else:
            x_axis = df[time_col]
            x_title = 'Time Index'
    else:
        x_axis = df.index
        x_title = 'Data Point Index'
    
    # Create speed plot
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=x_axis,
        y=df[speed_col],
        mode='lines',
        name='Speed',
        line=dict(color='orange', width=2)
    ))
    
    # Add average speed line
    avg_speed = df[speed_col].mean()
    fig.add_hline(
        y=avg_speed,
        line_dash="dash",
        line_color="red",
        annotation_text=f"Avg: {avg_speed:.1f} m/s"
    )
    
    # Update layout
    fig.update_layout(
        title='UAV Speed Profile',
        xaxis_title=x_title,
        yaxis_title='Speed (m/s)',
        width=800,
        height=400,
        showlegend=False
    )
    
    return fig


def create_battery_visualization(df: pd.DataFrame,
                                battery_col: str = 'battery_percent',
                                time_col: str = 'timestamp') -> go.Figure:
    """
    Create battery level visualization.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        battery_col (str): Name of the battery column
        time_col (str): Name of the timestamp column
        
    Returns:
        go.Figure: Plotly battery figure
    """
    if battery_col not in df.columns:
        raise ValueError(f"Battery column '{battery_col}' not found")
    
    # Determine x-axis
    if time_col in df.columns:
        if pd.api.types.is_datetime64_any_dtype(df[time_col]):
            x_axis = df[time_col]
            x_title = 'Time'
        else:
            x_axis = df[time_col]
            x_title = 'Time Index'
    else:
        x_axis = df.index
        x_title = 'Data Point Index'
    
    # Create battery plot
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=x_axis,
        y=df[battery_col],
        mode='lines',
        name='Battery Level',
        line=dict(color='green', width=2),
        fill='tozeroy',
        fillcolor='rgba(0, 200, 0, 0.2)'
    ))
    
    # Add warning zones
    fig.add_hline(
        y=20,
        line_dash="dash",
        line_color="orange",
        annotation_text="Low Battery Warning"
    )
    
    fig.add_hline(
        y=10,
        line_dash="dash",
        line_color="red",
        annotation_text="Critical Battery"
    )
    
    # Update layout
    fig.update_layout(
        title='UAV Battery Level',
        xaxis_title=x_title,
        yaxis_title='Battery (%)',
        width=800,
        height=400,
        showlegend=False,
        yaxis=dict(range=[0, 100])
    )
    
    return fig


def create_comprehensive_digital_twin(df: pd.DataFrame,
                                    lat_col: str = 'gps_lat',
                                    lon_col: str = 'gps_lon',
                                    alt_col: str = 'altitude_m',
                                    time_col: str = 'timestamp') -> Dict[str, go.Figure]:
    """
    Create a comprehensive digital twin with multiple visualizations.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        lat_col (str): Name of the latitude column
        lon_col (str): Name of the longitude column
        alt_col (str): Name of the altitude column
        time_col (str): Name of the timestamp column
        
    Returns:
        Dict[str, go.Figure]: Dictionary of visualization figures
    """
    visualizations = {}
    
    try:
        # 3D flight path
        visualizations['3d_flight_path'] = create_3d_flight_path(df, lat_col, lon_col, alt_col, time_col)
    except ValueError as e:
        print(f"Could not create 3D flight path: {e}")
    
    try:
        # 2D flight map
        visualizations['2d_flight_map'] = create_2d_flight_map(df, lat_col, lon_col, alt_col, time_col)
    except ValueError as e:
        print(f"Could not create 2D flight map: {e}")
    
    try:
        # Altitude profile
        visualizations['altitude_profile'] = create_altitude_profile(df, alt_col, time_col)
    except ValueError as e:
        print(f"Could not create altitude profile: {e}")
    
    try:
        # Attitude visualization
        visualizations['attitude'] = create_attitude_visualization(df, time_col=time_col)
    except ValueError as e:
        print(f"Could not create attitude visualization: {e}")
    
    try:
        # Speed visualization
        visualizations['speed'] = create_speed_visualization(df, time_col=time_col)
    except ValueError as e:
        print(f"Could not create speed visualization: {e}")
    
    try:
        # Battery visualization
        visualizations['battery'] = create_battery_visualization(df, time_col=time_col)
    except ValueError as e:
        print(f"Could not create battery visualization: {e}")
    
    return visualizations


def export_digital_twin_html(visualizations: Dict[str, go.Figure],
                            output_path: str = 'outputs/digital_twin.html') -> str:
    """
    Export digital twin visualizations to HTML file.
    
    Args:
        visualizations (Dict[str, go.Figure]): Dictionary of visualization figures
        output_path (str): Output file path
        
    Returns:
        str: Path to the generated HTML file
    """
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>UAV Digital Twin</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; }
            .plot-container { margin: 20px 0; }
            h1, h2 { color: #333; }
        </style>
    </head>
    <body>
        <h1>UAV Flight Digital Twin</h1>
    """
    
    for name, fig in visualizations.items():
        html_content += f"""
        <div class="plot-container">
            <h2>{name.replace('_', ' ').title()}</h2>
            {fig.to_html(include_plotlyjs=False, div_id=f"plot_{name}")}
        </div>
        """
    
    html_content += """
    </body>
    </html>
    """
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return output_path


def generate_flight_statistics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Generate comprehensive flight statistics for the digital twin.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        
    Returns:
        Dict[str, Any]: Flight statistics
    """
    stats = {}
    
    # Basic statistics
    stats['total_data_points'] = len(df)
    stats['date_range'] = {
        'start': str(df['timestamp'].min()) if 'timestamp' in df.columns else 'N/A',
        'end': str(df['timestamp'].max()) if 'timestamp' in df.columns else 'N/A'
    }
    
    # GPS statistics
    if 'gps_lat' in df.columns and 'gps_lon' in df.columns:
        stats['gps_bounds'] = {
            'lat_min': float(df['gps_lat'].min()),
            'lat_max': float(df['gps_lat'].max()),
            'lon_min': float(df['gps_lon'].min()),
            'lon_max': float(df['gps_lon'].max()),
            'center_lat': float(df['gps_lat'].mean()),
            'center_lon': float(df['gps_lon'].mean())
        }
    
    # Altitude statistics
    if 'altitude_m' in df.columns:
        stats['altitude'] = {
            'min': float(df['altitude_m'].min()),
            'max': float(df['altitude_m'].max()),
            'mean': float(df['altitude_m'].mean()),
            'range': float(df['altitude_m'].max() - df['altitude_m'].min())
        }
    
    # Speed statistics
    if 'speed_mps' in df.columns:
        stats['speed'] = {
            'min': float(df['speed_mps'].min()),
            'max': float(df['speed_mps'].max()),
            'mean': float(df['speed_mps'].mean()),
            'std': float(df['speed_mps'].std())
        }
    
    # Battery statistics
    if 'battery_percent' in df.columns:
        stats['battery'] = {
            'start': float(df['battery_percent'].iloc[0]),
            'end': float(df['battery_percent'].iloc[-1]),
            'consumed': float(df['battery_percent'].iloc[0] - df['battery_percent'].iloc[-1])
        }
    
    return stats


def create_interactive_dashboard(df: pd.DataFrame,
                                output_path: str = 'outputs/interactive_dashboard.html') -> str:
    """
    Create an interactive dashboard with all visualizations.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        output_path (str): Output file path
        
    Returns:
        str: Path to the generated HTML dashboard
    """
    # Generate all visualizations
    visualizations = create_comprehensive_digital_twin(df)
    
    # Generate statistics
    stats = generate_flight_statistics(df)
    
    # Create dashboard HTML
    dashboard_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>UAV Flight Analysis Dashboard</title>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
            .header {{ background-color: #2c3e50; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
            .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }}
            .stat-card {{ background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .stat-value {{ font-size: 24px; font-weight: bold; color: #3498db; }}
            .stat-label {{ color: #7f8c8d; margin-top: 5px; }}
            .plot-container {{ background-color: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }}
            h2 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🚁 UAV Flight Analysis Dashboard</h1>
            <p>Comprehensive flight data analysis and digital twin visualization</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value">{stats['total_data_points']}</div>
                <div class="stat-label">Total Data Points</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{stats.get('altitude', {}).get('max', 0):.1f} m</div>
                <div class="stat-label">Max Altitude</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{stats.get('speed', {}).get('mean', 0):.1f} m/s</div>
                <div class="stat-label">Average Speed</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{stats.get('battery', {}).get('consumed', 0):.1f}%</div>
                <div class="stat-label">Battery Consumed</div>
            </div>
        </div>
    """
    
    # Add visualizations
    for name, fig in visualizations.items():
        dashboard_html += f"""
        <div class="plot-container">
            <h2>{name.replace('_', ' ').title()}</h2>
            {fig.to_html(include_plotlyjs=False, div_id=f"plot_{name}")}
        </div>
        """
    
    dashboard_html += """
    </body>
    </html>
    """
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(dashboard_html)
    
    return output_path
