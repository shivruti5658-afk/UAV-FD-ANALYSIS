#!/usr/bin/env python3
"""
UAV Flight Analysis System - Main Controller

This is the main entry point for the UAV Flight Analysis System.
It provides a command-line interface for running comprehensive flight data analysis.

Usage:
    python main.py --data data/uav_flight_data.csv
    python main.py --data data/uav_flight_data.csv --output results/
    python main.py --generate-sample --output data/sample_flight.csv
    python main.py --dashboard

Author: UAV Flight Analysis Team
Version: 1.0.0
"""

import argparse
import os
import sys
from pathlib import Path
from datetime import datetime
import json

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import analysis modules
from data_loader import load_csv, validate_dataset, get_dataset_summary
from preprocessing import preprocess_pipeline
from flight_metrics import calculate_all_flight_metrics, format_flight_summary
from stability_analysis import assess_flight_stability, generate_stability_recommendations
from anomaly_detection import detect_all_anomalies, generate_anomaly_report
from battery_analysis import comprehensive_battery_analysis, format_battery_summary
from flight_phase_detection import detect_flight_phases, format_phase_summary
from digital_twin import create_comprehensive_digital_twin, create_interactive_dashboard
from visualization import create_comprehensive_flight_plots, create_anomaly_visualization
from report_generator import generate_all_reports

# Import ULG converter
try:
    from ulg_converter import ULGConverter
except ImportError:
    ULGConverter = None

# Import utilities
from utils.helpers import (
    setup_logging, validate_file_path, create_output_directory,
    create_synthetic_flight_data, validate_flight_data_structure,
    get_system_info, DEFAULT_CONFIG
)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="UAV Flight Analysis System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --data data/flight.csv
  python main.py --data data/flight.csv --output results/
  python main.py --generate-sample --output data/sample.csv
  python main.py --dashboard
  python main.py --convert-ulg flight.ulg --output flight.csv
  python main.py --batch-convert ulg_files/ --output csv_files/
        """
    )
    
    # Input options
    parser.add_argument(
        '--data', '-d',
        type=str,
        help='Path to UAV flight data CSV file'
    )
    
    parser.add_argument(
        '--generate-sample',
        action='store_true',
        help='Generate synthetic sample flight data'
    )
    
    parser.add_argument(
        '--dashboard',
        action='store_true',
        help='Launch Streamlit dashboard'
    )
    
    parser.add_argument(
        '--convert-ulg',
        type=str,
        help='Convert ULG file to CSV format (specify input file)'
    )
    
    parser.add_argument(
        '--batch-convert',
        type=str,
        help='Batch convert ULG files in directory to CSV format'
    )
    
    # Output options
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='outputs',
        help='Output directory for results (default: outputs)'
    )
    
    # Configuration options
    parser.add_argument(
        '--config', '-c',
        type=str,
        help='Path to configuration JSON file'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level (default: INFO)'
    )
    
    # Analysis options
    parser.add_argument(
        '--preprocess',
        action='store_true',
        default=True,
        help='Apply data preprocessing (default: True)'
    )
    
    parser.add_argument(
        '--no-preprocess',
        action='store_false',
        dest='preprocess',
        help='Skip data preprocessing'
    )
    
    parser.add_argument(
        '--visualize',
        action='store_true',
        default=True,
        help='Generate visualizations (default: True)'
    )
    
    parser.add_argument(
        '--no-visualize',
        action='store_false',
        dest='visualize',
        help='Skip visualization generation'
    )
    
    parser.add_argument(
        '--reports',
        action='store_true',
        default=True,
        help='Generate reports (default: True)'
    )
    
    parser.add_argument(
        '--no-reports',
        action='store_false',
        dest='reports',
        help='Skip report generation'
    )
    
    parser.add_argument(
        '--phase-method',
        choices=['hybrid', 'altitude', 'speed', 'clustering'],
        default='hybrid',
        help='Flight phase detection method (default: hybrid)'
    )
    
    return parser.parse_args()


def load_configuration(config_path: str = None) -> dict:
    """Load configuration from file or use defaults."""
    config = DEFAULT_CONFIG.copy()
    
    if config_path and validate_file_path(config_path):
        try:
            with open(config_path, 'r') as f:
                user_config = json.load(f)
            
            # Merge user config with defaults
            for section, values in user_config.items():
                if section in config:
                    config[section].update(values)
                else:
                    config[section] = values
                    
        except Exception as e:
            print(f"Warning: Could not load config file {config_path}: {e}")
    
    return config


def run_full_analysis(data_path: str, output_dir: str, config: dict, args) -> dict:
    """Run complete flight analysis pipeline."""
    
    logger = setup_logging(args.log_level, os.path.join(output_dir, 'analysis.log'))
    logger.info("Starting UAV Flight Analysis")
    logger.info(f"Input data: {data_path}")
    logger.info(f"Output directory: {output_dir}")
    
    results = {}
    
    try:
        # Step 1: Load and validate data
        logger.info("Step 1: Loading and validating data...")
        df = load_csv(data_path)
        
        validation_results = validate_dataset(df)
        if not validation_results['is_valid']:
            raise ValueError(f"Dataset validation failed: {validation_results['missing_columns']}")
        
        dataset_summary = get_dataset_summary(df)
        logger.info(f"Dataset loaded: {len(df)} rows, {len(df.columns)} columns")
        
        results['dataset_info'] = {
            'validation': validation_results,
            'summary': dataset_summary
        }
        
        # Step 2: Preprocessing (if enabled)
        if args.preprocess:
            logger.info("Step 2: Preprocessing data...")
            df_processed = preprocess_pipeline(df, config['preprocessing'])
            logger.info(f"Preprocessing completed: {len(df_processed)} rows remaining")
            df = df_processed
        else:
            logger.info("Step 2: Skipping preprocessing")
        
        # Step 3: Flight metrics calculation
        logger.info("Step 3: Calculating flight metrics...")
        flight_metrics = calculate_all_flight_metrics(df)
        logger.info("Flight metrics calculated")
        results['flight_metrics'] = flight_metrics
        
        # Step 4: Stability analysis
        logger.info("Step 4: Analyzing flight stability...")
        stability_analysis = assess_flight_stability(df)
        logger.info(f"Stability analysis completed: {stability_analysis['overall_rating']['rating']}")
        results['stability_analysis'] = stability_analysis
        
        # Step 5: Anomaly detection
        logger.info("Step 5: Detecting anomalies...")
        anomaly_results = detect_all_anomalies(df, config['anomaly_detection'])
        logger.info(f"Anomaly detection completed: {anomaly_results['summary']['total_anomalies']} anomalies")
        results['anomaly_results'] = anomaly_results
        
        # Step 6: Battery analysis
        logger.info("Step 6: Analyzing battery performance...")
        battery_analysis = comprehensive_battery_analysis(df)
        logger.info(f"Battery analysis completed: {battery_analysis['consumption_metrics']['total_consumption']:.1f}% consumed")
        results['battery_analysis'] = battery_analysis
        
        # Step 7: Flight phase detection
        logger.info("Step 7: Detecting flight phases...")
        phase_config = config['phase_detection'].copy()
        # Remove clustering-specific parameters for non-clustering methods
        if args.phase_method != 'clustering':
            phase_config.pop('n_clusters', None)
        phase_results = detect_flight_phases(df, args.phase_method, phase_config)
        logger.info(f"Phase detection completed: {phase_results['phase_summary']['total_phases']} phases")
        results['phase_results'] = phase_results
        
        # Step 8: Visualizations (if enabled)
        if args.visualize:
            logger.info("Step 8: Generating visualizations...")
            
            # Create output directories
            graphs_dir = os.path.join(output_dir, 'graphs')
            create_output_directory(graphs_dir)
            
            # Generate standard plots
            plot_paths = create_comprehensive_flight_plots(df, phase_results['phases'], graphs_dir)
            results['visualizations'] = plot_paths
            
            # Generate anomaly visualization if anomalies exist
            if anomaly_results['summary']['total_anomalies'] > 0:
                anomaly_plot_path = create_anomaly_visualization(df, anomaly_results, 
                                                             os.path.join(graphs_dir, 'anomalies.png'))
                results['visualizations']['anomalies'] = anomaly_plot_path
            
            # Generate digital twin
            try:
                digital_twin_viz = create_comprehensive_digital_twin(df)
                digital_twin_html = os.path.join(output_dir, 'digital_twin.html')
                from digital_twin import export_digital_twin_html
                export_digital_twin_html(digital_twin_viz, digital_twin_html)
                results['digital_twin'] = digital_twin_html
                logger.info("Digital twin created")
            except Exception as e:
                logger.warning(f"Could not create digital twin: {e}")
        
        # Step 9: Reports (if enabled)
        if args.reports:
            logger.info("Step 9: Generating reports...")
            
            reports_dir = os.path.join(output_dir, 'reports')
            create_output_directory(reports_dir)
            
            report_paths = generate_all_reports(
                df, flight_metrics, stability_analysis, anomaly_results,
                battery_analysis, phase_results, reports_dir
            )
            results['reports'] = report_paths
            logger.info(f"Reports generated: {list(report_paths.keys())}")
        
        # Step 10: Save analysis results
        results_path = os.path.join(output_dir, 'analysis_results.json')
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info("Analysis completed successfully!")
        return results
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        raise


def print_summary(results: dict, output_dir: str):
    """Print analysis summary to console."""
    print("\n" + "="*60)
    print("UAV FLIGHT ANALYSIS SUMMARY")
    print("="*60)
    
    # Dataset info
    dataset_info = results['dataset_info']['summary']
    print(f"\n📊 Dataset Information:")
    print(f"  • Data Points: {dataset_info['data_points']}")
    print(f"  • Flight Duration: {dataset_info['flight_duration_seconds']:.1f} seconds")
    print(f"  • Max Altitude: {dataset_info['altitude_range']['max']:.1f} m")
    print(f"  • Max Speed: {dataset_info['speed_range']['max']:.1f} m/s")
    
    # Flight metrics
    metrics = results['flight_metrics']
    print(f"\n✈️ Flight Performance:")
    print(f"  • Duration: {metrics['flight_duration']['minutes']:.1f} minutes")
    print(f"  • Distance: {metrics['distance_traveled']['total_distance_km']:.2f} km")
    print(f"  • Avg Speed: {metrics['speed_stats']['avg_speed']:.1f} m/s")
    print(f"  • Max Climb Rate: {metrics['climb_descent_rates']['max_climb_rate']:.2f} m/s")
    
    # Stability
    stability = results['stability_analysis']
    print(f"\n🎯 Stability Assessment:")
    print(f"  • Rating: {stability['overall_rating']['rating']} ({stability['overall_rating']['score']:.3f})")
    print(f"  • Roll Std Dev: {stability['attitude_stability']['roll']['std_dev']:.2f}°")
    print(f"  • Pitch Std Dev: {stability['attitude_stability']['pitch']['std_dev']:.2f}°")
    
    # Anomalies
    anomalies = results['anomaly_results']['summary']
    print(f"\n⚠️ Anomaly Detection:")
    print(f"  • Total Anomalies: {anomalies['total_anomalies']}")
    print(f"  • Anomaly Rate: {anomalies['overall_anomaly_rate']:.2%}")
    print(f"  • Assessment: {anomalies['overall_assessment']}")
    
    # Battery
    battery = results['battery_analysis']
    print(f"\n🔋 Battery Analysis:")
    print(f"  • Consumption: {battery['consumption_metrics']['total_consumption']:.1f}%")
    print(f"  • Drain Rate: {battery['consumption_metrics']['consumption_rate_percent_per_minute']:.2f}%/min")
    print(f"  • Remaining Time: {battery['remaining_time']['remaining_flight_time_minutes']:.1f} minutes")
    
    # Phases
    phases = results['phase_results']
    print(f"\n📍 Flight Phases:")
    print(f"  • Total Phases: {phases['phase_summary']['total_phases']}")
    print(f"  • Detection Method: {phases['detection_method']}")
    
    # Output files
    print(f"\n📁 Output Files:")
    print(f"  • Results Directory: {output_dir}")
    
    if 'visualizations' in results:
        print(f"  • Visualizations: {len(results['visualizations'])} plots generated")
    
    if 'reports' in results:
        print(f"  • Reports: {', '.join(results['reports'].keys())}")
    
    if 'digital_twin' in results:
        print(f"  • Digital Twin: {results['digital_twin']}")
    
    print("\n" + "="*60)


def generate_sample_data(output_path: str):
    """Generate synthetic sample flight data."""
    print("🚁 Generating synthetic UAV flight data...")
    
    # Create synthetic data
    df = create_synthetic_flight_data(
        duration_seconds=600,  # 10 minutes
        sampling_rate=10.0,    # 10 Hz
        start_altitude=0.0,
        max_altitude=150.0,
        cruise_speed=12.0
    )
    
    # Save to file
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    
    print(f"✅ Sample data generated: {output_path}")
    print(f"   • Duration: 10 minutes")
    print(f"   • Data Points: {len(df)}")
    print(f"   • Max Altitude: {df['altitude_m'].max():.1f} m")
    print(f"   • Flight Phases: Takeoff, Climb, Cruise, Descent, Landing")


def launch_dashboard():
    """Launch Streamlit dashboard."""
    print("🚀 Launching UAV Flight Analysis Dashboard...")
    print("   Opening in your default browser...")
    
    # Launch Streamlit
    import subprocess
    dashboard_path = os.path.join(os.path.dirname(__file__), 'dashboard', 'app.py')
    
    try:
        subprocess.run([
            sys.executable, '-m', 'streamlit', 'run', dashboard_path,
            '--server.headless', 'false',
            '--browser.gatherUsageStats', 'false'
        ])
    except KeyboardInterrupt:
        print("\n👋 Dashboard closed")
    except Exception as e:
        print(f"❌ Error launching dashboard: {e}")
        print("   Make sure Streamlit is installed: pip install streamlit")


def main():
    """Main entry point."""
    args = parse_arguments()
    
    # Setup logging
    logger = setup_logging(args.log_level)
    
    # Print system info
    system_info = get_system_info()
    logger.info(f"UAV Flight Analysis System v1.0.0")
    logger.info(f"Platform: {system_info['platform']}")
    logger.info(f"Python: {system_info['python_version']}")
    
    try:
        # Handle different modes
        if args.dashboard:
            launch_dashboard()
            return
        
        elif args.generate_sample:
            if not args.output:
                args.output = 'data/sample_flight_data.csv'
            generate_sample_data(args.output)
            return
        
        elif args.convert_ulg:
            if ULGConverter is None:
                print("❌ Error: ULG converter not available")
                print("   Please check if ulg_converter.py is properly installed")
                sys.exit(1)
            
            # Convert single ULG file
            converter = ULGConverter()
            if not args.output:
                args.output = os.path.splitext(args.convert_ulg)[0] + '.csv'
            
            try:
                output_path = converter.convert_ulg_to_csv(args.convert_ulg, args.output)
                print(f"✅ ULG file converted successfully!")
                print(f"📁 Output: {output_path}")
                return
            except Exception as e:
                print(f"❌ Error converting ULG file: {e}")
                sys.exit(1)
        
        elif args.batch_convert:
            if ULGConverter is None:
                print("❌ Error: ULG converter not available")
                print("   Please check if ulg_converter.py is properly installed")
                sys.exit(1)
            
            # Batch convert ULG files
            converter = ULGConverter()
            if not args.output:
                args.output = 'converted_csv'
            
            try:
                converted_files = converter.batch_convert(args.batch_convert, args.output)
                print(f"✅ Batch conversion completed!")
                print(f"📁 Converted {len(converted_files)} files:")
                for f in converted_files:
                    print(f"   - {f}")
                return
            except Exception as e:
                print(f"❌ Error in batch conversion: {e}")
                sys.exit(1)
        
        elif args.data:
            # Validate input file
            if not validate_file_path(args.data):
                print(f"❌ Error: Data file not found: {args.data}")
                sys.exit(1)
            
            # Create output directory
            output_dir = create_output_directory(args.output)
            
            # Load configuration
            config = load_configuration(args.config)
            
            # Run analysis
            print("🚁 Starting UAV Flight Analysis...")
            results = run_full_analysis(args.data, output_dir, config, args)
            
            # Print summary
            print_summary(results, output_dir)
            
            print(f"\n✅ Analysis completed successfully!")
            print(f"📁 Results saved to: {output_dir}")
            
        else:
            print("❌ Error: No action specified")
            print("   Use --data <file> to analyze flight data")
            print("   Use --generate-sample to create sample data")
            print("   Use --dashboard to launch web interface")
            print("   Use --convert-ulg <file> to convert ULG to CSV")
            print("   Use --batch-convert <dir> to batch convert ULG files")
            print("   Use --help for more options")
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n👋 Analysis interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        logger.error(f"Application error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
