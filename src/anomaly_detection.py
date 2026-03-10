import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from scipy import stats
from scipy.signal import find_peaks


def detect_altitude_anomalies(df: pd.DataFrame,
                            alt_col: str = 'altitude_m',
                            time_col: str = 'timestamp',
                            threshold_std: float = 3.0) -> Dict[str, Any]:
    """
    Detect altitude anomalies including sudden drops and spikes.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        alt_col (str): Name of the altitude column
        time_col (str): Name of the timestamp column
        threshold_std (float): Standard deviation threshold for anomaly detection
        
    Returns:
        Dict[str, Any]: Altitude anomaly detection results
    """
    if alt_col not in df.columns:
        return {'anomalies': [], 'total_anomalies': 0, 'anomaly_rate': 0}
    
    anomalies = []
    
    # Calculate altitude change rate
    df['altitude_rate'] = df[alt_col].diff()
    
    # Detect sudden altitude drops
    altitude_rate_std = df['altitude_rate'].std()
    if pd.isna(altitude_rate_std) or altitude_rate_std == 0:
        drop_threshold = 0
    else:
        drop_threshold = -threshold_std * altitude_rate_std
    drop_indices = df[df['altitude_rate'] < drop_threshold].index
    
    for idx in drop_indices:
        if pd.notna(df.loc[idx, 'altitude_rate']):
            anomalies.append({
                'type': 'altitude_drop',
                'timestamp': df.loc[idx, time_col] if time_col in df.columns else idx,
                'index': int(idx),
                'value': float(df.loc[idx, alt_col]),
                'rate': float(df.loc[idx, 'altitude_rate']),
                'severity': 'high' if df.loc[idx, 'altitude_rate'] < -2 * drop_threshold else 'medium'
            })
    
    # Detect altitude spikes
    altitude_rate_std = df['altitude_rate'].std()
    if pd.isna(altitude_rate_std) or altitude_rate_std == 0:
        spike_threshold = 0
    else:
        spike_threshold = threshold_std * altitude_rate_std
    spike_indices = df[df['altitude_rate'] > spike_threshold].index
    
    for idx in spike_indices:
        if pd.notna(df.loc[idx, 'altitude_rate']):
            anomalies.append({
                'type': 'altitude_spike',
                'timestamp': df.loc[idx, time_col] if time_col in df.columns else idx,
                'index': int(idx),
                'value': float(df.loc[idx, alt_col]),
                'rate': float(df.loc[idx, 'altitude_rate']),
                'severity': 'high' if df.loc[idx, 'altitude_rate'] > 2 * spike_threshold else 'medium'
            })
    
    # Z-score based anomaly detection
    z_scores = np.abs(stats.zscore(df[alt_col].dropna()))
    z_anomaly_indices = np.where(z_scores > threshold_std)[0]
    
    for idx in z_anomaly_indices:
        if idx < len(df):
            anomalies.append({
                'type': 'altitude_zscore',
                'timestamp': df.loc[idx, time_col] if time_col in df.columns else idx,
                'index': int(idx),
                'value': float(df.loc[idx, alt_col]),
                'z_score': float(z_scores[idx]),
                'severity': 'high' if z_scores[idx] > 4 else 'medium'
            })
    
    total_anomalies = len(anomalies)
    anomaly_rate = total_anomalies / len(df) if len(df) > 0 else 0
    
    return {
        'anomalies': anomalies,
        'total_anomalies': total_anomalies,
        'anomaly_rate': anomaly_rate,
        'detection_method': 'threshold_and_zscore'
    }


def detect_attitude_anomalies(df: pd.DataFrame,
                            roll_col: str = 'roll_deg',
                            pitch_col: str = 'pitch_deg',
                            yaw_col: str = 'yaw_deg',
                            time_col: str = 'timestamp',
                            threshold_std: float = 3.0) -> Dict[str, Any]:
    """
    Detect attitude anomalies including roll spikes and pitch excursions.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        roll_col (str): Name of the roll column
        pitch_col (str): Name of the pitch column
        yaw_col (str): Name of the yaw column
        time_col (str): Name of the timestamp column
        threshold_std (float): Standard deviation threshold
        
    Returns:
        Dict[str, Any]: Attitude anomaly detection results
    """
    anomalies = []
    attitude_cols = {'roll': roll_col, 'pitch': pitch_col, 'yaw': yaw_col}
    
    for attitude_type, col in attitude_cols.items():
        if col not in df.columns:
            continue
        
        # Detect rapid changes (spikes)
        df[f'{attitude_type}_rate'] = df[col].diff()
        attitude_rate_std = df[f'{attitude_type}_rate'].std()
        if pd.isna(attitude_rate_std) or attitude_rate_std == 0:
            rate_threshold = 0
        else:
            rate_threshold = threshold_std * attitude_rate_std
        
        spike_indices = df[np.abs(df[f'{attitude_type}_rate']) > rate_threshold].index
        
        for idx in spike_indices:
            if pd.notna(df.loc[idx, f'{attitude_type}_rate']):
                anomalies.append({
                    'type': f'{attitude_type}_spike',
                    'timestamp': df.loc[idx, time_col] if time_col in df.columns else idx,
                    'index': int(idx),
                    'value': float(df.loc[idx, col]),
                    'rate': float(df.loc[idx, f'{attitude_type}_rate']),
                    'severity': 'high' if abs(df.loc[idx, f'{attitude_type}_rate']) > 2 * rate_threshold else 'medium'
                })
        
        # Z-score based detection
        z_scores = np.abs(stats.zscore(df[col].dropna()))
        z_anomaly_indices = np.where(z_scores > threshold_std)[0]
        
        for idx in z_anomaly_indices:
            if idx < len(df):
                anomalies.append({
                    'type': f'{attitude_type}_zscore',
                    'timestamp': df.loc[idx, time_col] if time_col in df.columns else idx,
                    'index': int(idx),
                    'value': float(df.loc[idx, col]),
                    'z_score': float(z_scores[idx]),
                    'severity': 'high' if z_scores[idx] > 4 else 'medium'
                })
    
    return {
        'anomalies': anomalies,
        'total_anomalies': len(anomalies),
        'anomaly_rate': len(anomalies) / len(df) if len(df) > 0 else 0
    }


def detect_speed_anomalies(df: pd.DataFrame,
                          speed_col: str = 'speed_mps',
                          time_col: str = 'timestamp',
                          threshold_std: float = 3.0) -> Dict[str, Any]:
    """
    Detect speed anomalies including sudden acceleration/deceleration.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        speed_col (str): Name of the speed column
        time_col (str): Name of the timestamp column
        threshold_std (float): Standard deviation threshold
        
    Returns:
        Dict[str, Any]: Speed anomaly detection results
    """
    if speed_col not in df.columns:
        return {'anomalies': [], 'total_anomalies': 0, 'anomaly_rate': 0}
    
    anomalies = []
    
    # Calculate acceleration
    df['acceleration'] = df[speed_col].diff()
    
    # Detect sudden acceleration/deceleration
    accel_std = df['acceleration'].std()
    if pd.isna(accel_std) or accel_std == 0:
        accel_threshold = 0
    else:
        accel_threshold = threshold_std * accel_std
    accel_anomaly_indices = df[np.abs(df['acceleration']) > accel_threshold].index
    
    for idx in accel_anomaly_indices:
        if pd.notna(df.loc[idx, 'acceleration']):
            anomaly_type = 'sudden_acceleration' if df.loc[idx, 'acceleration'] > 0 else 'sudden_deceleration'
            anomalies.append({
                'type': anomaly_type,
                'timestamp': df.loc[idx, time_col] if time_col in df.columns else idx,
                'index': int(idx),
                'speed': float(df.loc[idx, speed_col]),
                'acceleration': float(df.loc[idx, 'acceleration']),
                'severity': 'high' if abs(df.loc[idx, 'acceleration']) > 2 * accel_threshold else 'medium'
            })
    
    # Z-score based speed anomaly detection
    z_scores = np.abs(stats.zscore(df[speed_col].dropna()))
    z_anomaly_indices = np.where(z_scores > threshold_std)[0]
    
    for idx in z_anomaly_indices:
        if idx < len(df):
            anomalies.append({
                'type': 'speed_zscore',
                'timestamp': df.loc[idx, time_col] if time_col in df.columns else idx,
                'index': int(idx),
                'value': float(df.loc[idx, speed_col]),
                'z_score': float(z_scores[idx]),
                'severity': 'high' if z_scores[idx] > 4 else 'medium'
            })
    
    return {
        'anomalies': anomalies,
        'total_anomalies': len(anomalies),
        'anomaly_rate': len(anomalies) / len(df) if len(df) > 0 else 0
    }


def detect_battery_anomalies(df: pd.DataFrame,
                           battery_col: str = 'battery_percent',
                           time_col: str = 'timestamp',
                           threshold_std: float = 3.0) -> Dict[str, Any]:
    """
    Detect battery anomalies including sudden drain and irregular behavior.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        battery_col (str): Name of the battery column
        time_col (str): Name of the timestamp column
        threshold_std (float): Standard deviation threshold
        
    Returns:
        Dict[str, Any]: Battery anomaly detection results
    """
    if battery_col not in df.columns:
        return {'anomalies': [], 'total_anomalies': 0, 'anomaly_rate': 0}
    
    anomalies = []
    
    # Calculate battery drain rate
    df['battery_drain_rate'] = -df[battery_col].diff()  # Negative because battery decreases
    
    # Detect sudden battery drain
    drain_std = df['battery_drain_rate'].std()
    if pd.isna(drain_std) or drain_std == 0:
        drain_threshold = 0
    else:
        drain_threshold = threshold_std * drain_std
    drain_anomaly_indices = df[df['battery_drain_rate'] > drain_threshold].index
    
    for idx in drain_anomaly_indices:
        if pd.notna(df.loc[idx, 'battery_drain_rate']):
            anomalies.append({
                'type': 'sudden_battery_drain',
                'timestamp': df.loc[idx, time_col] if time_col in df.columns else idx,
                'index': int(idx),
                'battery_level': float(df.loc[idx, battery_col]),
                'drain_rate': float(df.loc[idx, 'battery_drain_rate']),
                'severity': 'high' if df.loc[idx, 'battery_drain_rate'] > 2 * drain_threshold else 'medium'
            })
    
    # Detect battery increase (shouldn't happen during flight)
    battery_increase_indices = df[df[battery_col].diff() > 0].index
    
    for idx in battery_increase_indices:
        anomalies.append({
            'type': 'battery_increase_anomaly',
            'timestamp': df.loc[idx, time_col] if time_col in df.columns else idx,
            'index': int(idx),
            'battery_level': float(df.loc[idx, battery_col]),
            'change': float(df.loc[idx, battery_col] - df.loc[idx-1, battery_col] if idx > 0 else 0),
            'severity': 'medium'
        })
    
    return {
        'anomalies': anomalies,
        'total_anomalies': len(anomalies),
        'anomaly_rate': len(anomalies) / len(df) if len(df) > 0 else 0
    }


def detect_gps_anomalies(df: pd.DataFrame,
                        lat_col: str = 'gps_lat',
                        lon_col: str = 'gps_lon',
                        time_col: str = 'timestamp',
                        threshold_std: float = 3.0) -> Dict[str, Any]:
    """
    Detect GPS anomalies including sudden position jumps and signal loss.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        lat_col (str): Name of the latitude column
        lon_col (str): Name of the longitude column
        time_col (str): Name of the timestamp column
        threshold_std (float): Standard deviation threshold
        
    Returns:
        Dict[str, Any]: GPS anomaly detection results
    """
    if lat_col not in df.columns or lon_col not in df.columns:
        return {'anomalies': [], 'total_anomalies': 0, 'anomaly_rate': 0}
    
    anomalies = []
    
    # Calculate distance between consecutive GPS points
    distances = []
    for i in range(1, len(df)):
        lat1, lon1 = df.iloc[i-1][lat_col], df.iloc[i-1][lon_col]
        lat2, lon2 = df.iloc[i][lat_col], df.iloc[i][lon_col]
        
        # Convert to radians and calculate Haversine distance
        lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
        c = 2 * np.arcsin(np.sqrt(a))
        distance = 6371000 * c  # Earth's radius in meters
        distances.append(distance)
    
    # Add distance to dataframe
    df['gps_distance'] = [0] + distances
    
    # Detect GPS position jumps
    distance_threshold = threshold_std * np.std(distances) if distances else 0
    jump_indices = df[df['gps_distance'] > distance_threshold].index
    
    for idx in jump_indices:
        if idx > 0:  # Skip first point
            anomalies.append({
                'type': 'gps_position_jump',
                'timestamp': df.loc[idx, time_col] if time_col in df.columns else idx,
                'index': int(idx),
                'distance': float(df.loc[idx, 'gps_distance']),
                'lat': float(df.loc[idx, lat_col]),
                'lon': float(df.loc[idx, lon_col]),
                'severity': 'high' if df.loc[idx, 'gps_distance'] > 2 * distance_threshold else 'medium'
            })
    
    # Detect missing GPS data (NaN values)
    missing_gps_indices = df[df[lat_col].isna() | df[lon_col].isna()].index
    
    for idx in missing_gps_indices:
        anomalies.append({
            'type': 'gps_signal_loss',
            'timestamp': df.loc[idx, time_col] if time_col in df.columns else idx,
            'index': int(idx),
            'severity': 'high'
        })
    
    return {
        'anomalies': anomalies,
        'total_anomalies': len(anomalies),
        'anomaly_rate': len(anomalies) / len(df) if len(df) > 0 else 0
    }


def detect_all_anomalies(df: pd.DataFrame, 
                        config: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
    """
    Comprehensive anomaly detection across all flight parameters.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        config (Dict[str, float], optional): Configuration parameters for thresholds
        
    Returns:
        Dict[str, Any]: Complete anomaly detection results
    """
    if config is None:
        config = {
            'threshold_std': 3.0,
            'min_anomaly_severity': 'medium'
        }
    
    all_anomalies = {}
    
    # Altitude anomalies
    all_anomalies['altitude'] = detect_altitude_anomalies(df, threshold_std=config['threshold_std'])
    
    # Attitude anomalies
    all_anomalies['attitude'] = detect_attitude_anomalies(df, threshold_std=config['threshold_std'])
    
    # Speed anomalies
    all_anomalies['speed'] = detect_speed_anomalies(df, threshold_std=config['threshold_std'])
    
    # Battery anomalies
    all_anomalies['battery'] = detect_battery_anomalies(df, threshold_std=config['threshold_std'])
    
    # GPS anomalies
    all_anomalies['gps'] = detect_gps_anomalies(df, threshold_std=config['threshold_std'])
    
    # Summary statistics
    total_anomalies = sum(results['total_anomalies'] for results in all_anomalies.values())
    total_data_points = len(df)
    overall_anomaly_rate = total_anomalies / total_data_points if total_data_points > 0 else 0
    
    # Categorize anomalies by severity
    severity_counts = {'high': 0, 'medium': 0, 'low': 0}
    for category_results in all_anomalies.values():
        for anomaly in category_results['anomalies']:
            severity = anomaly.get('severity', 'medium')
            if severity in severity_counts:
                severity_counts[severity] += 1
    
    # Overall assessment
    if overall_anomaly_rate < 0.01:
        overall_assessment = "Excellent - Very few anomalies detected"
    elif overall_anomaly_rate < 0.05:
        overall_assessment = "Good - Low anomaly rate"
    elif overall_anomaly_rate < 0.1:
        overall_assessment = "Fair - Moderate anomaly rate"
    else:
        overall_assessment = "Poor - High anomaly rate"
    
    return {
        'categories': all_anomalies,
        'summary': {
            'total_anomalies': total_anomalies,
            'total_data_points': total_data_points,
            'overall_anomaly_rate': overall_anomaly_rate,
            'severity_breakdown': severity_counts,
            'overall_assessment': overall_assessment
        }
    }


def generate_anomaly_report(anomaly_results: Dict[str, Any]) -> str:
    """
    Generate a human-readable anomaly detection report.
    
    Args:
        anomaly_results (Dict[str, Any]): Results from anomaly detection
        
    Returns:
        str: Formatted anomaly report
    """
    report = []
    summary = anomaly_results['summary']
    
    report.append("=== ANOMALY DETECTION REPORT ===")
    report.append(f"Total Anomalies: {summary['total_anomalies']}")
    report.append(f"Overall Anomaly Rate: {summary['overall_anomaly_rate']:.2%}")
    report.append(f"Assessment: {summary['overall_assessment']}")
    report.append("")
    
    # Severity breakdown
    report.append("Severity Breakdown:")
    for severity, count in summary['severity_breakdown'].items():
        report.append(f"  {severity.capitalize()}: {count}")
    report.append("")
    
    # Category breakdown
    report.append("Anomaly Categories:")
    for category, results in anomaly_results['categories'].items():
        if results['total_anomalies'] > 0:
            report.append(f"  {category.capitalize()}: {results['total_anomalies']} anomalies")
            
            # Show top 3 anomalies for this category
            top_anomalies = results['anomalies'][:3]
            for anomaly in top_anomalies:
                timestamp = anomaly.get('timestamp', 'N/A')
                anomaly_type = anomaly.get('type', 'Unknown')
                severity = anomaly.get('severity', 'medium')
                report.append(f"    - {anomaly_type} at {timestamp} ({severity})")
            
            if results['total_anomalies'] > 3:
                report.append(f"    ... and {results['total_anomalies'] - 3} more")
    
    return "\n".join(report)
