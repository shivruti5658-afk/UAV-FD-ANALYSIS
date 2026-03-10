import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
from scipy import stats
from sklearn.linear_model import LinearRegression


def calculate_battery_consumption_rate(df: pd.DataFrame,
                                     battery_col: str = 'battery_percent',
                                     time_col: str = 'timestamp') -> Dict[str, float]:
    """
    Calculate battery consumption rate and related metrics.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        battery_col (str): Name of the battery column
        time_col (str): Name of the timestamp column
        
    Returns:
        Dict[str, float]: Battery consumption metrics
    """
    if battery_col not in df.columns:
        return {
            'consumption_rate_percent_per_minute': 0,
            'consumption_rate_percent_per_second': 0,
            'total_consumption': 0,
            'flight_duration_minutes': 0
        }
    
    # Calculate total battery consumption
    initial_battery = df[battery_col].iloc[0]
    final_battery = df[battery_col].iloc[-1]
    total_consumption = initial_battery - final_battery
    
    # Calculate flight duration
    if time_col in df.columns and pd.api.types.is_datetime64_any_dtype(df[time_col]):
        flight_duration_seconds = (df[time_col].iloc[-1] - df[time_col].iloc[0]).total_seconds()
        flight_duration_minutes = flight_duration_seconds / 60
    else:
        flight_duration_seconds = len(df) - 1
        flight_duration_minutes = flight_duration_seconds / 60
    
    # Calculate consumption rates
    if flight_duration_minutes > 0:
        consumption_rate_percent_per_minute = total_consumption / flight_duration_minutes
        consumption_rate_percent_per_second = total_consumption / flight_duration_seconds
    else:
        consumption_rate_percent_per_minute = 0
        consumption_rate_percent_per_second = 0
    
    return {
        'consumption_rate_percent_per_minute': float(consumption_rate_percent_per_minute),
        'consumption_rate_percent_per_second': float(consumption_rate_percent_per_second),
        'total_consumption': float(total_consumption),
        'flight_duration_minutes': float(flight_duration_minutes)
    }


def estimate_remaining_flight_time(df: pd.DataFrame,
                                  battery_col: str = 'battery_percent',
                                  time_col: str = 'timestamp',
                                  safety_margin: float = 20.0) -> Dict[str, float]:
    """
    Estimate remaining flight time based on current battery level and consumption rate.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        battery_col (str): Name of the battery column
        time_col (str): Name of the timestamp column
        safety_margin (float): Safety margin percentage (battery to reserve)
        
    Returns:
        Dict[str, float]: Estimated remaining flight time
    """
    if battery_col not in df.columns or len(df) == 0:
        return {
            'remaining_flight_time_minutes': 0,
            'remaining_flight_time_seconds': 0,
            'usable_battery_percentage': 0,
            'current_battery_level': 0
        }
    
    # Get current battery level
    current_battery = df[battery_col].iloc[-1]
    
    # Calculate usable battery (subtract safety margin)
    usable_battery = max(0, current_battery - safety_margin)
    
    # Get consumption rate
    consumption_metrics = calculate_battery_consumption_rate(df, battery_col, time_col)
    consumption_rate_per_minute = consumption_metrics['consumption_rate_percent_per_minute']
    
    # Estimate remaining flight time
    if consumption_rate_per_minute > 0:
        remaining_flight_time_minutes = usable_battery / consumption_rate_per_minute
        remaining_flight_time_seconds = remaining_flight_time_minutes * 60
    else:
        remaining_flight_time_minutes = 0
        remaining_flight_time_seconds = 0
    
    return {
        'remaining_flight_time_minutes': float(remaining_flight_time_minutes),
        'remaining_flight_time_seconds': float(remaining_flight_time_seconds),
        'usable_battery_percentage': float(usable_battery),
        'current_battery_level': float(current_battery)
    }


def analyze_battery_efficiency(df: pd.DataFrame,
                              battery_col: str = 'battery_percent',
                              alt_col: str = 'altitude_m',
                              speed_col: str = 'speed_mps',
                              distance_col: str = None) -> Dict[str, float]:
    """
    Analyze battery efficiency metrics.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        battery_col (str): Name of the battery column
        alt_col (str): Name of the altitude column
        speed_col (str): Name of the speed column
        distance_col (str): Name of the distance column (if available)
        
    Returns:
        Dict[str, float]: Battery efficiency metrics
    """
    if battery_col not in df.columns:
        return {
            'altitude_per_percent': 0,
            'speed_per_percent': 0,
            'distance_per_percent': 0,
            'battery_efficiency_score': 0
        }
    
    # Calculate total battery consumption
    initial_battery = df[battery_col].iloc[0]
    final_battery = df[battery_col].iloc[-1]
    battery_used = initial_battery - final_battery
    
    if battery_used <= 0:
        return {
            'altitude_per_percent': 0,
            'speed_per_percent': 0,
            'distance_per_percent': 0,
            'battery_efficiency_score': 0
        }
    
    efficiency_metrics = {}
    
    # Altitude efficiency
    if alt_col in df.columns:
        max_altitude = df[alt_col].max()
        min_altitude = df[alt_col].min()
        altitude_gain = max_altitude - min_altitude
        efficiency_metrics['altitude_per_percent'] = altitude_gain / battery_used
    
    # Speed efficiency
    if speed_col in df.columns:
        avg_speed = df[speed_col].mean()
        efficiency_metrics['speed_per_percent'] = avg_speed / battery_used
    
    # Distance efficiency
    if distance_col and distance_col in df.columns:
        total_distance = df[distance_col].iloc[-1] - df[distance_col].iloc[0]
        efficiency_metrics['distance_per_percent'] = total_distance / battery_used
    else:
        # Calculate distance from GPS if available
        if 'gps_lat' in df.columns and 'gps_lon' in df.columns:
            total_distance = 0
            for i in range(1, len(df)):
                lat1, lon1 = df.iloc[i-1]['gps_lat'], df.iloc[i-1]['gps_lon']
                lat2, lon2 = df.iloc[i]['gps_lat'], df.iloc[i]['gps_lon']
                
                # Haversine formula
                lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
                dlat = lat2 - lat1
                dlon = lon2 - lon1
                a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
                c = 2 * np.arcsin(np.sqrt(a))
                distance = 6371000 * c  # Earth's radius in meters
                total_distance += distance
            
            efficiency_metrics['distance_per_percent'] = total_distance / battery_used
        else:
            efficiency_metrics['distance_per_percent'] = 0
    
    # Calculate overall efficiency score (normalized)
    efficiency_values = [v for v in efficiency_metrics.values() if v > 0]
    if efficiency_values:
        efficiency_metrics['battery_efficiency_score'] = np.mean(efficiency_values)
    else:
        efficiency_metrics['battery_efficiency_score'] = 0
    
    return efficiency_metrics


def detect_battery_anomalies(df: pd.DataFrame,
                           battery_col: str = 'battery_percent',
                           time_col: str = 'timestamp',
                           threshold_std: float = 3.0) -> Dict[str, Any]:
    """
    Detect battery anomalies such as sudden drops or inconsistent behavior.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        battery_col (str): Name of the battery column
        time_col (str): Name of the timestamp column
        threshold_std (float): Standard deviation threshold for anomaly detection
        
    Returns:
        Dict[str, Any]: Battery anomaly detection results
    """
    if battery_col not in df.columns:
        return {'anomalies': [], 'total_anomalies': 0, 'anomaly_rate': 0}
    
    anomalies = []
    
    # Calculate battery drain rate
    df['battery_drain_rate'] = -df[battery_col].diff()  # Negative because battery decreases
    
    # Detect sudden battery drain
    if 'battery_drain_rate' in df.columns:
        drain_threshold = threshold_std * df['battery_drain_rate'].std()
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
    
    # Z-score based anomaly detection
    z_scores = np.abs(stats.zscore(df[battery_col].dropna()))
    z_anomaly_indices = np.where(z_scores > threshold_std)[0]
    
    for idx in z_anomaly_indices:
        if idx < len(df):
            anomalies.append({
                'type': 'battery_zscore',
                'timestamp': df.loc[idx, time_col] if time_col in df.columns else idx,
                'index': int(idx),
                'value': float(df.loc[idx, battery_col]),
                'z_score': float(z_scores[idx]),
                'severity': 'high' if z_scores[idx] > 4 else 'medium'
            })
    
    return {
        'anomalies': anomalies,
        'total_anomalies': len(anomalies),
        'anomaly_rate': len(anomalies) / len(df) if len(df) > 0 else 0
    }


def predict_battery_end_of_flight(df: pd.DataFrame,
                                 battery_col: str = 'battery_percent',
                                 time_col: str = 'timestamp',
                                 prediction_window: int = 10) -> Dict[str, Any]:
    """
    Predict battery depletion using linear regression.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        battery_col (str): Name of the battery column
        time_col (str): Name of the timestamp column
        prediction_window (int): Number of future points to predict
        
    Returns:
        Dict[str, Any]: Battery prediction results
    """
    if battery_col not in df.columns or len(df) < 5:
        return {
            'predicted_battery_levels': [],
            'predicted_depletion_time': None,
            'regression_score': 0,
            'trend': 'unknown'
        }
    
    # Prepare data for regression
    if time_col in df.columns and pd.api.types.is_datetime64_any_dtype(df[time_col]):
        # Use actual timestamps
        time_seconds = (df[time_col] - df[time_col].iloc[0]).dt.total_seconds().values
    else:
        # Use index as time
        time_seconds = np.arange(len(df)).astype(float)
    
    battery_levels = df[battery_col].values
    
    # Remove NaN values
    valid_indices = ~np.isnan(battery_levels)
    time_seconds = time_seconds[valid_indices]
    battery_levels = battery_levels[valid_indices]
    
    if len(time_seconds) < 3:
        return {
            'predicted_battery_levels': [],
            'predicted_depletion_time': None,
            'regression_score': 0,
            'trend': 'insufficient_data'
        }
    
    # Perform linear regression
    X = time_seconds.reshape(-1, 1)
    y = battery_levels
    
    model = LinearRegression()
    model.fit(X, y)
    
    # Calculate regression score
    regression_score = model.score(X, y)
    
    # Determine trend
    slope = model.coef_[0]
    if slope < -0.01:
        trend = 'decreasing'
    elif slope > 0.01:
        trend = 'increasing'
    else:
        trend = 'stable'
    
    # Predict future battery levels
    if trend == 'decreasing':
        # Predict future points
        last_time = time_seconds[-1]
        future_times = np.arange(last_time + 1, last_time + prediction_window + 1)
        future_times = future_times.reshape(-1, 1)
        predicted_levels = model.predict(future_times)
        
        # Find predicted depletion time (when battery reaches 0%)
        if slope < 0:
            depletion_time = -model.intercept_ / slope
            if depletion_time > last_time:
                predicted_depletion_time = depletion_time
            else:
                predicted_depletion_time = None
        else:
            predicted_depletion_time = None
    else:
        predicted_levels = []
        predicted_depletion_time = None
    
    return {
        'predicted_battery_levels': predicted_levels.tolist() if hasattr(predicted_levels, 'tolist') else predicted_levels,
        'predicted_depletion_time': float(predicted_depletion_time) if predicted_depletion_time is not None else None,
        'regression_score': float(regression_score),
        'trend': trend,
        'slope': float(slope),
        'intercept': float(model.intercept_)
    }


def analyze_battery_by_flight_phase(df: pd.DataFrame,
                                   battery_col: str = 'battery_percent',
                                   time_col: str = 'timestamp',
                                   phases: List[Dict] = None) -> Dict[str, Any]:
    """
    Analyze battery consumption by flight phases.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        battery_col (str): Name of the battery column
        time_col (str): Name of the timestamp column
        phases (List[Dict]): List of flight phases with start/end indices
        
    Returns:
        Dict[str, Any]: Battery analysis by flight phases
    """
    if battery_col not in df.columns or not phases:
        return {'phase_analysis': {}, 'most_consuming_phase': None, 'least_consuming_phase': None}
    
    phase_analysis = {}
    
    for phase in phases:
        phase_name = phase['phase']
        start_idx = phase['start_index']
        end_idx = phase['end_index']
        
        # Extract phase data
        phase_data = df.iloc[start_idx:end_idx + 1]
        
        if len(phase_data) < 2:
            continue
        
        # Calculate battery consumption for this phase
        initial_battery = phase_data[battery_col].iloc[0]
        final_battery = phase_data[battery_col].iloc[-1]
        consumption = initial_battery - final_battery
        
        # Calculate phase duration
        if time_col in phase_data.columns and pd.api.types.is_datetime64_any_dtype(phase_data[time_col]):
            duration_seconds = (phase_data[time_col].iloc[-1] - phase_data[time_col].iloc[0]).total_seconds()
            duration_minutes = duration_seconds / 60
        else:
            duration_minutes = len(phase_data)
        
        # Calculate consumption rate
        consumption_rate = consumption / duration_minutes if duration_minutes > 0 else 0
        
        phase_analysis[phase_name] = {
            'consumption_percent': float(consumption),
            'duration_minutes': float(duration_minutes),
            'consumption_rate_per_minute': float(consumption_rate),
            'start_battery': float(initial_battery),
            'end_battery': float(final_battery)
        }
    
    # Find most and least consuming phases
    if phase_analysis:
        most_consuming_phase = max(phase_analysis.items(), key=lambda x: x[1]['consumption_rate_per_minute'])
        least_consuming_phase = min(phase_analysis.items(), key=lambda x: x[1]['consumption_rate_per_minute'])
    else:
        most_consuming_phase = None
        least_consuming_phase = None
    
    return {
        'phase_analysis': phase_analysis,
        'most_consuming_phase': most_consuming_phase,
        'least_consuming_phase': least_consuming_phase
    }


def comprehensive_battery_analysis(df: pd.DataFrame,
                                  battery_col: str = 'battery_percent',
                                  time_col: str = 'timestamp',
                                  phases: List[Dict] = None) -> Dict[str, Any]:
    """
    Perform comprehensive battery analysis.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        battery_col (str): Name of the battery column
        time_col (str): Name of the timestamp column
        phases (List[Dict]): List of flight phases
        
    Returns:
        Dict[str, Any]: Comprehensive battery analysis results
    """
    analysis = {}
    
    # Basic consumption metrics
    analysis['consumption_metrics'] = calculate_battery_consumption_rate(df, battery_col, time_col)
    
    # Remaining flight time estimation
    analysis['remaining_time'] = estimate_remaining_flight_time(df, battery_col, time_col)
    
    # Battery efficiency
    analysis['efficiency'] = analyze_battery_efficiency(df, battery_col)
    
    # Anomaly detection
    analysis['anomalies'] = detect_battery_anomalies(df, battery_col, time_col)
    
    # Prediction
    analysis['prediction'] = predict_battery_end_of_flight(df, battery_col, time_col)
    
    # Phase-based analysis
    if phases:
        analysis['phase_analysis'] = analyze_battery_by_flight_phase(df, battery_col, time_col, phases)
    
    # Overall assessment
    consumption_rate = analysis['consumption_metrics']['consumption_rate_percent_per_minute']
    anomaly_rate = analysis['anomalies']['anomaly_rate']
    
    if consumption_rate < 2 and anomaly_rate < 0.05:
        assessment = "Excellent - Low consumption rate, no anomalies"
    elif consumption_rate < 5 and anomaly_rate < 0.1:
        assessment = "Good - Moderate consumption rate, few anomalies"
    elif consumption_rate < 10 and anomaly_rate < 0.2:
        assessment = "Fair - High consumption rate, some anomalies"
    else:
        assessment = "Poor - Very high consumption rate or many anomalies"
    
    analysis['overall_assessment'] = assessment
    
    return analysis


def format_battery_summary(analysis: Dict[str, Any]) -> str:
    """
    Format battery analysis results into a readable summary.
    
    Args:
        analysis (Dict[str, Any]): Results from battery analysis
        
    Returns:
        str: Formatted battery summary
    """
    summary = []
    
    # Consumption metrics
    consumption = analysis['consumption_metrics']
    summary.append(f"Battery Drain Rate: {consumption['consumption_rate_percent_per_minute']:.1f} %/min")
    summary.append(f"Total Consumption: {consumption['total_consumption']:.1f}%")
    
    # Remaining time
    remaining = analysis['remaining_time']
    summary.append(f"Remaining Flight Time: {remaining['remaining_flight_time_minutes']:.1f} minutes")
    summary.append(f"Current Battery Level: {remaining['current_battery_level']:.1f}%")
    
    # Efficiency
    efficiency = analysis['efficiency']
    summary.append(f"Altitude per %: {efficiency['altitude_per_percent']:.2f} m/%")
    summary.append(f"Distance per %: {efficiency['distance_per_percent']:.0f} m/%")
    
    # Anomalies
    anomalies = analysis['anomalies']
    if anomalies['total_anomalies'] > 0:
        summary.append(f"⚠️ {anomalies['total_anomalies']} battery anomalies detected")
    
    # Overall assessment
    summary.append(f"Assessment: {analysis['overall_assessment']}")
    
    return "\n".join(summary)
