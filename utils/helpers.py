import pandas as pd
import numpy as np
import os
import json
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
import logging
import sys


def setup_logging(log_level: str = 'INFO', log_file: Optional[str] = None) -> logging.Logger:
    """
    Set up logging configuration.
    
    Args:
        log_level (str): Logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR')
        log_file (str, optional): Path to log file
        
    Returns:
        logging.Logger: Configured logger
    """
    logger = logging.getLogger('uav_flight_analysis')
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def validate_file_path(file_path: str) -> bool:
    """
    Validate if a file path exists and is accessible.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        bool: True if file exists and is accessible
    """
    if not os.path.exists(file_path):
        return False
    
    if not os.path.isfile(file_path):
        return False
    
    if not os.access(file_path, os.R_OK):
        return False
    
    return True


def create_output_directory(base_path: str, subdirectory: str = '') -> str:
    """
    Create output directory if it doesn't exist.
    
    Args:
        base_path (str): Base path for output
        subdirectory (str): Subdirectory to create
        
    Returns:
        str: Full path to created directory
    """
    full_path = os.path.join(base_path, subdirectory) if subdirectory else base_path
    os.makedirs(full_path, exist_ok=True)
    return full_path


def save_json(data: Dict[str, Any], file_path: str) -> bool:
    """
    Save data to JSON file.
    
    Args:
        data (Dict[str, Any]): Data to save
        file_path (str): Path to save file
        
    Returns:
        bool: True if successful
    """
    try:
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        return True
    except Exception as e:
        logging.error(f"Error saving JSON to {file_path}: {str(e)}")
        return False


def load_json(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Load data from JSON file.
    
    Args:
        file_path (str): Path to JSON file
        
    Returns:
        Optional[Dict[str, Any]]: Loaded data or None if error
    """
    try:
        if not validate_file_path(file_path):
            return None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading JSON from {file_path}: {str(e)}")
        return None


def format_bytes(bytes_value: int) -> str:
    """
    Format bytes in human-readable format.
    
    Args:
        bytes_value (int): Number of bytes
        
    Returns:
        str: Formatted string
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"


def format_duration(seconds: float) -> str:
    """
    Format duration in human-readable format.
    
    Args:
        seconds (float): Duration in seconds
        
    Returns:
        str: Formatted duration string
    """
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} hours"


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate distance between two GPS coordinates using Haversine formula.
    
    Args:
        lat1 (float): Latitude of point 1
        lon1 (float): Longitude of point 1
        lat2 (float): Latitude of point 2
        lon2 (float): Longitude of point 2
        
    Returns:
        float: Distance in meters
    """
    # Convert to radians
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    
    # Earth's radius in meters
    return 6371000 * c


def smooth_data(data: np.ndarray, window_size: int = 5, method: str = 'moving_average') -> np.ndarray:
    """
    Apply smoothing to data array.
    
    Args:
        data (np.ndarray): Input data array
        window_size (int): Window size for smoothing
        method (str): Smoothing method ('moving_average', 'exponential')
        
    Returns:
        np.ndarray: Smoothed data array
    """
    if method == 'moving_average':
        return np.convolve(data, np.ones(window_size)/window_size, mode='same')
    elif method == 'exponential':
        alpha = 2.0 / (window_size + 1)
        smoothed = np.zeros_like(data)
        smoothed[0] = data[0]
        for i in range(1, len(data)):
            smoothed[i] = alpha * data[i] + (1 - alpha) * smoothed[i-1]
        return smoothed
    else:
        raise ValueError(f"Unknown smoothing method: {method}")


def detect_outliers_iqr(data: np.ndarray, multiplier: float = 1.5) -> np.ndarray:
    """
    Detect outliers using IQR method.
    
    Args:
        data (np.ndarray): Input data array
        multiplier (float): IQR multiplier for outlier detection
        
    Returns:
        np.ndarray: Boolean array indicating outliers
    """
    Q1 = np.percentile(data, 25)
    Q3 = np.percentile(data, 75)
    IQR = Q3 - Q1
    
    lower_bound = Q1 - multiplier * IQR
    upper_bound = Q3 + multiplier * IQR
    
    return (data < lower_bound) | (data > upper_bound)


def detect_outliers_zscore(data: np.ndarray, threshold: float = 3.0) -> np.ndarray:
    """
    Detect outliers using Z-score method.
    
    Args:
        data (np.ndarray): Input data array
        threshold (float): Z-score threshold for outlier detection
        
    Returns:
        np.ndarray: Boolean array indicating outliers
    """
    z_scores = np.abs((data - np.mean(data)) / np.std(data))
    return z_scores > threshold


def interpolate_missing_values(data: np.ndarray, method: str = 'linear') -> np.ndarray:
    """
    Interpolate missing values in data array.
    
    Args:
        data (np.ndarray): Input data array with NaN values
        method (str): Interpolation method ('linear', 'cubic', 'nearest')
        
    Returns:
        np.ndarray: Data array with interpolated values
    """
    if not np.any(np.isnan(data)):
        return data
    
    # Get indices of non-NaN values
    valid_indices = ~np.isnan(data)
    
    if np.sum(valid_indices) < 2:
        return data  # Not enough points for interpolation
    
    # Interpolate
    if method == 'linear':
        return np.interp(np.arange(len(data)), np.arange(len(data))[valid_indices], data[valid_indices])
    else:
        from scipy import interpolate
        if method == 'cubic':
            interp_func = interpolate.interp1d(
                np.arange(len(data))[valid_indices], 
                data[valid_indices], 
                kind='cubic', 
                fill_value='extrapolate'
            )
        elif method == 'nearest':
            interp_func = interpolate.interp1d(
                np.arange(len(data))[valid_indices], 
                data[valid_indices], 
                kind='nearest', 
                fill_value='extrapolate'
            )
        else:
            raise ValueError(f"Unknown interpolation method: {method}")
        
        return interp_func(np.arange(len(data)))


def normalize_angle(angle: float) -> float:
    """
    Normalize angle to [-180, 180] range.
    
    Args:
        angle (float): Input angle in degrees
        
    Returns:
        float: Normalized angle
    """
    while angle > 180:
        angle -= 360
    while angle < -180:
        angle += 360
    return angle


def calculate_sampling_rate(timestamps: pd.Series) -> float:
    """
    Calculate sampling rate from timestamps.
    
    Args:
        timestamps (pd.Series): Timestamp series
        
    Returns:
        float: Sampling rate in Hz
    """
    if len(timestamps) < 2:
        return 0.0
    
    # Convert to datetime if not already
    if not pd.api.types.is_datetime64_any_dtype(timestamps):
        timestamps = pd.to_datetime(timestamps)
    
    # Calculate time differences
    time_diffs = timestamps.diff().dropna()
    
    # Convert to seconds
    if pd.api.types.is_timedelta64_dtype(time_diffs):
        time_diffs_seconds = time_diffs.dt.total_seconds()
    else:
        time_diffs_seconds = time_diffs
    
    # Calculate average sampling rate
    avg_interval = time_diffs_seconds.mean()
    
    if avg_interval > 0:
        return 1.0 / avg_interval
    else:
        return 0.0


def generate_timestamps(start_time: datetime, duration_seconds: float, sampling_rate: float) -> List[datetime]:
    """
    Generate timestamps for synthetic data.
    
    Args:
        start_time (datetime): Start time
        duration_seconds (float): Duration in seconds
        sampling_rate (float): Sampling rate in Hz
        
    Returns:
        List[datetime]: List of timestamps
    """
    num_samples = int(duration_seconds * sampling_rate)
    interval = timedelta(seconds=1.0 / sampling_rate)
    
    timestamps = []
    current_time = start_time
    
    for _ in range(num_samples):
        timestamps.append(current_time)
        current_time += interval
    
    return timestamps


def create_synthetic_flight_data(
    duration_seconds: float = 600,
    sampling_rate: float = 10.0,
    start_altitude: float = 0.0,
    max_altitude: float = 150.0,
    cruise_speed: float = 12.0,
    start_lat: float = 40.0,
    start_lon: float = -74.0
) -> pd.DataFrame:
    """
    Create synthetic UAV flight data for testing.
    
    Args:
        duration_seconds (float): Flight duration in seconds
        sampling_rate (float): Sampling rate in Hz
        start_altitude (float): Starting altitude in meters
        max_altitude (float): Maximum altitude in meters
        cruise_speed (float): Cruise speed in m/s
        start_lat (float): Starting latitude
        start_lon (float): Starting longitude
        
    Returns:
        pd.DataFrame: Synthetic flight data
    """
    num_samples = int(duration_seconds * sampling_rate)
    
    # Generate timestamps
    start_time = datetime.now()
    timestamps = generate_timestamps(start_time, duration_seconds, sampling_rate)
    
    # Generate flight phases (takeoff, climb, cruise, descent, landing)
    phase_times = {
        'takeoff': (0, 0.1 * duration_seconds),
        'climb': (0.1 * duration_seconds, 0.3 * duration_seconds),
        'cruise': (0.3 * duration_seconds, 0.7 * duration_seconds),
        'descent': (0.7 * duration_seconds, 0.9 * duration_seconds),
        'landing': (0.9 * duration_seconds, duration_seconds)
    }
    
    # Initialize data arrays
    altitude = np.zeros(num_samples)
    speed = np.zeros(num_samples)
    roll = np.zeros(num_samples)
    pitch = np.zeros(num_samples)
    yaw = np.zeros(num_samples)
    battery = np.zeros(num_samples)
    lat = np.zeros(num_samples)
    lon = np.zeros(num_samples)
    
    for i, t in enumerate(np.linspace(0, duration_seconds, num_samples)):
        # Determine current phase
        current_phase = None
        for phase, (start, end) in phase_times.items():
            if start <= t < end:
                current_phase = phase
                break
        
        # Generate data based on phase
        if current_phase == 'takeoff':
            progress = t / (0.1 * duration_seconds)
            altitude[i] = start_altitude + progress * 10
            speed[i] = cruise_speed * progress
            roll[i] = np.random.normal(0, 2)
            pitch[i] = np.random.normal(5, 3)
            yaw[i] = np.random.normal(0, 5)
            
        elif current_phase == 'climb':
            progress = (t - 0.1 * duration_seconds) / (0.2 * duration_seconds)
            altitude[i] = 10 + progress * (max_altitude - 10)
            speed[i] = cruise_speed * (0.5 + 0.5 * progress)
            roll[i] = np.random.normal(0, 3)
            pitch[i] = np.random.normal(10, 2)
            yaw[i] = np.random.normal(0, 3)
            
        elif current_phase == 'cruise':
            altitude[i] = max_altitude + np.random.normal(0, 2)
            speed[i] = cruise_speed + np.random.normal(0, 1)
            roll[i] = np.random.normal(0, 1)
            pitch[i] = np.random.normal(0, 1)
            yaw[i] = np.random.normal(0, 2)
            
        elif current_phase == 'descent':
            progress = (t - 0.7 * duration_seconds) / (0.2 * duration_seconds)
            altitude[i] = max_altitude - progress * (max_altitude - 10)
            speed[i] = cruise_speed * (1 - 0.5 * progress)
            roll[i] = np.random.normal(0, 3)
            pitch[i] = np.random.normal(-10, 2)
            yaw[i] = np.random.normal(0, 3)
            
        elif current_phase == 'landing':
            progress = (t - 0.9 * duration_seconds) / (0.1 * duration_seconds)
            altitude[i] = 10 - progress * 10
            speed[i] = cruise_speed * 0.5 * (1 - progress)
            roll[i] = np.random.normal(0, 2)
            pitch[i] = np.random.normal(-5, 3)
            yaw[i] = np.random.normal(0, 5)
        
        # Battery (linear discharge)
        battery[i] = 100 - (t / duration_seconds) * 25  # 25% battery usage
        
        # GPS (simple circular pattern)
        if current_phase in ['cruise', 'climb', 'descent']:
            angle = (t / duration_seconds) * 2 * np.pi
            radius = 0.001  # Small circle in degrees
            lat[i] = start_lat + radius * np.cos(angle)
            lon[i] = start_lon + radius * np.sin(angle)
        else:
            lat[i] = start_lat
            lon[i] = start_lon
    
    # Add some noise and anomalies
    noise_level = 0.1
    altitude += np.random.normal(0, noise_level, num_samples)
    speed += np.random.normal(0, noise_level, num_samples)
    roll += np.random.normal(0, noise_level, num_samples)
    pitch += np.random.normal(0, noise_level, num_samples)
    yaw += np.random.normal(0, noise_level, num_samples)
    
    # Add a few anomalies
    anomaly_indices = np.random.choice(num_samples, size=min(5, num_samples//100), replace=False)
    for idx in anomaly_indices:
        altitude[idx] += np.random.normal(0, 20)
        roll[idx] += np.random.normal(0, 15)
    
    # Create DataFrame
    df = pd.DataFrame({
        'timestamp': timestamps,
        'altitude_m': altitude,
        'speed_mps': speed,
        'roll_deg': roll,
        'pitch_deg': pitch,
        'yaw_deg': yaw,
        'battery_percent': battery,
        'gps_lat': lat,
        'gps_lon': lon
    })
    
    return df


def validate_flight_data_structure(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Validate the structure and quality of flight data.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        
    Returns:
        Dict[str, Any]: Validation results
    """
    validation_results = {
        'is_valid': True,
        'errors': [],
        'warnings': [],
        'info': {}
    }
    
    # Check required columns
    required_columns = [
        'timestamp', 'altitude_m', 'speed_mps', 'roll_deg', 
        'pitch_deg', 'yaw_deg', 'battery_percent', 'gps_lat', 'gps_lon'
    ]
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        validation_results['errors'].append(f"Missing required columns: {missing_columns}")
        validation_results['is_valid'] = False
    
    # Check data types
    if 'timestamp' in df.columns:
        if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
            try:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                validation_results['warnings'].append("Timestamp column converted to datetime")
            except:
                validation_results['errors'].append("Cannot convert timestamp to datetime")
                validation_results['is_valid'] = False
    
    # Check for missing values
    missing_value_counts = df.isnull().sum()
    high_missing_cols = missing_value_counts[missing_value_counts > len(df) * 0.1].index.tolist()
    if high_missing_cols:
        validation_results['warnings'].append(f"High missing values in columns: {high_missing_cols}")
    
    # Check data ranges
    range_checks = {
        'altitude_m': (-100, 10000),
        'speed_mps': (0, 100),
        'roll_deg': (-180, 180),
        'pitch_deg': (-90, 90),
        'yaw_deg': (-180, 180),
        'battery_percent': (0, 100),
        'gps_lat': (-90, 90),
        'gps_lon': (-180, 180)
    }
    
    for col, (min_val, max_val) in range_checks.items():
        if col in df.columns:
            out_of_range = df[(df[col] < min_val) | (df[col] > max_val)]
            if not out_of_range.empty:
                validation_results['warnings'].append(f"Out of range values in {col}: {len(out_of_range)} records")
    
    # Dataset info
    validation_results['info'] = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'missing_values': df.isnull().sum().sum(),
        'data_completeness': (1 - df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
    }
    
    return validation_results


def get_system_info() -> Dict[str, Any]:
    """
    Get system information for debugging and reporting.
    
    Returns:
        Dict[str, Any]: System information
    """
    import platform
    import sys
    
    return {
        'platform': platform.platform(),
        'python_version': sys.version,
        'working_directory': os.getcwd(),
        'script_directory': os.path.dirname(os.path.abspath(__file__)),
        'timestamp': datetime.now().isoformat()
    }


def create_backup(file_path: str, backup_dir: str = 'backups') -> Optional[str]:
    """
    Create a backup of a file.
    
    Args:
        file_path (str): Path to file to backup
        backup_dir (str): Backup directory
        
    Returns:
        Optional[str]: Path to backup file or None if failed
    """
    try:
        if not validate_file_path(file_path):
            return None
        
        # Create backup directory
        os.makedirs(backup_dir, exist_ok=True)
        
        # Generate backup filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = os.path.basename(file_path)
        backup_path = os.path.join(backup_dir, f"{timestamp}_{filename}")
        
        # Copy file
        import shutil
        shutil.copy2(file_path, backup_path)
        
        return backup_path
    
    except Exception as e:
        logging.error(f"Error creating backup of {file_path}: {str(e)}")
        return None


def clean_old_files(directory: str, max_age_days: int = 30, pattern: str = '*') -> int:
    """
    Clean old files from a directory.
    
    Args:
        directory (str): Directory to clean
        max_age_days (int): Maximum age in days
        pattern (str): File pattern to match
        
    Returns:
        int: Number of files deleted
    """
    import glob
    
    if not os.path.exists(directory):
        return 0
    
    deleted_count = 0
    cutoff_time = datetime.now() - timedelta(days=max_age_days)
    
    for file_path in glob.glob(os.path.join(directory, pattern)):
        try:
            file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            if file_time < cutoff_time:
                os.remove(file_path)
                deleted_count += 1
        except Exception as e:
            logging.error(f"Error deleting file {file_path}: {str(e)}")
    
    return deleted_count


# Constants
DEFAULT_CONFIG = {
    'preprocessing': {
        'missing_strategy': 'interpolate',
        'smoothing_method': 'savgol',
        'smoothing_window': 5,
        'outlier_method': 'iqr',
        'outlier_threshold': 1.5
    },
    'anomaly_detection': {
        'threshold_std': 3.0,
        'min_anomaly_severity': 'medium'
    },
    'phase_detection': {
        'climb_threshold': 0.5,
        'descent_threshold': -0.5,
        'stationary_threshold': 2.0,
        'min_phase_duration': 5,
        'n_clusters': 5
    },
    'visualization': {
        'figure_size': (12, 8),
        'dpi': 300,
        'style': 'seaborn-v0_8'
    },
    'reporting': {
        'include_plots': True,
        'plot_format': 'png',
        'report_formats': ['markdown', 'json', 'html']
    }
}

# Export commonly used functions
__all__ = [
    'setup_logging',
    'validate_file_path',
    'create_output_directory',
    'save_json',
    'load_json',
    'format_bytes',
    'format_duration',
    'calculate_distance',
    'smooth_data',
    'detect_outliers_iqr',
    'detect_outliers_zscore',
    'interpolate_missing_values',
    'normalize_angle',
    'calculate_sampling_rate',
    'generate_timestamps',
    'create_synthetic_flight_data',
    'validate_flight_data_structure',
    'get_system_info',
    'create_backup',
    'clean_old_files',
    'DEFAULT_CONFIG'
]
