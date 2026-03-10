import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from typing import Dict, Any, List, Optional, Tuple
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import os
from datetime import datetime


# Set style
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")


def create_altitude_time_plot(df: pd.DataFrame,
                            alt_col: str = 'altitude_m',
                            time_col: str = 'timestamp',
                            output_path: Optional[str] = None,
                            show_plot: bool = False) -> str:
    """
    Create altitude vs time plot.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        alt_col (str): Name of the altitude column
        time_col (str): Name of the timestamp column
        output_path (str, optional): Path to save the plot
        show_plot (bool): Whether to display the plot
        
    Returns:
        str: Path to the saved plot
    """
    if alt_col not in df.columns:
        raise ValueError(f"Altitude column '{alt_col}' not found")
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Prepare x-axis
    if time_col in df.columns and pd.api.types.is_datetime64_any_dtype(df[time_col]):
        x_data = df[time_col]
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=1))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        x_label = 'Time'
    else:
        x_data = df.index
        x_label = 'Data Point Index'
    
    # Plot altitude
    ax.plot(x_data, df[alt_col], linewidth=2, color='blue', label='Altitude')
    ax.fill_between(x_data, df[alt_col], alpha=0.3, color='blue')
    
    # Add statistics
    max_alt = df[alt_col].max()
    min_alt = df[alt_col].min()
    avg_alt = df[alt_col].mean()
    
    ax.axhline(y=avg_alt, color='red', linestyle='--', alpha=0.7, label=f'Average: {avg_alt:.1f}m')
    
    # Formatting
    ax.set_xlabel(x_label)
    ax.set_ylabel('Altitude (m)')
    ax.set_title('UAV Altitude Profile')
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    # Add statistics text box
    stats_text = f'Max: {max_alt:.1f}m\nMin: {min_alt:.1f}m\nAvg: {avg_alt:.1f}m'
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    
    # Save plot
    if output_path is None:
        output_path = f'outputs/graphs/altitude_profile_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    
    if show_plot:
        plt.show()
    else:
        plt.close()
    
    return output_path


def create_speed_time_plot(df: pd.DataFrame,
                         speed_col: str = 'speed_mps',
                         time_col: str = 'timestamp',
                         output_path: Optional[str] = None,
                         show_plot: bool = False) -> str:
    """
    Create speed vs time plot.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        speed_col (str): Name of the speed column
        time_col (str): Name of the timestamp column
        output_path (str, optional): Path to save the plot
        show_plot (bool): Whether to display the plot
        
    Returns:
        str: Path to the saved plot
    """
    if speed_col not in df.columns:
        raise ValueError(f"Speed column '{speed_col}' not found")
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Prepare x-axis
    if time_col in df.columns and pd.api.types.is_datetime64_any_dtype(df[time_col]):
        x_data = df[time_col]
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        x_label = 'Time'
    else:
        x_data = df.index
        x_label = 'Data Point Index'
    
    # Plot speed
    ax.plot(x_data, df[speed_col], linewidth=2, color='green', label='Speed')
    
    # Add statistics
    max_speed = df[speed_col].max()
    min_speed = df[speed_col].min()
    avg_speed = df[speed_col].mean()
    
    ax.axhline(y=avg_speed, color='red', linestyle='--', alpha=0.7, label=f'Average: {avg_speed:.1f} m/s')
    
    # Formatting
    ax.set_xlabel(x_label)
    ax.set_ylabel('Speed (m/s)')
    ax.set_title('UAV Speed Profile')
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    # Add statistics text box
    stats_text = f'Max: {max_speed:.1f} m/s\nMin: {min_speed:.1f} m/s\nAvg: {avg_speed:.1f} m/s'
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.8))
    
    plt.tight_layout()
    
    # Save plot
    if output_path is None:
        output_path = f'outputs/graphs/speed_profile_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    
    if show_plot:
        plt.show()
    else:
        plt.close()
    
    return output_path


def create_attitude_plots(df: pd.DataFrame,
                        roll_col: str = 'roll_deg',
                        pitch_col: str = 'pitch_deg',
                        yaw_col: str = 'yaw_deg',
                        time_col: str = 'timestamp',
                        output_path: Optional[str] = None,
                        show_plot: bool = False) -> str:
    """
    Create attitude (roll, pitch, yaw) plots.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        roll_col (str): Name of the roll column
        pitch_col (str): Name of the pitch column
        yaw_col (str): Name of the yaw column
        time_col (str): Name of the timestamp column
        output_path (str, optional): Path to save the plot
        show_plot (bool): Whether to display the plot
        
    Returns:
        str: Path to the saved plot
    """
    attitude_cols = {'roll': roll_col, 'pitch': pitch_col, 'yaw': yaw_col}
    available_cols = {name: col for name, col in attitude_cols.items() if col in df.columns}
    
    if not available_cols:
        raise ValueError("No attitude columns found")
    
    # Prepare x-axis
    if time_col in df.columns and pd.api.types.is_datetime64_any_dtype(df[time_col]):
        x_data = df[time_col]
        x_label = 'Time'
        time_format = True
    else:
        x_data = df.index
        x_label = 'Data Point Index'
        time_format = False
    
    # Create subplots
    fig, axes = plt.subplots(len(available_cols), 1, figsize=(12, 3 * len(available_cols)))
    if len(available_cols) == 1:
        axes = [axes]
    
    colors = {'roll': 'red', 'pitch': 'green', 'yaw': 'blue'}
    
    for i, (name, col) in enumerate(available_cols.items()):
        ax = axes[i]
        
        # Plot attitude data
        ax.plot(x_data, df[col], linewidth=2, color=colors.get(name, 'blue'), label=name.capitalize())
        
        # Add zero line
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        
        # Add statistics
        mean_val = df[col].mean()
        std_val = df[col].std()
        
        ax.axhline(y=mean_val, color='red', linestyle='--', alpha=0.7, label=f'Mean: {mean_val:.1f}°')
        
        # Formatting
        ax.set_ylabel(f'{name.capitalize()} (degrees)')
        ax.set_title(f'UAV {name.capitalize()} Angle')
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        # Add statistics text box
        stats_text = f'Mean: {mean_val:.1f}°\nStd: {std_val:.1f}°'
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=9,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor=colors.get(name, 'blue'), alpha=0.3))
        
        if time_format:
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        if i == len(available_cols) - 1:  # Last subplot
            ax.set_xlabel(x_label)
    
    plt.tight_layout()
    
    # Save plot
    if output_path is None:
        output_path = f'outputs/graphs/attitude_profile_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    
    if show_plot:
        plt.show()
    else:
        plt.close()
    
    return output_path


def create_battery_plot(df: pd.DataFrame,
                       battery_col: str = 'battery_percent',
                       time_col: str = 'timestamp',
                       output_path: Optional[str] = None,
                       show_plot: bool = False) -> str:
    """
    Create battery level plot.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        battery_col (str): Name of the battery column
        time_col (str): Name of the timestamp column
        output_path (str, optional): Path to save the plot
        show_plot (bool): Whether to display the plot
        
    Returns:
        str: Path to the saved plot
    """
    if battery_col not in df.columns:
        raise ValueError(f"Battery column '{battery_col}' not found")
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Prepare x-axis
    if time_col in df.columns and pd.api.types.is_datetime64_any_dtype(df[time_col]):
        x_data = df[time_col]
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        x_label = 'Time'
    else:
        x_data = df.index
        x_label = 'Data Point Index'
    
    # Plot battery level
    ax.plot(x_data, df[battery_col], linewidth=2, color='orange', label='Battery Level')
    ax.fill_between(x_data, df[battery_col], alpha=0.3, color='orange')
    
    # Add warning zones
    ax.axhline(y=20, color='red', linestyle='--', alpha=0.7, label='Low Battery Warning')
    ax.axhline(y=10, color='darkred', linestyle='--', alpha=0.7, label='Critical Battery')
    
    # Calculate consumption rate
    if len(df) > 1:
        initial_battery = df[battery_col].iloc[0]
        final_battery = df[battery_col].iloc[-1]
        consumption = initial_battery - final_battery
        
        if time_col in df.columns and pd.api.types.is_datetime64_any_dtype(df[time_col]):
            flight_time = (df[time_col].iloc[-1] - df[time_col].iloc[0]).total_seconds() / 60  # minutes
            consumption_rate = consumption / flight_time if flight_time > 0 else 0
            rate_text = f'Consumption: {consumption_rate:.1f}%/min'
        else:
            rate_text = f'Total Consumption: {consumption:.1f}%'
    else:
        rate_text = 'Insufficient data'
    
    # Formatting
    ax.set_xlabel(x_label)
    ax.set_ylabel('Battery (%)')
    ax.set_title('UAV Battery Level')
    ax.grid(True, alpha=0.3)
    ax.legend()
    ax.set_ylim(0, 100)
    
    # Add statistics text box
    stats_text = f'Start: {initial_battery:.1f}%\nEnd: {final_battery:.1f}%\n{rate_text}'
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.8))
    
    plt.tight_layout()
    
    # Save plot
    if output_path is None:
        output_path = f'outputs/graphs/battery_level_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    
    if show_plot:
        plt.show()
    else:
        plt.close()
    
    return output_path


def create_gps_track_plot(df: pd.DataFrame,
                         lat_col: str = 'gps_lat',
                         lon_col: str = 'gps_lon',
                         alt_col: str = 'altitude_m',
                         output_path: Optional[str] = None,
                         show_plot: bool = False) -> str:
    """
    Create GPS track plot (2D).
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        lat_col (str): Name of the latitude column
        lon_col (str): Name of the longitude column
        alt_col (str): Name of the altitude column for color coding
        output_path (str, optional): Path to save the plot
        show_plot (bool): Whether to display the plot
        
    Returns:
        str: Path to the saved plot
    """
    required_cols = [lat_col, lon_col]
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Prepare data
    plot_data = df[[lat_col, lon_col]].copy()
    plot_data = plot_data.dropna()
    
    if plot_data.empty:
        raise ValueError("No valid GPS data available")
    
    # Determine color coding
    if alt_col and alt_col in df.columns:
        colors = df.loc[plot_data.index, alt_col]
        scatter = ax.scatter(plot_data[lon_col], plot_data[lat_col], 
                          c=colors, cmap='viridis', s=10, alpha=0.7)
        plt.colorbar(scatter, ax=ax, label='Altitude (m)')
    else:
        ax.plot(plot_data[lon_col], plot_data[lat_col], 
               linewidth=2, alpha=0.7, color='blue')
        ax.scatter(plot_data[lon_col], plot_data[lat_col], 
                  s=20, alpha=0.8, color='red', zorder=5)
    
    # Mark start and end points
    if len(plot_data) > 0:
        ax.scatter(plot_data[lon_col].iloc[0], plot_data[lat_col].iloc[0], 
                  s=100, color='green', marker='o', label='Start', zorder=10)
        ax.scatter(plot_data[lon_col].iloc[-1], plot_data[lat_col].iloc[-1], 
                  s=100, color='red', marker='s', label='End', zorder=10)
    
    # Formatting
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_title('UAV GPS Track')
    ax.grid(True, alpha=0.3)
    ax.legend()
    ax.set_aspect('equal', adjustable='box')
    
    # Add statistics
    if len(plot_data) > 1:
        # Calculate total distance
        total_distance = 0
        for i in range(1, len(plot_data)):
            lat1, lon1 = plot_data.iloc[i-1][lat_col], plot_data.iloc[i-1][lon_col]
            lat2, lon2 = plot_data.iloc[i][lat_col], plot_data.iloc[i][lon_col]
            
            # Haversine formula
            lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
            c = 2 * np.arcsin(np.sqrt(a))
            distance = 6371000 * c  # Earth's radius in meters
            total_distance += distance
        
        stats_text = f'Distance: {total_distance/1000:.2f} km\nPoints: {len(plot_data)}'
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    
    plt.tight_layout()
    
    # Save plot
    if output_path is None:
        output_path = f'outputs/graphs/gps_track_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    
    if show_plot:
        plt.show()
    else:
        plt.close()
    
    return output_path


def create_correlation_heatmap(df: pd.DataFrame,
                              columns: Optional[List[str]] = None,
                              output_path: Optional[str] = None,
                              show_plot: bool = False) -> str:
    """
    Create correlation heatmap for flight parameters.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        columns (List[str], optional): Columns to include in correlation
        output_path (str, optional): Path to save the plot
        show_plot (bool): Whether to display the plot
        
    Returns:
        str: Path to the saved plot
    """
    if columns is None:
        # Select numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        # Filter for relevant flight parameters
        relevant_cols = [col for col in numeric_cols if any(keyword in col.lower() 
                        for keyword in ['altitude', 'speed', 'roll', 'pitch', 'yaw', 'battery'])]
        columns = relevant_cols
    
    if not columns:
        raise ValueError("No numeric columns found for correlation analysis")
    
    # Filter available columns
    available_cols = [col for col in columns if col in df.columns]
    
    if len(available_cols) < 2:
        raise ValueError("Need at least 2 columns for correlation analysis")
    
    # Calculate correlation matrix
    corr_matrix = df[available_cols].corr()
    
    # Create heatmap
    fig, ax = plt.subplots(figsize=(10, 8))
    
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0,
                square=True, linewidths=0.5, cbar_kws={"shrink": .8}, ax=ax)
    
    ax.set_title('Flight Parameters Correlation Matrix')
    
    plt.tight_layout()
    
    # Save plot
    if output_path is None:
        output_path = f'outputs/graphs/correlation_heatmap_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    
    if show_plot:
        plt.show()
    else:
        plt.close()
    
    return output_path


def create_flight_phase_visualization(df: pd.DataFrame,
                                    phases: List[Dict],
                                    alt_col: str = 'altitude_m',
                                    time_col: str = 'timestamp',
                                    output_path: Optional[str] = None,
                                    show_plot: bool = False) -> str:
    """
    Create visualization with flight phases highlighted.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        phases (List[Dict]): List of flight phases
        alt_col (str): Name of the altitude column
        time_col (str): Name of the timestamp column
        output_path (str, optional): Path to save the plot
        show_plot (bool): Whether to display the plot
        
    Returns:
        str: Path to the saved plot
    """
    if alt_col not in df.columns:
        raise ValueError(f"Altitude column '{alt_col}' not found")
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Prepare x-axis
    if time_col in df.columns and pd.api.types.is_datetime64_any_dtype(df[time_col]):
        x_data = df[time_col]
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        x_label = 'Time'
    else:
        x_data = df.index
        x_label = 'Data Point Index'
    
    # Plot altitude
    ax.plot(x_data, df[alt_col], linewidth=2, color='blue', alpha=0.7)
    
    # Color map for phases
    phase_colors = {
        'takeoff': 'green',
        'climb': 'lightblue',
        'cruise': 'yellow',
        'descent': 'orange',
        'landing': 'red',
        'ground': 'gray',
        'stationary': 'gray',
        'moving': 'lightgreen'
    }
    
    # Highlight phases
    for phase in phases:
        start_idx = phase['start_index']
        end_idx = phase['end_index']
        phase_name = phase['phase']
        
        if start_idx < len(df) and end_idx < len(df):
            if time_col in df.columns and pd.api.types.is_datetime64_any_dtype(df[time_col]):
                start_time = df.loc[start_idx, time_col]
                end_time = df.loc[end_idx, time_col]
                ax.axvspan(start_time, end_time, alpha=0.3, 
                          color=phase_colors.get(phase_name, 'lightgray'),
                          label=phase_name if phase_name not in [p['phase'] for p in phases[:phases.index(phase)]] else '')
            else:
                ax.axvspan(start_idx, end_idx, alpha=0.3,
                          color=phase_colors.get(phase_name, 'lightgray'),
                          label=phase_name if phase_name not in [p['phase'] for p in phases[:phases.index(phase)]] else '')
    
    # Formatting
    ax.set_xlabel(x_label)
    ax.set_ylabel('Altitude (m)')
    ax.set_title('UAV Flight Phases')
    ax.grid(True, alpha=0.3)
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    
    plt.tight_layout()
    
    # Save plot
    if output_path is None:
        output_path = f'outputs/graphs/flight_phases_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    
    if show_plot:
        plt.show()
    else:
        plt.close()
    
    return output_path


def create_comprehensive_flight_plots(df: pd.DataFrame,
                                    phases: Optional[List[Dict]] = None,
                                    output_dir: str = 'outputs/graphs') -> Dict[str, str]:
    """
    Create all standard flight plots.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        phases (List[Dict], optional): Flight phases for visualization
        output_dir (str): Output directory for plots
        
    Returns:
        Dict[str, str]: Dictionary mapping plot names to file paths
    """
    plot_paths = {}
    
    try:
        plot_paths['altitude'] = create_altitude_time_plot(df, output_path=f'{output_dir}/altitude.png')
    except ValueError as e:
        print(f"Could not create altitude plot: {e}")
    
    try:
        plot_paths['speed'] = create_speed_time_plot(df, output_path=f'{output_dir}/speed.png')
    except ValueError as e:
        print(f"Could not create speed plot: {e}")
    
    try:
        plot_paths['attitude'] = create_attitude_plots(df, output_path=f'{output_dir}/attitude.png')
    except ValueError as e:
        print(f"Could not create attitude plot: {e}")
    
    try:
        plot_paths['battery'] = create_battery_plot(df, output_path=f'{output_dir}/battery.png')
    except ValueError as e:
        print(f"Could not create battery plot: {e}")
    
    try:
        plot_paths['gps_track'] = create_gps_track_plot(df, output_path=f'{output_dir}/gps_track.png')
    except ValueError as e:
        print(f"Could not create GPS track plot: {e}")
    
    try:
        plot_paths['correlation'] = create_correlation_heatmap(df, output_path=f'{output_dir}/correlation.png')
    except ValueError as e:
        print(f"Could not create correlation heatmap: {e}")
    
    if phases:
        try:
            plot_paths['phases'] = create_flight_phase_visualization(df, phases, output_path=f'{output_dir}/phases.png')
        except ValueError as e:
            print(f"Could not create flight phases plot: {e}")
    
    return plot_paths


def create_anomaly_visualization(df: pd.DataFrame,
                               anomalies: Dict[str, Any],
                               output_path: Optional[str] = None,
                               show_plot: bool = False) -> str:
    """
    Create visualization highlighting detected anomalies.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        anomalies (Dict[str, Any]): Anomaly detection results
        output_path (str, optional): Path to save the plot
        show_plot (bool): Whether to display the plot
        
    Returns:
        str: Path to the saved plot
    """
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    axes = axes.flatten()
    
    # Time axis
    if 'timestamp' in df.columns and pd.api.types.is_datetime64_any_dtype(df['timestamp']):
        x_data = df['timestamp']
        time_format = True
    else:
        x_data = df.index
        time_format = False
    
    plot_idx = 0
    
    # Altitude anomalies
    if 'altitude' in anomalies['categories'] and anomalies['categories']['altitude']['anomalies']:
        ax = axes[plot_idx]
        ax.plot(x_data, df['altitude_m'], color='blue', alpha=0.7, label='Altitude')
        
        for anomaly in anomalies['categories']['altitude']['anomalies']:
            idx = anomaly['index']
            if idx < len(df):
                ax.scatter(x_data[idx], df.loc[idx, 'altitude_m'], 
                          color='red', s=50, zorder=5)
        
        ax.set_title('Altitude Anomalies')
        ax.set_ylabel('Altitude (m)')
        ax.grid(True, alpha=0.3)
        plot_idx += 1
    
    # Attitude anomalies
    if 'attitude' in anomalies['categories'] and anomalies['categories']['attitude']['anomalies']:
        ax = axes[plot_idx]
        
        # Plot roll as example
        if 'roll_deg' in df.columns:
            ax.plot(x_data, df['roll_deg'], color='green', alpha=0.7, label='Roll')
            
            for anomaly in anomalies['categories']['attitude']['anomalies']:
                if 'roll' in anomaly['type']:
                    idx = anomaly['index']
                    if idx < len(df):
                        ax.scatter(x_data[idx], df.loc[idx, 'roll_deg'], 
                                  color='red', s=50, zorder=5)
        
        ax.set_title('Attitude Anomalies')
        ax.set_ylabel('Roll (degrees)')
        ax.grid(True, alpha=0.3)
        plot_idx += 1
    
    # Speed anomalies
    if 'speed' in anomalies['categories'] and anomalies['categories']['speed']['anomalies']:
        ax = axes[plot_idx]
        ax.plot(x_data, df['speed_mps'], color='orange', alpha=0.7, label='Speed')
        
        for anomaly in anomalies['categories']['speed']['anomalies']:
            idx = anomaly['index']
            if idx < len(df):
                ax.scatter(x_data[idx], df.loc[idx, 'speed_mps'], 
                          color='red', s=50, zorder=5)
        
        ax.set_title('Speed Anomalies')
        ax.set_ylabel('Speed (m/s)')
        ax.grid(True, alpha=0.3)
        plot_idx += 1
    
    # Battery anomalies
    if 'battery' in anomalies['categories'] and anomalies['categories']['battery']['anomalies']:
        ax = axes[plot_idx]
        ax.plot(x_data, df['battery_percent'], color='purple', alpha=0.7, label='Battery')
        
        for anomaly in anomalies['categories']['battery']['anomalies']:
            idx = anomaly['index']
            if idx < len(df):
                ax.scatter(x_data[idx], df.loc[idx, 'battery_percent'], 
                          color='red', s=50, zorder=5)
        
        ax.set_title('Battery Anomalies')
        ax.set_ylabel('Battery (%)')
        ax.set_ylim(0, 100)
        ax.grid(True, alpha=0.3)
        plot_idx += 1
    
    # Format time axis
    if time_format:
        for i in range(plot_idx):
            axes[i].xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
            plt.setp(axes[i].xaxis.get_majorticklabels(), rotation=45)
    
    # Hide unused subplots
    for i in range(plot_idx, len(axes)):
        axes[i].set_visible(False)
    
    plt.suptitle(f'Flight Anomalies (Total: {anomalies["summary"]["total_anomalies"]})', fontsize=16)
    plt.tight_layout()
    
    # Save plot
    if output_path is None:
        output_path = f'outputs/graphs/anomalies_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    
    if show_plot:
        plt.show()
    else:
        plt.close()
    
    return output_path
