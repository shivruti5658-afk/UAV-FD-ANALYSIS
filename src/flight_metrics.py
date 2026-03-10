import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple
from scipy import stats


def calculate_flight_duration(df: pd.DataFrame, time_col: str = 'timestamp') -> Dict[str, float]:
    """
    Calculate flight duration in different units.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        time_col (str): Name of the timestamp column
        
    Returns:
        Dict[str, float]: Flight duration in seconds, minutes, and hours
    """
    if time_col not in df.columns:
        return {'seconds': 0, 'minutes': 0, 'hours': 0}
    
    # Ensure timestamp is datetime
    if not pd.api.types.is_datetime64_any_dtype(df[time_col]):
        df[time_col] = pd.to_datetime(df[time_col])
    
    duration_seconds = (df[time_col].max() - df[time_col].min()).total_seconds()
    
    return {
        'seconds': duration_seconds,
        'minutes': duration_seconds / 60,
        'hours': duration_seconds / 3600
    }


def calculate_max_altitude(df: pd.DataFrame, alt_col: str = 'altitude_m') -> Dict[str, float]:
    """
    Calculate altitude statistics.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        alt_col (str): Name of the altitude column
        
    Returns:
        Dict[str, float]: Altitude statistics
    """
    if alt_col not in df.columns:
        return {'max_altitude': 0, 'min_altitude': 0, 'avg_altitude': 0, 'altitude_range': 0}
    
    max_alt = df[alt_col].max()
    min_alt = df[alt_col].min()
    avg_alt = df[alt_col].mean()
    altitude_range = max_alt - min_alt
    
    return {
        'max_altitude': float(max_alt),
        'min_altitude': float(min_alt),
        'avg_altitude': float(avg_alt),
        'altitude_range': float(altitude_range)
    }


def calculate_speed_statistics(df: pd.DataFrame, speed_col: str = 'speed_mps') -> Dict[str, float]:
    """
    Calculate speed statistics.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        speed_col (str): Name of the speed column
        
    Returns:
        Dict[str, float]: Speed statistics
    """
    if speed_col not in df.columns:
        return {
            'avg_speed': 0, 'max_speed': 0, 'min_speed': 0, 
            'speed_std': 0, 'speed_variance': 0
        }
    
    avg_speed = df[speed_col].mean()
    max_speed = df[speed_col].max()
    min_speed = df[speed_col].min()
    speed_std = df[speed_col].std()
    speed_variance = df[speed_col].var()
    
    return {
        'avg_speed': float(avg_speed),
        'max_speed': float(max_speed),
        'min_speed': float(min_speed),
        'speed_std': float(speed_std),
        'speed_variance': float(speed_variance)
    }


def calculate_climb_descent_rates(df: pd.DataFrame, alt_col: str = 'altitude_m', 
                                time_col: str = 'time_elapsed') -> Dict[str, float]:
    """
    Calculate climb and descent rates.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        alt_col (str): Name of the altitude column
        time_col (str): Name of the time elapsed column
        
    Returns:
        Dict[str, float]: Climb and descent rates
    """
    if alt_col not in df.columns or time_col not in df.columns:
        return {'max_climb_rate': 0, 'max_descent_rate': 0, 'avg_vertical_speed': 0}
    
    # Calculate vertical speed (altitude change rate)
    if time_col in df.columns and pd.api.types.is_datetime64_any_dtype(df[time_col]):
        time_diff = df[time_col].diff().dt.total_seconds()
    else:
        time_diff = df[time_col].diff()
    
    # Avoid division by zero
    time_diff_safe = time_diff.replace(0, np.nan)
    df['vertical_speed'] = df[alt_col].diff() / time_diff_safe
    
    # Separate climb and descent rates
    climb_rates = df[df['vertical_speed'] > 0]['vertical_speed']
    descent_rates = df[df['vertical_speed'] < 0]['vertical_speed']
    
    max_climb_rate = climb_rates.max() if not climb_rates.empty else 0
    max_descent_rate = abs(descent_rates.min()) if not descent_rates.empty else 0
    avg_vertical_speed = df['vertical_speed'].mean()
    
    return {
        'max_climb_rate': float(max_climb_rate),
        'max_descent_rate': float(max_descent_rate),
        'avg_vertical_speed': float(avg_vertical_speed)
    }


def calculate_distance_traveled(df: pd.DataFrame, lat_col: str = 'gps_lat', 
                               lon_col: str = 'gps_lon') -> Dict[str, float]:
    """
    Calculate total distance traveled using GPS coordinates.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        lat_col (str): Name of the latitude column
        lon_col (str): Name of the longitude column
        
    Returns:
        Dict[str, float]: Distance statistics
    """
    if lat_col not in df.columns or lon_col not in df.columns:
        return {'total_distance_m': 0, 'total_distance_km': 0}
    
    # Calculate distance between consecutive points using Haversine formula
    distances = []
    
    for i in range(1, len(df)):
        lat1, lon1 = df.iloc[i-1][lat_col], df.iloc[i-1][lon_col]
        lat2, lon2 = df.iloc[i][lat_col], df.iloc[i][lon_col]
        
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        
        # Earth's radius in meters
        distance = 6371000 * c
        distances.append(distance)
    
    total_distance_m = sum(distances)
    total_distance_km = total_distance_m / 1000
    
    return {
        'total_distance_m': float(total_distance_m),
        'total_distance_km': float(total_distance_km)
    }


def calculate_attitude_statistics(df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
    """
    Calculate attitude (roll, pitch, yaw) statistics.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        
    Returns:
        Dict[str, Dict[str, float]]: Statistics for each attitude component
    """
    attitude_cols = ['roll_deg', 'pitch_deg', 'yaw_deg']
    results = {}
    
    for col in attitude_cols:
        if col in df.columns:
            stats_dict = {
                'mean': float(df[col].mean()),
                'std': float(df[col].std()),
                'min': float(df[col].min()),
                'max': float(df[col].max()),
                'range': float(df[col].max() - df[col].min())
            }
            results[col] = stats_dict
        else:
            results[col] = {'mean': 0, 'std': 0, 'min': 0, 'max': 0, 'range': 0}
    
    return results


def calculate_flight_efficiency(df: pd.DataFrame, alt_col: str = 'altitude_m', 
                               speed_col: str = 'speed_mps', 
                               battery_col: str = 'battery_percent') -> Dict[str, float]:
    """
    Calculate flight efficiency metrics.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        alt_col (str): Name of the altitude column
        speed_col (str): Name of the speed column
        battery_col (str): Name of the battery column
        
    Returns:
        Dict[str, float]: Flight efficiency metrics
    """
    efficiency_metrics = {}
    
    # Altitude efficiency (altitude gained per battery percentage)
    if alt_col in df.columns and battery_col in df.columns:
        altitude_gain = df[alt_col].max() - df[alt_col].min()
        battery_used = df[battery_col].iloc[0] - df[battery_col].iloc[-1]
        if battery_used > 0:
            efficiency_metrics['altitude_per_battery'] = altitude_gain / battery_used
        else:
            efficiency_metrics['altitude_per_battery'] = 0
    
    # Speed efficiency (average speed per battery percentage)
    if speed_col in df.columns and battery_col in df.columns:
        avg_speed = df[speed_col].mean()
        battery_used = df[battery_col].iloc[0] - df[battery_col].iloc[-1]
        if battery_used > 0:
            efficiency_metrics['speed_per_battery'] = avg_speed / battery_used
        else:
            efficiency_metrics['speed_per_battery'] = 0
    
    # Distance efficiency (distance per battery percentage)
    if battery_col in df.columns:
        distance_metrics = calculate_distance_traveled(df)
        battery_used = df[battery_col].iloc[0] - df[battery_col].iloc[-1]
        if battery_used > 0:
            efficiency_metrics['distance_per_battery'] = distance_metrics['total_distance_m'] / battery_used
        else:
            efficiency_metrics['distance_per_battery'] = 0
    
    return efficiency_metrics


def calculate_all_flight_metrics(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Calculate all flight metrics in one comprehensive function.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        
    Returns:
        Dict[str, Any]: Comprehensive flight metrics
    """
    metrics = {}
    
    # Basic flight metrics
    metrics['flight_duration'] = calculate_flight_duration(df)
    metrics['altitude_stats'] = calculate_max_altitude(df)
    metrics['speed_stats'] = calculate_speed_statistics(df)
    metrics['climb_descent_rates'] = calculate_climb_descent_rates(df)
    metrics['distance_traveled'] = calculate_distance_traveled(df)
    metrics['attitude_stats'] = calculate_attitude_statistics(df)
    metrics['flight_efficiency'] = calculate_flight_efficiency(df)
    
    # Additional derived metrics
    if 'timestamp' in df.columns:
        metrics['data_points'] = len(df)
        metrics['sampling_rate'] = len(df) / metrics['flight_duration']['seconds'] if metrics['flight_duration']['seconds'] > 0 else 0
    
    return metrics


def format_flight_summary(metrics: Dict[str, Any]) -> str:
    """
    Format flight metrics into a readable summary.
    
    Args:
        metrics (Dict[str, Any]): Flight metrics dictionary
        
    Returns:
        str: Formatted flight summary
    """
    summary = []
    
    # Flight duration
    duration = metrics['flight_duration']
    summary.append(f"Flight Duration: {duration['minutes']:.1f} minutes")
    
    # Altitude
    altitude = metrics['altitude_stats']
    summary.append(f"Max Altitude: {altitude['max_altitude']:.1f} m")
    summary.append(f"Altitude Range: {altitude['altitude_range']:.1f} m")
    
    # Speed
    speed = metrics['speed_stats']
    summary.append(f"Average Speed: {speed['avg_speed']:.1f} m/s")
    summary.append(f"Max Speed: {speed['max_speed']:.1f} m/s")
    
    # Climb/Descent
    rates = metrics['climb_descent_rates']
    summary.append(f"Max Climb Rate: {rates['max_climb_rate']:.1f} m/s")
    summary.append(f"Max Descent Rate: {rates['max_descent_rate']:.1f} m/s")
    
    # Distance
    distance = metrics['distance_traveled']
    summary.append(f"Total Distance: {distance['total_distance_km']:.2f} km")
    
    return "\n".join(summary)
