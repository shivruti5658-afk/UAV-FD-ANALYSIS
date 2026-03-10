import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
from scipy import signal
from sklearn.preprocessing import StandardScaler, MinMaxScaler


def handle_missing_values(df: pd.DataFrame, strategy: str = 'interpolate') -> pd.DataFrame:
    """
    Handle missing values in the flight dataset.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        strategy (str): Strategy for handling missing values ('interpolate', 'forward_fill', 'backward_fill', 'drop')
        
    Returns:
        pd.DataFrame: DataFrame with handled missing values
    """
    df_clean = df.copy()
    
    if strategy == 'interpolate':
        # Linear interpolation for numeric columns
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
        df_clean[numeric_cols] = df_clean[numeric_cols].interpolate(method='linear')
        
        # Forward fill for remaining NaN values
        df_clean = df_clean.ffill()
        df_clean = df_clean.bfill()
        
    elif strategy == 'forward_fill':
        df_clean = df_clean.ffill()
        
    elif strategy == 'backward_fill':
        df_clean = df_clean.bfill()
        
    elif strategy == 'drop':
        df_clean = df_clean.dropna()
    
    return df_clean


def smooth_sensor_noise(df: pd.DataFrame, columns: Optional[list] = None, 
                       method: str = 'savgol', window_size: int = 5) -> pd.DataFrame:
    """
    Apply smoothing to reduce sensor noise.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        columns (list, optional): Columns to smooth. If None, smooth all numeric columns
        method (str): Smoothing method ('savgol', 'moving_average', 'exponential')
        window_size (int): Window size for smoothing
        
    Returns:
        pd.DataFrame: DataFrame with smoothed data
    """
    df_smooth = df.copy()
    
    if columns is None:
        columns = df_smooth.select_dtypes(include=[np.number]).columns.tolist()
    
    for col in columns:
        if col in df_smooth.columns:
            if method == 'savgol':
                # Savitzky-Golay filter
                if len(df_smooth[col]) >= window_size:
                    df_smooth[col] = signal.savgol_filter(df_smooth[col], window_size, 3)
                    
            elif method == 'moving_average':
                # Moving average
                df_smooth[col] = df_smooth[col].rolling(window=window_size, center=True).mean()
                df_smooth[col] = df_smooth[col].bfill().ffill()
                
            elif method == 'exponential':
                # Exponential smoothing
                df_smooth[col] = df_smooth[col].ewm(span=window_size).mean()
    
    return df_smooth


def normalize_data(df: pd.DataFrame, columns: Optional[list] = None, 
                  method: str = 'standard') -> pd.DataFrame:
    """
    Normalize numerical data.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        columns (list, optional): Columns to normalize. If None, normalize all numeric columns
        method (str): Normalization method ('standard', 'minmax')
        
    Returns:
        pd.DataFrame: DataFrame with normalized data
    """
    df_norm = df.copy()
    
    if columns is None:
        columns = df_norm.select_dtypes(include=[np.number]).columns.tolist()
    
    if method == 'standard':
        scaler = StandardScaler()
    elif method == 'minmax':
        scaler = MinMaxScaler()
    else:
        raise ValueError("Method must be 'standard' or 'minmax'")
    
    df_norm[columns] = scaler.fit_transform(df_norm[columns])
    
    return df_norm, scaler


def compute_time_series_features(df: pd.DataFrame, time_col: str = 'timestamp') -> pd.DataFrame:
    """
    Compute time-based features for analysis.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        time_col (str): Name of the time column
        
    Returns:
        pd.DataFrame: DataFrame with added time series features
    """
    df_ts = df.copy()
    
    # Convert timestamp to datetime if not already
    if not pd.api.types.is_datetime64_any_dtype(df_ts[time_col]):
        df_ts[time_col] = pd.to_datetime(df_ts[time_col])
    
    # Sort by timestamp
    df_ts = df_ts.sort_values(time_col).reset_index(drop=True)
    
    # Calculate time differences
    df_ts['time_delta'] = df_ts[time_col].diff().dt.total_seconds()
    df_ts['time_elapsed'] = (df_ts[time_col] - df_ts[time_col].iloc[0]).dt.total_seconds()
    
    # Calculate derivatives for key metrics
    numeric_cols = ['altitude_m', 'speed_mps', 'battery_percent']
    for col in numeric_cols:
        if col in df_ts.columns:
            # First derivative (rate of change)
            # Avoid division by zero
            time_delta_safe = df_ts['time_delta'].replace(0, np.nan)
            df_ts[f'{col}_rate'] = df_ts[col].diff() / time_delta_safe
            
            # Second derivative (acceleration)
            # Avoid division by zero
            time_delta_safe = df_ts['time_delta'].replace(0, np.nan)
            df_ts[f'{col}_accel'] = df_ts[f'{col}_rate'].diff() / time_delta_safe
    
    # Fill NaN values created by differencing
    df_ts = df_ts.bfill().fillna(0)
    
    return df_ts


def remove_outliers(df: pd.DataFrame, columns: Optional[list] = None, 
                   method: str = 'iqr', threshold: float = 1.5) -> pd.DataFrame:
    """
    Remove outliers from the dataset.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        columns (list, optional): Columns to check for outliers
        method (str): Outlier detection method ('iqr', 'zscore')
        threshold (float): Threshold for outlier detection
        
    Returns:
        pd.DataFrame: DataFrame with outliers removed
    """
    df_clean = df.copy()
    
    if columns is None:
        columns = df_clean.select_dtypes(include=[np.number]).columns.tolist()
    
    for col in columns:
        if col in df_clean.columns:
            if method == 'iqr':
                Q1 = df_clean[col].quantile(0.25)
                Q3 = df_clean[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                
                # Remove outliers
                df_clean = df_clean[(df_clean[col] >= lower_bound) & (df_clean[col] <= upper_bound)]
                
            elif method == 'zscore':
                z_scores = np.abs((df_clean[col] - df_clean[col].mean()) / df_clean[col].std())
                df_clean = df_clean[z_scores < threshold]
    
    return df_clean


def preprocess_pipeline(df: pd.DataFrame, config: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
    """
    Complete preprocessing pipeline for flight data.
    
    Args:
        df (pd.DataFrame): Raw flight data DataFrame
        config (Dict[str, Any], optional): Configuration parameters for preprocessing
        
    Returns:
        pd.DataFrame: Fully preprocessed flight data
    """
    if config is None:
        config = {
            'missing_strategy': 'interpolate',
            'smoothing_method': 'savgol',
            'smoothing_window': 5,
            'normalization_method': 'standard',
            'outlier_method': 'iqr',
            'outlier_threshold': 1.5
        }
    
    # Step 1: Handle missing values
    df_processed = handle_missing_values(df, config['missing_strategy'])
    
    # Step 2: Remove outliers
    df_processed = remove_outliers(df_processed, method=config['outlier_method'], 
                                   threshold=config['outlier_threshold'])
    
    # Step 3: Smooth sensor noise
    sensor_cols = ['altitude_m', 'speed_mps', 'roll_deg', 'pitch_deg', 'yaw_deg']
    df_processed = smooth_sensor_noise(df_processed, sensor_cols, 
                                      config['smoothing_method'], config['smoothing_window'])
    
    # Step 4: Compute time series features
    if 'timestamp' in df_processed.columns:
        df_processed = compute_time_series_features(df_processed)
    
    return df_processed
