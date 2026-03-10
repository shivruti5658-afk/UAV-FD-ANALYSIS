import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
from scipy import stats
from scipy.signal import find_peaks


def calculate_attitude_stability(df: pd.DataFrame, 
                                roll_col: str = 'roll_deg', 
                                pitch_col: str = 'pitch_deg',
                                yaw_col: str = 'yaw_deg') -> Dict[str, Any]:
    """
    Calculate attitude stability metrics.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        roll_col (str): Name of the roll column
        pitch_col (str): Name of the pitch column
        yaw_col (str): Name of the yaw column
        
    Returns:
        Dict[str, Any]: Attitude stability metrics
    """
    stability_metrics = {}
    
    # Roll stability
    if roll_col in df.columns:
        roll_std = df[roll_col].std()
        roll_var = df[roll_col].var()
        roll_range = df[roll_col].max() - df[roll_col].min()
        
        stability_metrics['roll'] = {
            'std_dev': float(roll_std),
            'variance': float(roll_var),
            'range': float(roll_range),
            'mean': float(df[roll_col].mean())
        }
    else:
        stability_metrics['roll'] = {'std_dev': 0, 'variance': 0, 'range': 0, 'mean': 0}
    
    # Pitch stability
    if pitch_col in df.columns:
        pitch_std = df[pitch_col].std()
        pitch_var = df[pitch_col].var()
        pitch_range = df[pitch_col].max() - df[pitch_col].min()
        
        stability_metrics['pitch'] = {
            'std_dev': float(pitch_std),
            'variance': float(pitch_var),
            'range': float(pitch_range),
            'mean': float(df[pitch_col].mean())
        }
    else:
        stability_metrics['pitch'] = {'std_dev': 0, 'variance': 0, 'range': 0, 'mean': 0}
    
    # Yaw stability
    if yaw_col in df.columns:
        yaw_std = df[yaw_col].std()
        yaw_var = df[yaw_col].var()
        yaw_range = df[yaw_col].max() - df[yaw_col].min()
        
        stability_metrics['yaw'] = {
            'std_dev': float(yaw_std),
            'variance': float(yaw_var),
            'range': float(yaw_range),
            'mean': float(df[yaw_col].mean())
        }
    else:
        stability_metrics['yaw'] = {'std_dev': 0, 'variance': 0, 'range': 0, 'mean': 0}
    
    return stability_metrics


def calculate_stability_index(df: pd.DataFrame,
                            roll_col: str = 'roll_deg',
                            pitch_col: str = 'pitch_deg') -> Dict[str, float]:
    """
    Calculate overall stability index.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        roll_col (str): Name of the roll column
        pitch_col (str): Name of the pitch column
        
    Returns:
        Dict[str, float]: Stability indices
    """
    stability_indices = {}
    
    # Get standard deviations
    roll_std = df[roll_col].std() if roll_col in df.columns else 0
    pitch_std = df[pitch_col].std() if pitch_col in df.columns else 0
    
    # Calculate stability index (inverse of combined standard deviation)
    if roll_std + pitch_std > 0:
        stability_index = 1 / (roll_std + pitch_std)
    else:
        stability_index = float('inf')  # Perfect stability
    
    # Normalize to 0-1 scale (assuming typical UAV operations)
    normalized_index = min(stability_index / 0.1, 1.0)  # 0.1 is a reasonable baseline
    
    stability_indices = {
        'stability_index': float(stability_index),
        'normalized_stability_index': float(normalized_index),
        'roll_std': float(roll_std),
        'pitch_std': float(pitch_std)
    }
    
    return stability_indices


def detect_attitude_oscillations(df: pd.DataFrame,
                                 roll_col: str = 'roll_deg',
                                 pitch_col: str = 'pitch_deg',
                                 min_prominence: float = 2.0) -> Dict[str, Any]:
    """
    Detect oscillations in attitude data.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        roll_col (str): Name of the roll column
        pitch_col (str): Name of the pitch column
        min_prominence (float): Minimum prominence for peak detection
        
    Returns:
        Dict[str, Any]: Oscillation detection results
    """
    oscillations = {}
    
    for col_name, col in [('roll', roll_col), ('pitch', pitch_col)]:
        if col in df.columns:
            # Find peaks and troughs
            peaks, _ = find_peaks(df[col], prominence=min_prominence)
            troughs, _ = find_peaks(-df[col], prominence=min_prominence)
            
            # Calculate oscillation frequency
            total_oscillations = len(peaks) + len(troughs)
            if 'timestamp' in df.columns and len(df) > 1:
                flight_duration = (df['timestamp'].max() - df['timestamp'].min()).total_seconds()
                oscillation_frequency = total_oscillations / flight_duration if flight_duration > 0 else 0
            else:
                oscillation_frequency = 0
            
            oscillations[col_name] = {
                'num_peaks': len(peaks),
                'num_troughs': len(troughs),
                'total_oscillations': total_oscillations,
                'oscillation_frequency': float(oscillation_frequency),
                'peak_indices': peaks.tolist() if len(peaks) > 0 else [],
                'trough_indices': troughs.tolist() if len(troughs) > 0 else []
            }
        else:
            oscillations[col_name] = {
                'num_peaks': 0, 'num_troughs': 0, 'total_oscillations': 0,
                'oscillation_frequency': 0, 'peak_indices': [], 'trough_indices': []
            }
    
    return oscillations


def calculate_altitude_stability(df: pd.DataFrame,
                                alt_col: str = 'altitude_m',
                                time_col: str = 'time_elapsed') -> Dict[str, float]:
    """
    Calculate altitude stability metrics.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        alt_col (str): Name of the altitude column
        time_col (str): Name of the time elapsed column
        
    Returns:
        Dict[str, float]: Altitude stability metrics
    """
    if alt_col not in df.columns:
        return {
            'altitude_std': 0, 'altitude_variance': 0,
            'altitude_stability_index': 0, 'holding_accuracy': 0
        }
    
    altitude_std = df[alt_col].std()
    altitude_variance = df[alt_col].var()
    
    # Calculate altitude stability index (inverse of variance)
    altitude_stability_index = 1 / (altitude_variance + 1e-6)  # Add small value to avoid division by zero
    
    # Calculate holding accuracy (how well UAV maintains altitude)
    if len(df) > 1:
        target_altitude = df[alt_col].median()
        altitude_deviations = np.abs(df[alt_col] - target_altitude)
        holding_accuracy = 1 - (altitude_deviations.mean() / target_altitude) if target_altitude > 0 else 0
        holding_accuracy = max(0, holding_accuracy)  # Ensure non-negative
    else:
        holding_accuracy = 0
    
    return {
        'altitude_std': float(altitude_std),
        'altitude_variance': float(altitude_variance),
        'altitude_stability_index': float(altitude_stability_index),
        'holding_accuracy': float(holding_accuracy)
    }


def calculate_speed_stability(df: pd.DataFrame,
                            speed_col: str = 'speed_mps') -> Dict[str, float]:
    """
    Calculate speed stability metrics.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        speed_col (str): Name of the speed column
        
    Returns:
        Dict[str, float]: Speed stability metrics
    """
    if speed_col not in df.columns:
        return {
            'speed_std': 0, 'speed_variance': 0,
            'speed_stability_index': 0, 'speed_consistency': 0
        }
    
    speed_std = df[speed_col].std()
    speed_variance = df[speed_col].var()
    speed_mean = df[speed_col].mean()
    
    # Calculate speed stability index
    speed_stability_index = 1 / (speed_std + 1e-6)
    
    # Calculate speed consistency (coefficient of variation)
    speed_consistency = 1 - (speed_std / speed_mean) if speed_mean > 0 else 0
    speed_consistency = max(0, speed_consistency)
    
    return {
        'speed_std': float(speed_std),
        'speed_variance': float(speed_variance),
        'speed_stability_index': float(speed_stability_index),
        'speed_consistency': float(speed_consistency)
    }


def assess_flight_stability(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Comprehensive flight stability assessment.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        
    Returns:
        Dict[str, Any]: Complete stability assessment
    """
    assessment = {}
    
    # Attitude stability
    assessment['attitude_stability'] = calculate_attitude_stability(df)
    
    # Overall stability index
    assessment['stability_indices'] = calculate_stability_index(df)
    
    # Oscillation detection
    assessment['oscillations'] = detect_attitude_oscillations(df)
    
    # Altitude stability
    assessment['altitude_stability'] = calculate_altitude_stability(df)
    
    # Speed stability
    assessment['speed_stability'] = calculate_speed_stability(df)
    
    # Overall stability rating
    stability_score = assessment['stability_indices']['normalized_stability_index']
    
    if stability_score >= 0.8:
        stability_rating = "Excellent"
        color = "green"
    elif stability_score >= 0.6:
        stability_rating = "Good"
        color = "yellow"
    elif stability_score >= 0.4:
        stability_rating = "Fair"
        color = "orange"
    else:
        stability_rating = "Poor"
        color = "red"
    
    assessment['overall_rating'] = {
        'score': stability_score,
        'rating': stability_rating,
        'color': color
    }
    
    return assessment


def generate_stability_recommendations(assessment: Dict[str, Any]) -> List[str]:
    """
    Generate recommendations based on stability analysis.
    
    Args:
        assessment (Dict[str, Any]): Stability assessment results
        
    Returns:
        List[str]: List of recommendations
    """
    recommendations = []
    
    # Check attitude stability
    roll_std = assessment['attitude_stability']['roll']['std_dev']
    pitch_std = assessment['attitude_stability']['pitch']['std_dev']
    
    if roll_std > 5:
        recommendations.append("Consider adjusting roll PID gains to reduce roll oscillations")
    
    if pitch_std > 5:
        recommendations.append("Consider adjusting pitch PID gains to reduce pitch oscillations")
    
    # Check oscillations
    total_oscillations = assessment['oscillations']['roll']['total_oscillations'] + \
                        assessment['oscillations']['pitch']['total_oscillations']
    
    if total_oscillations > 10:
        recommendations.append("High oscillation detected - review control system tuning")
    
    # Check altitude stability
    holding_accuracy = assessment['altitude_stability']['holding_accuracy']
    if holding_accuracy < 0.8:
        recommendations.append("Improve altitude hold performance - check barometer/altimeter calibration")
    
    # Check speed stability
    speed_consistency = assessment['speed_stability']['speed_consistency']
    if speed_consistency < 0.8:
        recommendations.append("Improve speed control - review throttle response and wind compensation")
    
    # Overall recommendations
    overall_score = assessment['overall_rating']['score']
    if overall_score < 0.5:
        recommendations.append("Overall stability is poor - comprehensive system review recommended")
        recommendations.append("Check for mechanical issues, sensor calibration, and environmental factors")
    
    if not recommendations:
        recommendations.append("Flight stability appears acceptable - continue monitoring")
    
    return recommendations


def format_stability_summary(assessment: Dict[str, Any]) -> str:
    """
    Format stability assessment into a readable summary.
    
    Args:
        assessment (Dict[str, Any]): Stability assessment results
        
    Returns:
        str: Formatted stability summary
    """
    summary = []
    
    # Overall rating
    overall = assessment['overall_rating']
    summary.append(f"Stability Index: {overall['score']:.2f}")
    summary.append(f"Status: {overall['rating']} Flight")
    
    # Attitude stability
    attitude = assessment['attitude_stability']
    summary.append(f"Roll Std Dev: {attitude['roll']['std_dev']:.2f}°")
    summary.append(f"Pitch Std Dev: {attitude['pitch']['std_dev']:.2f}°")
    
    # Oscillations
    osc = assessment['oscillations']
    total_osc = osc['roll']['total_oscillations'] + osc['pitch']['total_oscillations']
    summary.append(f"Total Oscillations: {total_osc}")
    
    # Altitude stability
    alt_stab = assessment['altitude_stability']
    summary.append(f"Altitude Holding Accuracy: {alt_stab['holding_accuracy']:.2%}")
    
    return "\n".join(summary)
