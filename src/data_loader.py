import pandas as pd
import os
from typing import Optional, Dict, Any


def load_csv(file_path: str) -> pd.DataFrame:
    """
    Load UAV flight data from CSV file.
    
    Args:
        file_path (str): Path to the CSV file
        
    Returns:
        pd.DataFrame: Loaded flight data
        
    Raises:
        FileNotFoundError: If file doesn't exist
        pd.errors.EmptyDataError: If file is empty
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Data file not found: {file_path}")
    
    try:
        df = pd.read_csv(file_path)
        return df
    except pd.errors.EmptyDataError:
        raise pd.errors.EmptyDataError("CSV file is empty")
    except Exception as e:
        raise Exception(f"Error loading CSV file: {str(e)}")


def validate_dataset(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Validate the UAV flight dataset structure and content.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        
    Returns:
        Dict[str, Any]: Validation results including missing columns and data quality issues
    """
    required_columns = [
        'timestamp', 'altitude_m', 'speed_mps', 'roll_deg', 'pitch_deg', 
        'yaw_deg', 'battery_percent', 'gps_lat', 'gps_lon'
    ]
    
    validation_results = {
        'is_valid': True,
        'missing_columns': [],
        'data_quality_issues': [],
        'dataset_info': {}
    }
    
    # Check for required columns
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        validation_results['missing_columns'] = missing_cols
        validation_results['is_valid'] = False
    
    # Check for empty dataset
    if df.empty:
        validation_results['data_quality_issues'].append("Dataset is empty")
        validation_results['is_valid'] = False
    
    # Check for missing values
    missing_values = df.isnull().sum()
    high_missing_cols = missing_values[missing_values > len(df) * 0.1].index.tolist()
    if high_missing_cols:
        validation_results['data_quality_issues'].append(
            f"High missing values in columns: {high_missing_cols}"
        )
    
    # Dataset info
    validation_results['dataset_info'] = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'columns': df.columns.tolist(),
        'data_types': df.dtypes.to_dict()
    }
    
    return validation_results


def get_dataset_summary(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Get a summary of the flight dataset.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        
    Returns:
        Dict[str, Any]: Dataset summary statistics
    """
    summary = {
        'flight_duration_seconds': 0,
        'altitude_range': {'min': 0, 'max': 0},
        'speed_range': {'min': 0, 'max': 0},
        'battery_range': {'min': 0, 'max': 0},
        'data_points': len(df)
    }
    
    if not df.empty and 'timestamp' in df.columns:
        # Calculate flight duration
        if pd.api.types.is_datetime64_any_dtype(df['timestamp']):
            summary['flight_duration_seconds'] = (
                df['timestamp'].max() - df['timestamp'].min()
            ).total_seconds()
        elif 'timestamp' in df.columns:
            # Try to convert timestamp to datetime
            try:
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                summary['flight_duration_seconds'] = (
                    df['timestamp'].max() - df['timestamp'].min()
                ).total_seconds()
            except:
                pass
    
    # Calculate ranges for key metrics
    for col, range_key in [('altitude_m', 'altitude_range'), 
                           ('speed_mps', 'speed_range'),
                           ('battery_percent', 'battery_range')]:
        if col in df.columns:
            summary[range_key]['min'] = float(df[col].min())
            summary[range_key]['max'] = float(df[col].max())
    
    return summary
