"""
Official ULG (UAV Log) to CSV Converter
Uses only the official pyulog tool from PX4 Autopilot
"""

import pandas as pd
import numpy as np
import os
import subprocess
import tempfile
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ULGConverter:
    """Official ULG to CSV converter using pyulog only"""
    
    def __init__(self):
        self.required_columns = [
            'timestamp', 'altitude_m', 'speed_mps', 
            'roll_deg', 'pitch_deg', 'yaw_deg',
            'battery_percent', 'gps_lat', 'gps_lon'
        ]
        
        # Check if pyulog is available
        self.pyulog_available = self._check_pyulog_availability()
        
    def _check_pyulog_availability(self) -> bool:
        """Check if pyulog command-line tool is available"""
        try:
            result = subprocess.run(['ulog2csv', '--help'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                logger.info("✅ Official pyulog tool (ulog2csv) is available")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # Try importing pyulog Python library
        try:
            import pyulog
            logger.info("✅ pyulog Python library is available")
            return True
        except ImportError:
            pass
        
        logger.error("❌ pyulog not found. Please install: pip install pyulog")
        return False
    
    def convert_ulg_to_csv(self, ulg_file_path: str, csv_output_path: str) -> str:
        """
        Convert ULG file to CSV format using official pyulog only
        
        Args:
            ulg_file_path (str): Path to input ULG file
            csv_output_path (str): Path to output CSV file
            
        Returns:
            str: Path to generated CSV file
        """
        try:
            logger.info(f"Converting ULG file: {ulg_file_path}")
            
            # Validate pyulog availability
            if not self.pyulog_available:
                raise RuntimeError(
                    "pyulog is not available. Please install it with: pip install pyulog\n"
                    "This is required for ULG conversion as it's the official PX4 tool."
                )
            
            # Validate input file
            if not os.path.exists(ulg_file_path):
                raise FileNotFoundError(f"ULG file not found: {ulg_file_path}")
            
            # Convert using official pyulog method
            df = self._convert_with_pyulog(ulg_file_path)
            
            if df is None or len(df) == 0:
                raise RuntimeError("pyulog conversion failed - no data extracted")
            
            # Ensure output directory exists
            output_dir = os.path.dirname(csv_output_path)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            
            # Save to CSV
            df.to_csv(csv_output_path, index=False)
            
            logger.info(f"✅ Successfully converted to CSV: {csv_output_path}")
            logger.info(f"📊 Generated {len(df)} data points using official pyulog")
            
            return csv_output_path
            
        except Exception as e:
            logger.error(f"❌ Error converting ULG to CSV: {e}")
            raise
    
    def _convert_with_pyulog(self, ulg_file_path: str) -> pd.DataFrame:
        """
        Convert ULG file using official pyulog tool
        This is the standard method used by PX4 developers
        """
        try:
            # Method 1: Try command-line ulog2csv tool first
            csv_files = self._try_commandline_pyulog(ulg_file_path)
            if csv_files:
                return self._load_pyulog_csv_files(csv_files)
            
            # Method 2: Try Python pyulog library
            return self._try_python_pyulog(ulg_file_path)
                
        except Exception as e:
            logger.error(f"pyulog conversion failed: {e}")
            raise
    
    def _try_commandline_pyulog(self, ulg_file_path: str) -> dict:
        """Try using command-line ulog2csv tool"""
        try:
            # Convert path to forward slashes for compatibility
            ulg_file_path_fixed = ulg_file_path.replace('\\', '/')
            
            with tempfile.TemporaryDirectory() as temp_dir:
                # Run ulog2csv command with fixed path
                result = subprocess.run([
                    'ulog2csv', ulg_file_path_fixed
                ], 
                cwd=temp_dir,  # Output files will be created here
                capture_output=True, 
                text=True, 
                timeout=30
                )
                
                if result.returncode == 0:
                    logger.info("✅ ulog2csv command executed successfully")
                    
                    # Find generated CSV files
                    csv_files = {}
                    expected_files = [
                        'vehicle_local_position.csv',
                        'vehicle_attitude.csv', 
                        'battery_status.csv',
                        'vehicle_gps_position.csv'
                    ]
                    
                    for file in expected_files:
                        file_path = os.path.join(temp_dir, file)
                        if os.path.exists(file_path):
                            csv_files[file.replace('.csv', '')] = file_path
                    
                    if csv_files:
                        logger.info(f"Found {len(csv_files)} CSV files from ulog2csv")
                        return csv_files
                    else:
                        logger.warning("No CSV files generated by ulog2csv")
                        return None
                else:
                    logger.warning(f"ulog2csv failed: {result.stderr}")
                    return None
                    
        except subprocess.TimeoutExpired:
            logger.warning("ulog2csv command timed out")
            return None
        except Exception as e:
            logger.warning(f"ulog2csv command error: {e}")
            return None
    
    def _try_python_pyulog(self, ulg_file_path: str) -> pd.DataFrame:
        """Try using Python pyulog library"""
        try:
            import pyulog
            
            # Load ULG file
            ulog = pyulog.ULog(ulg_file_path)
            
            # Diagnostics: Check what datasets are available
            logger.info(f"🔍 Available datasets in ULG file:")
            try:
                all_datasets = ulog.get_dataset_names()
            except AttributeError:
                # Fallback for different pyulog versions
                try:
                    all_datasets = ulog.data_list
                    logger.info("🔧 Using data_list attribute (older pyulog version)")
                except AttributeError:
                    # Try to get datasets from the ulog object directly
                    all_datasets = []
                    try:
                        for name in dir(ulog):
                            if not name.startswith('_') and hasattr(ulog, name):
                                attr = getattr(ulog, name)
                                if hasattr(attr, 'data') and hasattr(attr, 'name'):
                                    all_datasets.append(attr.name)
                        logger.info("🔧 Using attribute inspection for datasets")
                    except:
                        all_datasets = []
                        logger.warning("⚠️ Could not determine available datasets")
            
            if all_datasets:
                for dataset_name in all_datasets:
                    logger.info(f"   - {dataset_name}")
            else:
                logger.warning("⚠️ No datasets found or could not enumerate")
            
            # Extract required datasets with fallback options
            required_datasets = [
                'vehicle_local_position',    # altitude, velocity
                'vehicle_attitude',          # roll, pitch, yaw
                'battery_status',           # battery data
                'vehicle_gps_position'      # GPS coordinates
            ]
            
            # Alternative dataset names for different firmwares
            alternative_datasets = {
                'vehicle_local_position': ['vehicle_local_position_0', 'local_position', 'position'],
                'vehicle_attitude': ['vehicle_attitude_0', 'attitude', 'vehicle_attitude_groundframe'],
                'battery_status': ['battery_status_0', 'battery', 'system_power'],
                'vehicle_gps_position': ['vehicle_gps_position_0', 'gps_position', 'gps']
            }
            
            data_frames = {}
            
            for primary_name in required_datasets:
                datasets_to_try = [primary_name] + alternative_datasets.get(primary_name, [])
                dataset_found = False
                
                for dataset_name in datasets_to_try:
                    try:
                        # Try different methods to get dataset
                        dataset = None
                        
                        # Method 1: get_dataset (newer pyulog)
                        try:
                            dataset = ulog.get_dataset(dataset_name)
                        except:
                            pass
                        
                        # Method 2: Access from data_list (older pyulog)
                        if dataset is None and hasattr(ulog, 'data_list'):
                            for data_item in ulog.data_list:
                                if hasattr(data_item, 'name') and data_item.name == dataset_name:
                                    dataset = data_item
                                    break
                        
                        # Method 3: Direct attribute access
                        if dataset is None and hasattr(ulog, dataset_name):
                            dataset = getattr(ulog, dataset_name)
                        
                        if dataset:
                            # Try different methods to get data
                            df = None
                            
                            # Method 1: dataset.data
                            if hasattr(dataset, 'data'):
                                df = dataset.data
                            
                            # Method 2: dataset.list
                            elif hasattr(dataset, 'list'):
                                df = pd.DataFrame(dataset.list)
                            
                            # Method 3: Convert to DataFrame manually
                            elif hasattr(dataset, '__dict__'):
                                data_dict = {}
                                for key, value in dataset.__dict__.items():
                                    if isinstance(value, list) and len(value) > 0:
                                        data_dict[key] = value
                                if data_dict:
                                    df = pd.DataFrame(data_dict)
                            
                            if df is not None and not df.empty:
                                data_frames[primary_name] = df
                                logger.info(f"✅ Loaded dataset: {dataset_name} -> {primary_name} ({len(df)} points)")
                                dataset_found = True
                                break
                                
                    except Exception as e:
                        logger.debug(f"Could not load dataset {dataset_name}: {e}")
                        continue
                
                if not dataset_found:
                    logger.warning(f"⚠️ No suitable dataset found for {primary_name}")
            
            # If no required datasets, try to extract ANY available dataset
            if not data_frames:
                logger.info("🔧 Attempting to extract from available datasets...")
                
                for dataset_name in all_datasets:
                    try:
                        data = ulog.get_dataset(dataset_name)
                        if data:
                            df = data.data
                            if not df.empty and len(df) > 10:  # Must have some data
                                # Try to map to our required columns
                                mapped_df = self._map_dataset_to_standard(df, dataset_name)
                                if mapped_df is not None:
                                    data_frames[dataset_name] = mapped_df
                                    logger.info(f"✅ Mapped dataset: {dataset_name} ({len(df)} points)")
                                    break
                    except Exception as e:
                        logger.debug(f"Could not process dataset {dataset_name}: {e}")
                        continue
            
            # Combine datasets into unified DataFrame
            if not data_frames:
                # Provide detailed error message
                logger.error("❌ No valid datasets found in ULG file")
                logger.error("🔍 Possible causes:")
                logger.error("   - ULG file is corrupted or incomplete")
                logger.error("   - File is from a non-PX4 firmware")
                logger.error("   - File contains no flight data")
                logger.error("   - File format is incompatible with pyulog")
                logger.error(f"📋 Available datasets: {all_datasets}")
                raise RuntimeError("No valid datasets found in ULG file")
            
            return self._combine_pyulog_datasets(data_frames)
            
        except ImportError:
            logger.error("pyulog Python library not available")
            raise
        except Exception as e:
            logger.error(f"Python pyulog error: {e}")
            raise
    
    def _map_dataset_to_standard(self, df: pd.DataFrame, dataset_name: str) -> pd.DataFrame:
        """Try to map any dataset to our standard format"""
        try:
            # Get available columns
            available_cols = df.columns.tolist()
            logger.info(f"🔍 Dataset '{dataset_name}' columns: {available_cols}")
            
            # Standard column mapping attempts
            column_mappings = {
                # Timestamp mappings
                'timestamp': ['timestamp', 't', 'time', 'Timestamp'],
                
                # Position mappings
                'altitude_m': ['z', 'altitude', 'alt', 'pos_z', 'position_z', 'baro_alt', 'relative_alt'],
                'gps_lat': ['lat', 'latitude', 'gps_lat'],
                'gps_lon': ['lon', 'lng', 'longitude', 'gps_lon', 'gps_lng'],
                
                # Velocity mappings
                'speed_mps': ['vx', 'velocity_x', 'ground_speed', 'speed', 'horizontal_speed'],
                
                # Attitude mappings
                'roll_deg': ['roll', 'phi', 'roll_deg'],
                'pitch_deg': ['pitch', 'theta', 'pitch_deg'],
                'yaw_deg': ['yaw', 'psi', 'heading', 'yaw_deg', 'course'],
                
                # Battery mappings
                'battery_percent': ['remaining', 'battery_remaining', 'battery', 'voltage', 'current']
            }
            
            # Create standard DataFrame
            standard_df = pd.DataFrame()
            
            # Map timestamp first
            for col_name in column_mappings['timestamp']:
                if col_name in available_cols:
                    standard_df['timestamp'] = df[col_name]
                    break
            
            # If no timestamp, create one
            if 'timestamp' not in standard_df.columns:
                standard_df['timestamp'] = range(len(df))
            
            # Map other columns
            for std_col, possible_cols in column_mappings.items():
                if std_col == 'timestamp':
                    continue
                    
                for col_name in possible_cols:
                    if col_name in available_cols:
                        standard_df[std_col] = df[col_name]
                        break
            
            # Fill missing required columns with defaults
            required_defaults = {
                'altitude_m': 0.0,
                'speed_mps': 0.0,
                'roll_deg': 0.0,
                'pitch_deg': 0.0,
                'yaw_deg': 0.0,
                'battery_percent': 100.0,
                'gps_lat': 0.0,
                'gps_lon': 0.0
            }
            
            for col, default_val in required_defaults.items():
                if col not in standard_df.columns:
                    standard_df[col] = default_val
            
            # Ensure we have at least some flight data (not all zeros)
            non_timestamp_cols = [col for col in self.required_columns if col != 'timestamp']
            has_flight_data = any(standard_df[col].std() > 0.001 for col in non_timestamp_cols)
            
            if has_flight_data:
                logger.info(f"✅ Successfully mapped dataset '{dataset_name}' to standard format")
                return standard_df[self.required_columns]
            else:
                logger.warning(f"⚠️ Dataset '{dataset_name}' appears to contain no flight data")
                return None
                
        except Exception as e:
            logger.error(f"Error mapping dataset '{dataset_name}': {e}")
            return None
    
    def _load_pyulog_csv_files(self, csv_files: dict) -> pd.DataFrame:
        """Load and combine CSV files generated by ulog2csv command"""
        try:
            data_frames = {}
            
            for dataset_name, csv_path in csv_files.items():
                try:
                    df = pd.read_csv(csv_path)
                    if not df.empty:
                        data_frames[dataset_name] = df
                        logger.info(f"✅ Loaded CSV: {dataset_name} ({len(df)} points)")
                except Exception as e:
                    logger.warning(f"Could not read CSV {csv_path}: {e}")
            
            if not data_frames:
                raise RuntimeError("No valid CSV files loaded")
            
            return self._combine_pyulog_datasets(data_frames)
            
        except Exception as e:
            logger.error(f"Error loading pyulog CSV files: {e}")
            raise
    
    def _combine_pyulog_datasets(self, data_frames: dict) -> pd.DataFrame:
        """Combine multiple pyulog datasets into unified DataFrame"""
        try:
            if not data_frames:
                logger.warning("No datasets to combine")
                return None
            
            # Start with attitude data (usually most complete)
            if 'vehicle_attitude' in data_frames:
                result_df = data_frames['vehicle_attitude'].copy()
                
                # Rename columns to our standard format
                column_mapping = {
                    'timestamp': 'timestamp',
                    'roll': 'roll_deg',
                    'pitch': 'pitch_deg', 
                    'yaw': 'yaw_deg'
                }
                
                for old_col, new_col in column_mapping.items():
                    if old_col in result_df.columns:
                        result_df = result_df.rename(columns={old_col: new_col})
            else:
                # Create base DataFrame with timestamps
                first_df = list(data_frames.values())[0]
                result_df = pd.DataFrame({'timestamp': first_df.get('timestamp', [])})
            
            # Merge other datasets
            merge_mappings = {
                'vehicle_local_position': {
                    'timestamp': 'timestamp',
                    'z': 'altitude_m',  # Negative altitude in NED frame
                    'vx': 'speed_mps',  # Use x velocity as speed
                    'vy': 'speed_y_mps',
                    'vz': 'speed_z_mps'
                },
                'battery_status': {
                    'timestamp': 'timestamp',
                    'remaining': 'battery_percent'
                },
                'vehicle_gps_position': {
                    'timestamp': 'timestamp',
                    'lat': 'gps_lat',
                    'lon': 'gps_lon',
                    'alt': 'gps_alt_m'
                }
            }
            
            for dataset_name, df in data_frames.items():
                if dataset_name == 'vehicle_attitude':
                    continue  # Already used as base
                
                if dataset_name in merge_mappings:
                    mapping = merge_mappings[dataset_name]
                    
                    # Select and rename columns
                    merge_df = df[['timestamp'] + [col for col in mapping.keys() if col in df.columns]].copy()
                    merge_df = merge_df.rename(columns=mapping)
                    
                    # Merge on timestamp (nearest match)
                    result_df = pd.merge_asof(result_df, merge_df, on='timestamp', direction='nearest')
            
            # Calculate derived values
            if 'altitude_m' in result_df.columns:
                # Convert NED altitude (negative) to positive altitude
                result_df['altitude_m'] = -result_df['altitude_m']
            
            # Calculate total speed from velocity components if available
            if all(col in result_df.columns for col in ['speed_mps', 'speed_y_mps', 'speed_z_mps']):
                result_df['speed_mps'] = np.sqrt(
                    result_df['speed_mps']**2 + 
                    result_df['speed_y_mps']**2 + 
                    result_df['speed_z_mps']**2
                )
            
            # Ensure all required columns exist
            for col in self.required_columns:
                if col not in result_df.columns:
                    if col == 'timestamp':
                        continue  # Should always exist
                    elif col == 'altitude_m':
                        result_df[col] = 0.0
                    elif col == 'speed_mps':
                        result_df[col] = 0.0
                    elif col in ['roll_deg', 'pitch_deg', 'yaw_deg']:
                        result_df[col] = 0.0
                    elif col == 'battery_percent':
                        result_df[col] = 100.0
                    elif col in ['gps_lat', 'gps_lon']:
                        result_df[col] = 0.0
            
            # Sort by timestamp and drop duplicates
            result_df = result_df.sort_values('timestamp').drop_duplicates(subset=['timestamp'])
            
            # Reset index
            result_df = result_df.reset_index(drop=True)
            
            logger.info(f"✅ Combined datasets: {len(result_df)} total records")
            return result_df[self.required_columns]  # Return only required columns
            
        except Exception as e:
            logger.error(f"Error combining datasets: {e}")
            return None
    
    def batch_convert(self, input_path: str, output_dir: str) -> list:
        """
        Batch convert multiple ULG files using official pyulog only
        
        Args:
            input_path (str): Path to ULG file or directory containing ULG files
            output_dir (str): Directory to save converted CSV files
            
        Returns:
            list: List of converted file paths
        """
        converted_files = []
        
        try:
            # Ensure pyulog is available
            if not self.pyulog_available:
                raise RuntimeError(
                    "pyulog is not available. Please install it with: pip install pyulog\n"
                    "This is required for ULG conversion as it's the official PX4 tool."
                )
            
            # Ensure output directory exists
            os.makedirs(output_dir, exist_ok=True)
            
            if os.path.isfile(input_path):
                # Single file conversion
                if input_path.endswith('.ulg'):
                    output_file = os.path.join(output_dir, 
                                            os.path.splitext(os.path.basename(input_path))[0] + '.csv')
                    self.convert_ulg_to_csv(input_path, output_file)
                    converted_files.append(output_file)
                    
            elif os.path.isdir(input_path):
                # Directory conversion
                ulg_files = []
                for root, dirs, files in os.walk(input_path):
                    for file in files:
                        if file.endswith('.ulg'):
                            ulg_files.append(os.path.join(root, file))
                
                logger.info(f"Found {len(ulg_files)} ULG files to convert")
                
                for ulg_file in ulg_files:
                    try:
                        rel_path = os.path.relpath(ulg_file, input_path)
                        output_file = os.path.join(output_dir, 
                                                os.path.splitext(rel_path)[0] + '.csv')
                        
                        # Create subdirectories if needed
                        os.makedirs(os.path.dirname(output_file), exist_ok=True)
                        
                        self.convert_ulg_to_csv(ulg_file, output_file)
                        converted_files.append(output_file)
                        logger.info(f"✅ Converted: {ulg_file}")
                        
                    except Exception as e:
                        logger.error(f"❌ Failed to convert {ulg_file}: {e}")
                        continue
            else:
                raise FileNotFoundError(f"Input path not found: {input_path}")
            
            logger.info(f"✅ Batch conversion completed: {len(converted_files)} files")
            return converted_files
            
        except Exception as e:
            logger.error(f"❌ Batch conversion error: {e}")
            raise


def main():
    """Main function for command line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Convert ULG files to CSV format using official pyulog tool only',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single file conversion (requires pyulog)
  python ulg_converter.py flight.ulg
  
  # Single file with custom output
  python ulg_converter.py flight.ulg --output flight_data.csv
  
  # Batch conversion directory
  python ulg_converter.py /path/to/ulg/files/ --output /path/to/csv/files/
  
  # Install pyulog first (required)
  pip install pyulog
  
  # Then convert using official PX4 method
  ulog2csv your_log_file.ulg
        """
    )
    
    parser.add_argument('input', help='Input ULG file or directory')
    parser.add_argument('--output', '-o', help='Output CSV file or directory')
    parser.add_argument('--batch', '-b', action='store_true', 
                       help='Batch convert all ULG files in directory')
    
    args = parser.parse_args()
    
    try:
        converter = ULGConverter()
        
        if args.batch or os.path.isdir(args.input):
            # Batch conversion
            output_dir = args.output or 'converted_csv'
            converted_files = converter.batch_convert(args.input, output_dir)
            
            print(f"✅ Batch conversion completed!")
            print(f"📁 Converted {len(converted_files)} files:")
            for f in converted_files:
                print(f"   - {f}")
                
        else:
            # Single file conversion
            output_file = args.output or os.path.splitext(args.input)[0] + '.csv'
            output_path = converter.convert_ulg_to_csv(args.input, output_file)
            
            print(f"✅ ULG file converted successfully!")
            print(f"📁 Output: {output_path}")
            print("🔧 Method: Official pyulog (PX4 standard)")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1


if __name__ == '__main__':
    exit(main())
