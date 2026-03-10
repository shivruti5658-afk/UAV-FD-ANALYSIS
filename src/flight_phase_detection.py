import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from scipy.signal import find_peaks
from sklearn.cluster import KMeans


def detect_flight_phases_altitude_based(df: pd.DataFrame,
                                       alt_col: str = 'altitude_m',
                                       time_col: str = 'timestamp',
                                       climb_threshold: float = 0.5,
                                       descent_threshold: float = -0.5,
                                       min_phase_duration: int = 5) -> Dict[str, Any]:
    """
    Detect flight phases based on altitude changes.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        alt_col (str): Name of the altitude column
        time_col (str): Name of the timestamp column
        climb_threshold (float): Altitude rate threshold for climb (m/s)
        descent_threshold (float): Altitude rate threshold for descent (m/s)
        min_phase_duration (int): Minimum duration of a phase in data points
        
    Returns:
        Dict[str, Any]: Flight phase detection results
    """
    if alt_col not in df.columns:
        return {'phases': [], 'phase_summary': {}}
    
    # Calculate altitude rate
    df['altitude_rate'] = df[alt_col].diff()
    
    # Initialize phase detection
    phases = []
    current_phase = None
    phase_start = 0
    
    # Phase detection logic
    for i in range(len(df)):
        alt_rate = df.loc[i, 'altitude_rate']
        
        if pd.isna(alt_rate):
            continue
        
        # Determine phase based on altitude rate
        if alt_rate > climb_threshold:
            phase = 'climb'
        elif alt_rate < descent_threshold:
            phase = 'descent'
        else:
            # Determine if cruise or ground based on altitude
            altitude = df.loc[i, alt_col]
            if altitude < 5:  # Assuming ground level is below 5m
                phase = 'ground'
            else:
                phase = 'cruise'
        
        # Check if phase changed
        if current_phase != phase:
            # Save previous phase if it has sufficient duration
            if current_phase is not None and (i - phase_start) >= min_phase_duration:
                phase_info = {
                    'phase': current_phase,
                    'start_index': phase_start,
                    'end_index': i - 1,
                    'start_time': df.loc[phase_start, time_col] if time_col in df.columns else phase_start,
                    'end_time': df.loc[i - 1, time_col] if time_col in df.columns else i - 1,
                    'duration_points': i - phase_start,
                    'start_altitude': float(df.loc[phase_start, alt_col]),
                    'end_altitude': float(df.loc[i - 1, alt_col])
                }
                
                # Calculate duration in seconds if timestamp is available
                if time_col in df.columns and pd.api.types.is_datetime64_any_dtype(df[time_col]):
                    duration_seconds = (df.loc[i - 1, time_col] - df.loc[phase_start, time_col]).total_seconds()
                    phase_info['duration_seconds'] = duration_seconds
                
                phases.append(phase_info)
            
            # Start new phase
            current_phase = phase
            phase_start = i
    
    # Add the last phase
    if current_phase is not None and (len(df) - phase_start) >= min_phase_duration:
        phase_info = {
            'phase': current_phase,
            'start_index': phase_start,
            'end_index': len(df) - 1,
            'start_time': df.loc[phase_start, time_col] if time_col in df.columns else phase_start,
            'end_time': df.loc[len(df) - 1, time_col] if time_col in df.columns else len(df) - 1,
            'duration_points': len(df) - phase_start,
            'start_altitude': float(df.loc[phase_start, alt_col]),
            'end_altitude': float(df.loc[len(df) - 1, alt_col])
        }
        
        if time_col in df.columns and pd.api.types.is_datetime64_any_dtype(df[time_col]):
            duration_seconds = (df.loc[len(df) - 1, time_col] - df.loc[phase_start, time_col]).total_seconds()
            phase_info['duration_seconds'] = duration_seconds
        
        phases.append(phase_info)
    
    # Post-process phases to identify takeoff and landing
    phases = identify_takeoff_landing(phases, df, alt_col)
    
    # Create phase summary
    phase_summary = create_phase_summary(phases)
    
    return {
        'phases': phases,
        'phase_summary': phase_summary,
        'detection_method': 'altitude_based'
    }


def identify_takeoff_landing(phases: List[Dict], df: pd.DataFrame, alt_col: str) -> List[Dict]:
    """
    Identify takeoff and landing phases from detected phases.
    
    Args:
        phases (List[Dict]): List of detected phases
        df (pd.DataFrame): Flight data DataFrame
        alt_col (str): Name of the altitude column
        
    Returns:
        List[Dict]: Updated phases with takeoff/landing identification
    """
    for i, phase in enumerate(phases):
        if phase['phase'] == 'climb':
            # Check if this is takeoff (first climb from ground)
            if i == 0 or (i > 0 and phases[i-1]['phase'] == 'ground'):
                phase['phase'] = 'takeoff'
                phase['sub_phase'] = 'initial_climb'
        
        elif phase['phase'] == 'descent':
            # Check if this is landing (last descent to ground)
            if i == len(phases) - 1 or (i < len(phases) - 1 and phases[i+1]['phase'] == 'ground'):
                phase['phase'] = 'landing'
                phase['sub_phase'] = 'final_descent'
    
    return phases


def create_phase_summary(phases: List[Dict]) -> Dict[str, Any]:
    """
    Create a summary of detected flight phases.
    
    Args:
        phases (List[Dict]): List of detected phases
        
    Returns:
        Dict[str, Any]: Phase summary statistics
    """
    summary = {
        'total_phases': len(phases),
        'phase_counts': {},
        'phase_durations': {},
        'total_flight_time': 0
    }
    
    # Count phases and calculate durations
    for phase in phases:
        phase_name = phase['phase']
        
        # Count phases
        if phase_name not in summary['phase_counts']:
            summary['phase_counts'][phase_name] = 0
        summary['phase_counts'][phase_name] += 1
        
        # Sum durations
        if phase_name not in summary['phase_durations']:
            summary['phase_durations'][phase_name] = 0
        duration = phase.get('duration_seconds', phase['duration_points'])
        summary['phase_durations'][phase_name] += duration
        summary['total_flight_time'] += duration
    
    return summary


def detect_flight_phases_speed_based(df: pd.DataFrame,
                                   speed_col: str = 'speed_mps',
                                   time_col: str = 'timestamp',
                                   stationary_threshold: float = 2.0,
                                   min_phase_duration: int = 5) -> Dict[str, Any]:
    """
    Detect flight phases based on speed changes.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        speed_col (str): Name of the speed column
        time_col (str): Name of the timestamp column
        stationary_threshold (float): Speed threshold for stationary phase (m/s)
        min_phase_duration (int): Minimum duration of a phase in data points
        
    Returns:
        Dict[str, Any]: Flight phase detection results
    """
    if speed_col not in df.columns:
        return {'phases': [], 'phase_summary': {}}
    
    phases = []
    current_phase = None
    phase_start = 0
    
    for i in range(len(df)):
        speed = df.loc[i, speed_col]
        
        if pd.isna(speed):
            continue
        
        # Determine phase based on speed
        if speed < stationary_threshold:
            phase = 'stationary'
        else:
            phase = 'moving'
        
        # Check if phase changed
        if current_phase != phase:
            # Save previous phase
            if current_phase is not None and (i - phase_start) >= min_phase_duration:
                phase_info = {
                    'phase': current_phase,
                    'start_index': phase_start,
                    'end_index': i - 1,
                    'start_time': df.loc[phase_start, time_col] if time_col in df.columns else phase_start,
                    'end_time': df.loc[i - 1, time_col] if time_col in df.columns else i - 1,
                    'duration_points': i - phase_start,
                    'avg_speed': float(df.loc[phase_start:i, speed_col].mean())
                }
                
                if time_col in df.columns and pd.api.types.is_datetime64_any_dtype(df[time_col]):
                    duration_seconds = (df.loc[i - 1, time_col] - df.loc[phase_start, time_col]).total_seconds()
                    phase_info['duration_seconds'] = duration_seconds
                
                phases.append(phase_info)
            
            # Start new phase
            current_phase = phase
            phase_start = i
    
    # Add the last phase
    if current_phase is not None and (len(df) - phase_start) >= min_phase_duration:
        phase_info = {
            'phase': current_phase,
            'start_index': phase_start,
            'end_index': len(df) - 1,
            'start_time': df.loc[phase_start, time_col] if time_col in df.columns else phase_start,
            'end_time': df.loc[len(df) - 1, time_col] if time_col in df.columns else len(df) - 1,
            'duration_points': len(df) - phase_start,
            'avg_speed': float(df.loc[phase_start:, speed_col].mean())
        }
        
        if time_col in df.columns and pd.api.types.is_datetime64_any_dtype(df[time_col]):
            duration_seconds = (df.loc[len(df) - 1, time_col] - df.loc[phase_start, time_col]).total_seconds()
            phase_info['duration_seconds'] = duration_seconds
        
        phases.append(phase_info)
    
    # Create phase summary
    phase_summary = create_phase_summary(phases)
    
    return {
        'phases': phases,
        'phase_summary': phase_summary,
        'detection_method': 'speed_based'
    }


def detect_flight_phases_clustering(df: pd.DataFrame,
                                  features: List[str] = None,
                                  n_clusters: int = 5,
                                  time_col: str = 'timestamp') -> Dict[str, Any]:
    """
    Detect flight phases using clustering algorithm.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        features (List[str]): Features to use for clustering
        n_clusters (int): Number of clusters to identify
        time_col (str): Name of the timestamp column
        
    Returns:
        Dict[str, Any]: Flight phase detection results
    """
    if features is None:
        features = ['altitude_m', 'speed_mps', 'roll_deg', 'pitch_deg']
    
    # Filter available features
    available_features = [f for f in features if f in df.columns]
    
    if len(available_features) < 2:
        return {'phases': [], 'phase_summary': {}}
    
    # Prepare data for clustering
    feature_data = df[available_features].fillna(0)
    
    # Normalize features
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(feature_data)
    
    # Apply K-means clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    cluster_labels = kmeans.fit_predict(scaled_data)
    
    # Assign cluster labels to dataframe
    df['cluster'] = cluster_labels
    
    # Convert clusters to phases
    phases = []
    current_cluster = None
    phase_start = 0
    
    for i in range(len(df)):
        cluster = df.loc[i, 'cluster']
        
        if current_cluster != cluster:
            # Save previous phase
            if current_cluster is not None:
                phase_info = {
                    'phase': f'cluster_{current_cluster}',
                    'start_index': phase_start,
                    'end_index': i - 1,
                    'start_time': df.loc[phase_start, time_col] if time_col in df.columns else phase_start,
                    'end_time': df.loc[i - 1, time_col] if time_col in df.columns else i - 1,
                    'duration_points': i - phase_start,
                    'cluster_id': current_cluster
                }
                
                if time_col in df.columns and pd.api.types.is_datetime64_any_dtype(df[time_col]):
                    duration_seconds = (df.loc[i - 1, time_col] - df.loc[phase_start, time_col]).total_seconds()
                    phase_info['duration_seconds'] = duration_seconds
                
                # Add cluster characteristics
                cluster_data = df.loc[phase_start:i-1, available_features]
                for feature in available_features:
                    phase_info[f'avg_{feature}'] = float(cluster_data[feature].mean())
                
                phases.append(phase_info)
            
            # Start new phase
            current_cluster = cluster
            phase_start = i
    
    # Add the last phase
    if current_cluster is not None:
        phase_info = {
            'phase': f'cluster_{current_cluster}',
            'start_index': phase_start,
            'end_index': len(df) - 1,
            'start_time': df.loc[phase_start, time_col] if time_col in df.columns else phase_start,
            'end_time': df.loc[len(df) - 1, time_col] if time_col in df.columns else len(df) - 1,
            'duration_points': len(df) - phase_start,
            'cluster_id': current_cluster
        }
        
        if time_col in df.columns and pd.api.types.is_datetime64_any_dtype(df[time_col]):
            duration_seconds = (df.loc[len(df) - 1, time_col] - df.loc[phase_start, time_col]).total_seconds()
            phase_info['duration_seconds'] = duration_seconds
        
        # Add cluster characteristics
        cluster_data = df.loc[phase_start:, available_features]
        for feature in available_features:
            phase_info[f'avg_{feature}'] = float(cluster_data[feature].mean())
        
        phases.append(phase_info)
    
    # Create phase summary
    phase_summary = create_phase_summary(phases)
    
    return {
        'phases': phases,
        'phase_summary': phase_summary,
        'detection_method': 'clustering',
        'cluster_centers': kmeans.cluster_centers_.tolist(),
        'features_used': available_features
    }


def detect_flight_phases_hybrid(df: pd.DataFrame,
                               time_col: str = 'timestamp',
                               climb_threshold: float = 0.5,
                               descent_threshold: float = -0.5,
                               stationary_threshold: float = 2.0,
                               min_phase_duration: int = 5) -> Dict[str, Any]:
    """
    Detect flight phases using a hybrid approach combining altitude and speed.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        time_col (str): Name of the timestamp column
        climb_threshold (float): Altitude rate threshold for climb (m/s)
        descent_threshold (float): Altitude rate threshold for descent (m/s)
        stationary_threshold (float): Speed threshold for stationary phase (m/s)
        min_phase_duration (int): Minimum duration of a phase in data points
        
    Returns:
        Dict[str, Any]: Flight phase detection results
    """
    phases = []
    current_phase = None
    phase_start = 0
    
    for i in range(len(df)):
        altitude_rate = df.loc[i, 'altitude_rate'] if 'altitude_rate' in df.columns else 0
        speed = df.loc[i, 'speed_mps'] if 'speed_mps' in df.columns else 0
        altitude = df.loc[i, 'altitude_m'] if 'altitude_m' in df.columns else 0
        
        # Determine phase using hybrid logic
        if altitude < 5 and speed < stationary_threshold:
            phase = 'ground'
        elif altitude_rate > climb_threshold and speed > stationary_threshold:
            phase = 'takeoff'
        elif altitude_rate > climb_threshold:
            phase = 'climb'
        elif altitude_rate < descent_threshold and altitude > 10:
            phase = 'descent'
        elif altitude_rate < descent_threshold and altitude <= 10 and speed < stationary_threshold:
            phase = 'landing'
        elif speed > stationary_threshold and abs(altitude_rate) < 0.2:
            phase = 'cruise'
        else:
            phase = 'transition'
        
        # Check if phase changed
        if current_phase != phase:
            # Save previous phase
            if current_phase is not None and (i - phase_start) >= min_phase_duration:
                phase_info = {
                    'phase': current_phase,
                    'start_index': phase_start,
                    'end_index': i - 1,
                    'start_time': df.loc[phase_start, time_col] if time_col in df.columns else phase_start,
                    'end_time': df.loc[i - 1, time_col] if time_col in df.columns else i - 1,
                    'duration_points': i - phase_start
                }
                
                if time_col in df.columns and pd.api.types.is_datetime64_any_dtype(df[time_col]):
                    duration_seconds = (df.loc[i - 1, time_col] - df.loc[phase_start, time_col]).total_seconds()
                    phase_info['duration_seconds'] = duration_seconds
                
                phases.append(phase_info)
            
            # Start new phase
            current_phase = phase
            phase_start = i
    
    # Add the last phase
    if current_phase is not None and (len(df) - phase_start) >= min_phase_duration:
        phase_info = {
            'phase': current_phase,
            'start_index': phase_start,
            'end_index': len(df) - 1,
            'start_time': df.loc[phase_start, time_col] if time_col in df.columns else phase_start,
            'end_time': df.loc[len(df) - 1, time_col] if time_col in df.columns else len(df) - 1,
            'duration_points': len(df) - phase_start
        }
        
        if time_col in df.columns and pd.api.types.is_datetime64_any_dtype(df[time_col]):
            duration_seconds = (df.loc[len(df) - 1, time_col] - df.loc[phase_start, time_col]).total_seconds()
            phase_info['duration_seconds'] = duration_seconds
        
        phases.append(phase_info)
    
    # Create phase summary
    phase_summary = create_phase_summary(phases)
    
    return {
        'phases': phases,
        'phase_summary': phase_summary,
        'detection_method': 'hybrid'
    }


def detect_flight_phases(df: pd.DataFrame, 
                        method: str = 'hybrid',
                        config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Main function to detect flight phases using specified method.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        method (str): Detection method ('altitude', 'speed', 'clustering', 'hybrid')
        config (Dict[str, Any], optional): Configuration parameters
        
    Returns:
        Dict[str, Any]: Flight phase detection results
    """
    if config is None:
        config = {
            'climb_threshold': 0.5,
            'descent_threshold': -0.5,
            'stationary_threshold': 2.0,
            'min_phase_duration': 5,
            'n_clusters': 5
        }
    
    # Pre-compute altitude rate if needed
    if 'altitude_m' in df.columns and method in ['altitude', 'hybrid']:
        df['altitude_rate'] = df['altitude_m'].diff()
    
    # Choose detection method
    if method == 'altitude':
        return detect_flight_phases_altitude_based(df, **config)
    elif method == 'speed':
        return detect_flight_phases_speed_based(df, **config)
    elif method == 'clustering':
        return detect_flight_phases_clustering(df, **config)
    elif method == 'hybrid':
        return detect_flight_phases_hybrid(df, **config)
    else:
        raise ValueError(f"Unknown detection method: {method}")


def format_phase_summary(phase_results: Dict[str, Any]) -> str:
    """
    Format flight phase results into a readable summary.
    
    Args:
        phase_results (Dict[str, Any]): Results from phase detection
        
    Returns:
        str: Formatted phase summary
    """
    summary = []
    phases = phase_results['phases']
    phase_summary = phase_results['phase_summary']
    
    summary.append(f"Detection Method: {phase_results['detection_method']}")
    summary.append(f"Total Phases: {phase_summary['total_phases']}")
    summary.append("")
    
    # Phase counts
    summary.append("Phase Breakdown:")
    for phase_name, count in phase_summary['phase_counts'].items():
        duration = phase_summary['phase_durations'][phase_name]
        summary.append(f"  {phase_name.capitalize()}: {count} occurrences, {duration:.1f}s total")
    
    summary.append("")
    
    # Detailed phase timeline
    summary.append("Phase Timeline:")
    for i, phase in enumerate(phases):
        phase_name = phase['phase']
        duration = phase.get('duration_seconds', phase['duration_points'])
        start_time = phase.get('start_time', phase['start_index'])
        
        if isinstance(start_time, str):
            time_str = start_time
        else:
            time_str = f"Index {start_time}"
        
        summary.append(f"  {i+1}. {phase_name.capitalize()}: {time_str} - {duration:.1f}s")
    
    return "\n".join(summary)
