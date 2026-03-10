#!/usr/bin/env python3
"""
Direct ULG Analysis Tool
Analyzes ULG files directly without CSV conversion
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
import logging

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DirectULGAnalyzer:
    """Direct ULG file analyzer - no CSV conversion needed"""
    
    def __init__(self):
        self.flight_data = None
        self.analysis_results = {}
        
    def analyze_ulg_directly(self, ulg_file_path: str):
        """
        Analyze ULG file directly without CSV conversion
        
        Args:
            ulg_file_path: Path to ULG file
            
        Returns:
            dict: Analysis results
        """
        try:
            logger.info(f"🚁 Starting direct ULG analysis: {ulg_file_path}")
            
            # Try pyulog first
            if self._try_pyulog_analysis(ulg_file_path):
                return self.analysis_results
            
            # Fallback to binary analysis
            if self._try_binary_analysis(ulg_file_path):
                return self.analysis_results
            
            raise RuntimeError("Could not analyze ULG file with any method")
            
        except Exception as e:
            logger.error(f"❌ Direct ULG analysis failed: {e}")
            raise
    
    def _try_pyulog_analysis(self, ulg_file_path: str) -> bool:
        """Try to analyze using pyulog directly"""
        try:
            import pyulog
            
            # Load ULG file
            ulog = pyulog.ULog(ulg_file_path)
            logger.info("✅ Loaded ULG with pyulog")
            
            # Get all available datasets
            try:
                datasets = ulog.get_dataset_names()
            except AttributeError:
                # Fallback for different pyulog versions
                datasets = []
                if hasattr(ulog, 'data_list'):
                    datasets = [item.name for item in ulog.data_list if hasattr(item, 'name')]
                else:
                    # Try to find datasets by inspection
                    for name in dir(ulog):
                        if not name.startswith('_') and hasattr(ulog, name):
                            attr = getattr(ulog, name)
                            if hasattr(attr, 'data') and hasattr(attr, 'name'):
                                datasets.append(attr.name)
            
            logger.info(f"📊 Found {len(datasets)} datasets")
            
            # Extract flight data from available datasets
            flight_data = self._extract_flight_data_from_pyulog(ulog, datasets)
            
            if flight_data is not None:
                self.flight_data = flight_data
                self._perform_comprehensive_analysis()
                return True
            else:
                logger.warning("⚠️ Could not extract flight data from pyulog")
                return False
                
        except ImportError:
            logger.info("pyulog not available, trying binary analysis")
            return False
        except Exception as e:
            logger.warning(f"pyulog analysis failed: {e}")
            return False
    
    def _extract_flight_data_from_pyulog(self, ulog, datasets):
        """Extract flight data from pyulog datasets"""
        try:
            # Priority dataset mapping
            dataset_mapping = {
                'attitude': ['vehicle_attitude', 'attitude', 'vehicle_attitude_0'],
                'position': ['vehicle_local_position', 'local_position', 'position'],
                'gps': ['vehicle_gps_position', 'gps_position', 'gps'],
                'battery': ['battery_status', 'battery', 'system_power']
            }
            
            extracted_data = {}
            
            for data_type, possible_names in dataset_mapping.items():
                for name in possible_names:
                    if name in datasets:
                        try:
                            dataset = ulog.get_dataset(name)
                            if dataset and hasattr(dataset, 'data'):
                                df = dataset.data
                                if not df.empty:
                                    extracted_data[data_type] = df
                                    logger.info(f"✅ Extracted {data_type} from {name} ({len(df)} points)")
                                    break
                        except:
                            continue
            
            if not extracted_data:
                logger.warning("No standard datasets found, trying any available dataset...")
                # Try to extract from any dataset that has flight-like data
                for dataset_name in datasets[:10]:  # Try first 10 datasets
                    try:
                        dataset = ulog.get_dataset(dataset_name)
                        if dataset and hasattr(dataset, 'data'):
                            df = dataset.data
                            if not df.empty and len(df) > 100:
                                # Check if it looks like flight data
                                if self._looks_like_flight_data(df):
                                    extracted_data['primary'] = df
                                    logger.info(f"✅ Found flight-like data in {dataset_name}")
                                    break
                    except:
                        continue
            
            if extracted_data:
                return self._create_unified_flight_data(extracted_data)
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error extracting flight data: {e}")
            return None
    
    def _looks_like_flight_data(self, df):
        """Check if DataFrame looks like flight data"""
        try:
            # Check for common flight data columns
            flight_keywords = ['timestamp', 'time', 'roll', 'pitch', 'yaw', 'altitude', 'lat', 'lon', 'battery', 'speed']
            columns_lower = [col.lower() for col in df.columns]
            
            keyword_matches = sum(1 for keyword in flight_keywords if any(keyword in col for col in columns_lower))
            
            # Should have at least some flight-related columns
            return keyword_matches >= 2 and len(df) > 100
            
        except:
            return False
    
    def _create_unified_flight_data(self, extracted_data):
        """Create unified flight data from extracted datasets"""
        try:
            # Start with the most complete dataset
            primary_df = None
            
            # Priority order for primary dataset
            priority = ['attitude', 'position', 'primary', 'gps', 'battery']
            
            for data_type in priority:
                if data_type in extracted_data:
                    primary_df = extracted_data[data_type]
                    break
            
            if primary_df is None:
                primary_df = list(extracted_data.values())[0]
            
            # Standardize column names
            standardized_df = self._standardize_columns(primary_df)
            
            # Add data from other datasets
            for data_type, df in extracted_data.items():
                if data_type != priority[0]:  # Skip primary if already used
                    standardized_df = self._merge_datasets(standardized_df, df)
            
            logger.info(f"✅ Created unified flight data: {len(standardized_df)} records")
            return standardized_df
            
        except Exception as e:
            logger.error(f"Error creating unified data: {e}")
            return None
    
    def _standardize_columns(self, df):
        """Standardize column names to our format"""
        try:
            column_mapping = {
                # Timestamp
                'timestamp': 'timestamp', 't': 'timestamp', 'time': 'timestamp',
                
                # Attitude
                'roll': 'roll_deg', 'phi': 'roll_deg', 'roll_deg': 'roll_deg',
                'pitch': 'pitch_deg', 'theta': 'pitch_deg', 'pitch_deg': 'pitch_deg',
                'yaw': 'yaw_deg', 'psi': 'yaw_deg', 'yaw_deg': 'yaw_deg', 'heading': 'yaw_deg',
                
                # Position
                'z': 'altitude_m', 'altitude': 'altitude_m', 'alt': 'altitude_m',
                'lat': 'gps_lat', 'latitude': 'gps_lat',
                'lon': 'gps_lon', 'lng': 'gps_lon', 'longitude': 'gps_lon',
                
                # Velocity
                'vx': 'speed_mps', 'velocity_x': 'speed_mps', 'speed': 'speed_mps',
                
                # Battery
                'remaining': 'battery_percent', 'battery': 'battery_percent', 'voltage': 'battery_percent'
            }
            
            standardized = df.copy()
            
            # Apply column mapping
            for old_name, new_name in column_mapping.items():
                if old_name in standardized.columns:
                    standardized = standardized.rename(columns={old_name: new_name})
            
            # Ensure required columns exist
            required_columns = ['timestamp', 'altitude_m', 'speed_mps', 'roll_deg', 'pitch_deg', 'yaw_deg', 'battery_percent', 'gps_lat', 'gps_lon']
            
            for col in required_columns:
                if col not in standardized.columns:
                    if col == 'timestamp':
                        # Create timestamp if missing
                        standardized[col] = range(len(standardized))
                    elif 'altitude' in col:
                        standardized[col] = 0.0
                    elif 'speed' in col:
                        standardized[col] = 0.0
                    elif col in ['roll_deg', 'pitch_deg', 'yaw_deg']:
                        standardized[col] = 0.0
                    elif 'battery' in col:
                        standardized[col] = 100.0
                    else:  # GPS
                        standardized[col] = 0.0
            
            return standardized[required_columns]
            
        except Exception as e:
            logger.error(f"Error standardizing columns: {e}")
            return df
    
    def _merge_datasets(self, primary_df, secondary_df):
        """Merge two datasets on timestamp"""
        try:
            # Standardize secondary dataset
            std_secondary = self._standardize_columns(secondary_df)
            
            # Merge on timestamp (nearest match)
            merged = pd.merge_asof(primary_df.sort_values('timestamp'), 
                                 std_secondary.sort_values('timestamp'), 
                                 on='timestamp', direction='nearest')
            
            return merged
            
        except Exception as e:
            logger.warning(f"Could not merge datasets: {e}")
            return primary_df
    
    def _try_binary_analysis(self, ulg_file_path: str) -> bool:
        """Fallback binary analysis of ULG file"""
        try:
            logger.info("🔧 Trying binary analysis...")
            
            with open(ulg_file_path, 'rb') as f:
                raw_data = f.read()
            
            # Look for ULog header
            if raw_data.startswith(b'ULog'):
                logger.info("✅ Detected ULog format")
                
                # Extract basic flight parameters from binary data
                flight_data = self._extract_from_binary(raw_data)
                
                if flight_data is not None:
                    self.flight_data = flight_data
                    self._perform_comprehensive_analysis()
                    return True
            
            return False
            
        except Exception as e:
            logger.warning(f"Binary analysis failed: {e}")
            return False
    
    def _extract_from_binary(self, raw_data):
        """Extract flight data from binary ULog data"""
        try:
            import struct
            
            # Skip ULog header (first ~16 bytes)
            data_start = 16
            if len(raw_data) < data_start + 100:
                return None
            
            # Try to extract float32 values
            float_count = (len(raw_data) - data_start) // 4
            floats = struct.unpack(f'{float_count}f', raw_data[data_start:data_start + float_count*4])
            
            # Filter valid floats
            valid_floats = [f for f in floats if not (np.isinf(f) or np.isnan(f) or abs(f) > 1e6)]
            
            if len(valid_floats) < 100:
                return None
            
            # Create flight data from floats
            records = []
            record_size = 9  # timestamp + 8 parameters
            
            for i in range(0, len(valid_floats) - record_size, record_size):
                record = valid_floats[i:i+record_size]
                
                # Basic validation
                if record[0] > 0 and record[0] < 1e12:  # Reasonable timestamp
                    records.append({
                        'timestamp': record[0],
                        'altitude_m': max(0, min(10000, record[1])),
                        'speed_mps': max(0, min(100, abs(record[2]))),
                        'roll_deg': max(-180, min(180, record[3])),
                        'pitch_deg': max(-180, min(180, record[4])),
                        'yaw_deg': record[5] % 360,
                        'battery_percent': max(0, min(100, record[6])),
                        'gps_lat': max(-90, min(90, record[7])),
                        'gps_lon': max(-180, min(180, record[8]))
                    })
            
            if records:
                df = pd.DataFrame(records)
                logger.info(f"✅ Extracted {len(records)} records from binary data")
                return df
            else:
                return None
                
        except Exception as e:
            logger.error(f"Binary extraction failed: {e}")
            return None
    
    def _perform_comprehensive_analysis(self):
        """Perform comprehensive flight analysis"""
        try:
            if self.flight_data is None or len(self.flight_data) == 0:
                logger.warning("No flight data available for analysis")
                return
            
            df = self.flight_data
            logger.info(f"📊 Analyzing {len(df)} flight data points")
            
            # Basic flight statistics
            self.analysis_results['flight_summary'] = {
                'total_records': len(df),
                'flight_duration_s': (df['timestamp'].iloc[-1] - df['timestamp'].iloc[0]) / 1000,
                'max_altitude_m': df['altitude_m'].max(),
                'min_altitude_m': df['altitude_m'].min(),
                'avg_altitude_m': df['altitude_m'].mean(),
                'max_speed_mps': df['speed_mps'].max(),
                'avg_speed_mps': df['speed_mps'].mean(),
                'max_roll_deg': df['roll_deg'].max(),
                'min_roll_deg': df['roll_deg'].min(),
                'max_pitch_deg': df['pitch_deg'].max(),
                'min_pitch_deg': df['pitch_deg'].min(),
                'battery_start_%': df['battery_percent'].iloc[0],
                'battery_end_%': df['battery_percent'].iloc[-1],
                'battery_used_%': df['battery_percent'].iloc[0] - df['battery_percent'].iloc[-1]
            }
            
            # Flight phases
            self.analysis_results['flight_phases'] = self._analyze_flight_phases(df)
            
            # Stability analysis
            self.analysis_results['stability_metrics'] = self._analyze_stability(df)
            
            # GPS analysis
            self.analysis_results['gps_analysis'] = self._analyze_gps(df)
            
            # Battery analysis
            self.analysis_results['battery_analysis'] = self._analyze_battery(df)
            
            logger.info("✅ Comprehensive analysis completed")
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
    
    def _analyze_flight_phases(self, df):
        """Analyze flight phases"""
        try:
            total_points = len(df)
            phases = {
                'takeoff': (0, int(total_points * 0.1)),
                'climb': (int(total_points * 0.1), int(total_points * 0.3)),
                'cruise': (int(total_points * 0.3), int(total_points * 0.7)),
                'descent': (int(total_points * 0.7), int(total_points * 0.9)),
                'landing': (int(total_points * 0.9), total_points)
            }
            
            phase_analysis = {}
            for phase, (start, end) in phases.items():
                phase_data = df.iloc[start:end]
                phase_analysis[phase] = {
                    'duration_%': (end - start) / total_points * 100,
                    'avg_altitude_m': phase_data['altitude_m'].mean(),
                    'avg_speed_mps': phase_data['speed_mps'].mean(),
                    'altitude_range_m': phase_data['altitude_m'].max() - phase_data['altitude_m'].min()
                }
            
            return phase_analysis
            
        except Exception as e:
            logger.error(f"Flight phase analysis failed: {e}")
            return {}
    
    def _analyze_stability(self, df):
        """Analyze flight stability"""
        try:
            return {
                'roll_stability_deg': df['roll_deg'].std(),
                'pitch_stability_deg': df['pitch_deg'].std(),
                'yaw_stability_deg': df['yaw_deg'].std(),
                'altitude_stability_m': df['altitude_m'].std(),
                'speed_stability_mps': df['speed_mps'].std(),
                'overall_stability_score': self._calculate_stability_score(df)
            }
            
        except Exception as e:
            logger.error(f"Stability analysis failed: {e}")
            return {}
    
    def _calculate_stability_score(self, df):
        """Calculate overall stability score (0-100)"""
        try:
            # Lower standard deviations = higher stability
            roll_score = max(0, 100 - df['roll_deg'].std() * 2)
            pitch_score = max(0, 100 - df['pitch_deg'].std() * 2)
            altitude_score = max(0, 100 - df['altitude_m'].std() / 10)
            
            return (roll_score + pitch_score + altitude_score) / 3
            
        except:
            return 50.0
    
    def _analyze_gps(self, df):
        """Analyze GPS data"""
        try:
            valid_gps = df[(df['gps_lat'] != 0) & (df['gps_lon'] != 0)]
            
            if len(valid_gps) > 0:
                lat_range = valid_gps['gps_lat'].max() - valid_gps['gps_lat'].min()
                lon_range = valid_gps['gps_lon'].max() - valid_gps['gps_lon'].min()
                
                # Approximate distance (rough calculation)
                distance_km = np.sqrt(lat_range**2 + lon_range**2) * 111
                
                return {
                    'gps_points_available': len(valid_gps),
                    'gps_coverage_%': len(valid_gps) / len(df) * 100,
                    'latitude_range_deg': lat_range,
                    'longitude_range_deg': lon_range,
                    'estimated_distance_km': distance_km
                }
            else:
                return {'gps_points_available': 0, 'gps_coverage_%': 0}
                
        except Exception as e:
            logger.error(f"GPS analysis failed: {e}")
            return {}
    
    def _analyze_battery(self, df):
        """Analyze battery performance"""
        try:
            battery_data = df['battery_percent']
            
            return {
                'initial_battery_%': battery_data.iloc[0],
                'final_battery_%': battery_data.iloc[-1],
                'battery_used_%': battery_data.iloc[0] - battery_data.iloc[-1],
                'avg_drain_rate_%_per_min': (battery_data.iloc[0] - battery_data.iloc[-1]) / (len(df) / 600),  # Assuming 10Hz
                'battery_efficiency_score': self._calculate_battery_efficiency(df)
            }
            
        except Exception as e:
            logger.error(f"Battery analysis failed: {e}")
            return {}
    
    def _calculate_battery_efficiency(self, df):
        """Calculate battery efficiency score"""
        try:
            # Efficiency based on distance covered per battery percentage
            if 'gps_lat' in df.columns and 'gps_lon' in df.columns:
                valid_gps = df[(df['gps_lat'] != 0) & (df['gps_lon'] != 0)]
                if len(valid_gps) > 1:
                    lat_diff = valid_gps['gps_lat'].iloc[-1] - valid_gps['gps_lat'].iloc[0]
                    lon_diff = valid_gps['gps_lon'].iloc[-1] - valid_gps['gps_lon'].iloc[0]
                    distance_km = np.sqrt(lat_diff**2 + lon_diff**2) * 111
                    
                    battery_used = df['battery_percent'].iloc[0] - df['battery_percent'].iloc[-1]
                    if battery_used > 0:
                        return min(100, distance_km / battery_used * 10)  # km per % battery
            
            return 50.0  # Default efficiency score
            
        except:
            return 50.0
    
    def get_analysis_summary(self):
        """Get formatted analysis summary"""
        if not self.analysis_results:
            return "No analysis results available"
        
        summary = []
        summary.append("🚁 DIRECT ULG FLIGHT ANALYSIS RESULTS")
        summary.append("=" * 50)
        
        # Flight summary
        if 'flight_summary' in self.analysis_results:
            fs = self.analysis_results['flight_summary']
            summary.append(f"📊 Flight Summary:")
            summary.append(f"   Records: {fs['total_records']:,}")
            summary.append(f"   Duration: {fs['flight_duration_s']:.1f} seconds")
            summary.append(f"   Max Altitude: {fs['max_altitude_m']:.1f} m")
            summary.append(f"   Max Speed: {fs['max_speed_mps']:.1f} m/s")
            summary.append(f"   Battery Used: {fs['battery_used_%']:.1f}%")
        
        # Stability
        if 'stability_metrics' in self.analysis_results:
            sm = self.analysis_results['stability_metrics']
            summary.append(f"\n🎯 Stability Metrics:")
            summary.append(f"   Roll Stability: {sm['roll_stability_deg']:.1f}°")
            summary.append(f"   Pitch Stability: {sm['pitch_stability_deg']:.1f}°")
            summary.append(f"   Overall Score: {sm['overall_stability_score']:.1f}/100")
        
        # GPS
        if 'gps_analysis' in self.analysis_results:
            ga = self.analysis_results['gps_analysis']
            summary.append(f"\n📍 GPS Analysis:")
            summary.append(f"   GPS Coverage: {ga.get('gps_coverage_%', 0):.1f}%")
            summary.append(f"   Distance: {ga.get('estimated_distance_km', 0):.2f} km")
        
        # Battery
        if 'battery_analysis' in self.analysis_results:
            ba = self.analysis_results['battery_analysis']
            summary.append(f"\n🔋 Battery Analysis:")
            summary.append(f"   Efficiency: {ba['battery_efficiency_score']:.1f}/100")
            summary.append(f"   Drain Rate: {ba['avg_drain_rate_%_per_min']:.2f}%/min")
        
        return "\n".join(summary)
    
    def export_analysis_report(self, output_path: str):
        """Export detailed analysis report"""
        try:
            with open(output_path, 'w') as f:
                f.write(self.get_analysis_summary())
                f.write("\n\n" + "=" * 50 + "\n")
                f.write("DETAILED ANALYSIS DATA\n")
                f.write("=" * 50 + "\n")
                
                # Write detailed results
                for category, data in self.analysis_results.items():
                    f.write(f"\n{category.upper()}:\n")
                    f.write("-" * len(category) + "\n")
                    for key, value in data.items():
                        f.write(f"  {key}: {value}\n")
                
                # Write sample flight data
                if self.flight_data is not None:
                    f.write(f"\nSAMPLE FLIGHT DATA (first 10 records):\n")
                    f.write("-" * 35 + "\n")
                    f.write(self.flight_data.head(10).to_string())
            
            logger.info(f"✅ Analysis report exported to: {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to export report: {e}")


def main():
    """Main function for direct ULG analysis"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze ULG files directly without CSV conversion')
    parser.add_argument('ulg_file', help='ULG file to analyze')
    parser.add_argument('--output', '-o', help='Output report file')
    parser.add_argument('--export-data', help='Export flight data to CSV')
    
    args = parser.parse_args()
    
    try:
        analyzer = DirectULGAnalyzer()
        
        # Perform analysis
        analyzer.analyze_ulg_directly(args.ulg_file)
        
        # Print summary
        print(analyzer.get_analysis_summary())
        
        # Export report if requested
        if args.output:
            analyzer.export_analysis_report(args.output)
            print(f"\n📄 Report saved to: {args.output}")
        
        # Export flight data if requested
        if args.export_data and analyzer.flight_data is not None:
            analyzer.flight_data.to_csv(args.export_data, index=False)
            print(f"📊 Flight data saved to: {args.export_data}")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
