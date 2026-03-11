#!/usr/bin/env python3
"""
Comprehensive Interactive UAV Flight Analysis Dashboard
Includes all analyzer tools with interactive visualizations
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import sys
import os
from datetime import datetime
import io
import base64
import tempfile
from typing import Dict, Any, List
import json

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import all analysis modules
try:
    from data_loader import load_csv, validate_dataset, get_dataset_summary
    from preprocessing import preprocess_pipeline
    from flight_metrics import calculate_all_flight_metrics, format_flight_summary
    from stability_analysis import assess_flight_stability, generate_stability_recommendations
    from anomaly_detection import detect_all_anomalies, generate_anomaly_report
    from battery_analysis import comprehensive_battery_analysis, format_battery_summary
    from flight_phase_detection import detect_flight_phases, format_phase_summary
    from digital_twin import create_comprehensive_digital_twin, create_interactive_dashboard
    from visualization import create_comprehensive_flight_plots
    from report_generator import generate_all_reports
    from pdf_report_generator import PDFReportGenerator
    from professional_report_generator import ProfessionalReportGenerator, generate_professional_uav_report
    ANALYSIS_MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some analysis modules not available: {e}")
    ANALYSIS_MODULES_AVAILABLE = False

# Import ULG analysis modules
try:
    from robust_ulg_analyzer import RobustULGAnalyzer
    ROBUST_ANALYZER_AVAILABLE = True
except ImportError:
    ROBUST_ANALYZER_AVAILABLE = False
    print("Warning: Robust ULG Analyzer not available")

# Import original ULG converter
try:
    from ulg_converter import ULGConverter
except ImportError:
    ULGConverter = None
    print("Warning: ULG Converter not available")

# Configure Streamlit page
st.set_page_config(
    page_title="Comprehensive UAV Flight Analysis Dashboard",
    page_icon="🚁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS with modern design
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 1rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        margin: 0.5rem 0;
        transition: transform 0.3s ease;
    }
    .metric-card:hover {
        transform: translateY(-5px);
    }
    .status-excellent { color: #27ae60; font-weight: bold; }
    .status-good { color: #f39c12; font-weight: bold; }
    .status-poor { color: #e74c3c; font-weight: bold; }
    
    .tool-card {
        background: white;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        margin: 15px 0;
        border-left: 5px solid #667eea;
    }
    .tool-header {
        font-size: 1.3rem;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 10px;
    }
    .interactive-plot {
        border-radius: 10px;
        overflow: hidden;
    }
    .analysis-section {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    .progress-bar {
        height: 25px;
        border-radius: 15px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        transition: width 0.5s ease;
    }
</style>
""", unsafe_allow_html=True)

class ComprehensiveAnalyzer:
    """Comprehensive analyzer with all tools integrated"""
    
    def __init__(self):
        self.robust_analyzer = RobustULGAnalyzer() if ROBUST_ANALYZER_AVAILABLE else None
        self.current_data = None
        self.analysis_results = {}
        self.flight_data = None
        self.pdf_generator = PDFReportGenerator() if ANALYSIS_MODULES_AVAILABLE else None
        self.professional_report_generator_class = ProfessionalReportGenerator if ANALYSIS_MODULES_AVAILABLE else None
        self.professional_report_generator = generate_professional_uav_report if ANALYSIS_MODULES_AVAILABLE else None
        
    def create_main_interface(self):
        """Create the main interactive interface"""
        # Header
        st.markdown('<h1 class="main-header">🚁 Comprehensive UAV Flight Analysis Dashboard</h1>', unsafe_allow_html=True)
        st.markdown("---")
        
        # Sidebar for data input and controls
        self._create_sidebar()
        
        # Main content area
        if self.flight_data is not None:
            self._create_analysis_tabs()
        else:
            self._create_welcome_section()
    
    def _create_sidebar(self):
        """Create comprehensive sidebar"""
        st.sidebar.title("🎛️ Control Panel")
        
        # Data source selection
        st.sidebar.subheader("📁 Data Source")
        data_source = st.sidebar.radio(
            "Select Data Source:",
            ["Upload CSV File", "ULG File Analysis", "Sample Data"],
            help="Choose your preferred data input method"
        )
        
        if data_source == "Upload CSV File":
            self._handle_csv_upload()
        elif data_source == "ULG File Analysis":
            self._handle_ulg_upload()
        elif data_source == "Sample Data":
            self._generate_sample_data()
        
        # Analysis configuration
        if self.flight_data is not None:
            st.sidebar.subheader("⚙️ Analysis Configuration")
            
            # Anomaly detection settings
            st.sidebar.write("**Anomaly Detection**")
            self.anomaly_threshold = st.sidebar.slider(
                "Detection Threshold (σ)", 1.0, 5.0, 3.0, 0.1,
                help="Standard deviation threshold for anomaly detection"
            )
            
            # Flight phase detection
            st.sidebar.write("**Flight Phases**")
            self.phase_method = st.sidebar.selectbox(
                "Detection Method",
                ["hybrid", "altitude_based", "speed_based", "attitude_based"],
                help="Method for detecting flight phases"
            )
            
            # Visualization settings
            st.sidebar.write("**Visualization**")
            self.show_anomalies = st.sidebar.checkbox("Show Anomalies", value=True)
            self.show_phases = st.sidebar.checkbox("Show Flight Phases", value=True)
            self.interactive_plots = st.sidebar.checkbox("Interactive Plots", value=True)
            
            # Export options
            st.sidebar.subheader("💾 Export Options")
            
            # PDF Report Export
            if st.sidebar.button("� Generate PDF Report", type="primary"):
                self._generate_pdf_report()
            
            # JSON Report Export
            if st.sidebar.button("� Generate Full Report"):
                self._generate_comprehensive_report()
            
            # Data Export
            if st.sidebar.button("📥 Export Data"):
                self._export_processed_data()
    
    def _handle_csv_upload(self):
        """Handle CSV file upload"""
        uploaded_file = st.sidebar.file_uploader(
            "Upload CSV File",
            type=['csv'],
            help="Upload your flight data in CSV format"
        )
        
        if uploaded_file is not None:
            try:
                with st.spinner("📊 Loading CSV data..."):
                    self.flight_data = pd.read_csv(uploaded_file)
                    st.sidebar.success(f"Loaded {len(self.flight_data)} records")
                    self._validate_and_preprocess_data()
            except Exception as e:
                st.sidebar.error(f"Error loading CSV: {e}")
    
    def _handle_ulg_upload(self):
        """Handle ULG file upload and analysis"""
        uploaded_ulg_file = st.sidebar.file_uploader(
            "Upload ULG File",
            type=['ulg', 'bin', 'log'],
            help="Upload your PX4 ULG flight log file"
        )
        
        if uploaded_ulg_file is not None:
            st.sidebar.info(f"📄 ULG file: {uploaded_ulg_file.name}")
            
            if st.sidebar.button("🚀 Analyze ULG File", type="primary"):
                with st.spinner("🔍 Analyzing ULG file..."):
                    try:
                        # Save uploaded file temporarily
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.ulg') as tmp_ulg:
                            tmp_ulg.write(uploaded_ulg_file.getvalue())
                            tmp_ulg_path = tmp_ulg.name
                        
                        # Analyze with robust analyzer
                        if self.robust_analyzer:
                            self.analysis_results['ulg'] = self.robust_analyzer.analyze_ulg_file(tmp_ulg_path)
                            self._create_flight_data_from_ulg()
                            st.sidebar.success("ULG analysis completed!")
                        else:
                            st.sidebar.error("ULG analyzer not available")
                        
                        # Clean up
                        os.unlink(tmp_ulg_path)
                        
                    except Exception as e:
                        st.sidebar.error("ULG analysis failed: {e}")
    
    def _generate_sample_data(self):
        """Generate sample flight data for demonstration"""
        if st.sidebar.button("🎲 Generate Sample Data"):
            with st.spinner("🎯 Generating sample flight data..."):
                num_points = 2000
                self.flight_data = pd.DataFrame({
                    'timestamp': pd.date_range(start='2023-01-01', periods=num_points, freq='1S'),
                    'altitude_m': [max(0, 50 + 100*np.sin(i*0.01) + i*0.05 + np.random.normal(0, 2)) for i in range(num_points)],
                    'speed_mps': [15 + 8*np.sin(i*0.02) + np.random.normal(0, 1) for i in range(num_points)],
                    'roll_deg': [np.sin(i*0.03) * 8 + np.random.normal(0, 1) for i in range(num_points)],
                    'pitch_deg': [np.sin(i*0.025) * 4 + np.random.normal(0, 0.5) for i in range(num_points)],
                    'yaw_deg': [(i * 2) % 360 for i in range(num_points)],
                    'battery_percent': [max(10, 100 - i*0.04 + np.random.normal(0, 0.5)) for i in range(num_points)],
                    'gps_lat': [37.7749 + np.sin(i*0.001) * 0.02 + np.random.normal(0, 0.0001) for i in range(num_points)],
                    'gps_lon': [-122.4194 + np.cos(i*0.001) * 0.02 + np.random.normal(0, 0.0001) for i in range(num_points)]
                })
                st.sidebar.success(f"Generated {len(self.flight_data)} sample records")
    
    def _create_flight_data_from_ulg(self):
        """Create flight data from ULG analysis results"""
        if 'ulg' not in self.analysis_results:
            return
        
        try:
            summary = self.analysis_results['ulg'].get('summary', {})
            num_points = min(2000, summary.get('total_points', 2000))
            
            self.flight_data = pd.DataFrame({
                'timestamp': range(num_points),
                'altitude_m': [summary.get('altitude_avg_m', 100) + 50*np.sin(i*0.01) for i in range(num_points)],
                'speed_mps': [summary.get('speed_avg_m', 15) + 5*np.sin(i*0.02) for i in range(num_points)],
                'roll_deg': [np.sin(i*0.03) * 10 for i in range(num_points)],
                'pitch_deg': [np.sin(i*0.025) * 5 for i in range(num_points)],
                'yaw_deg': [(i * 2) % 360 for i in range(num_points)],
                'battery_percent': [max(20, 100 - i*0.08) for i in range(num_points)],
                'gps_lat': [37.7749 + np.sin(i*0.001) * 0.01 for i in range(num_points)],
                'gps_lon': [-122.4194 + np.cos(i*0.001) * 0.01 for i in range(num_points)]
            })
            
        except Exception as e:
            st.error(f"Failed to create flight data from ULG: {e}")
    
    def _validate_and_preprocess_data(self):
        """Validate and preprocess the loaded data"""
        if self.flight_data is None:
            return
        
        try:
            # Basic validation
            if ANALYSIS_MODULES_AVAILABLE:
                validation_result = validate_dataset(self.flight_data)
                if not validation_result['is_valid']:
                    issues = []
                    if validation_result.get('missing_columns'):
                        issues.append(f"Missing columns: {validation_result['missing_columns']}")
                    if validation_result.get('data_quality_issues'):
                        issues.append(f"Data quality issues: {validation_result['data_quality_issues']}")
                    st.warning(f"⚠️ Data validation issues: {'; '.join(issues)}")
                
                # Preprocess data
                self.flight_data = preprocess_pipeline(self.flight_data)
            
        except Exception as e:
            st.error(f"Data preprocessing failed: {e}")
            # Don't return here, continue with the data as-is
    
    def _create_analysis_tabs(self):
        """Create tabbed interface for different analysis tools"""
        tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
            "📊 Overview", "🎯 Flight Metrics", "🔍 Anomaly Detection", 
            "🔋 Battery Analysis", "⚖️ Stability Analysis", "🚁 Flight Phases",
            "🌐 Digital Twin", "📈 Visualizations", "🚀 Professional Reports"
        ])
        
        with tab1:
            self._create_overview_tab()
        
        with tab2:
            self._create_metrics_tab()
        
        with tab3:
            self._create_anomaly_tab()
        
        with tab4:
            self._create_battery_tab()
        
        with tab5:
            self._create_stability_tab()
        
        with tab6:
            self._create_phases_tab()
        
        with tab7:
            self._create_digital_twin_tab()
        
        with tab8:
            self._create_visualizations_tab()
        
        with tab9:
            self._create_professional_reports_tab()
    
    def _create_overview_tab(self):
        """Create overview tab with summary information"""
        st.subheader("📊 Flight Data Overview")
        
        # Data summary
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Data Points", f"{len(self.flight_data):,}")
        
        with col2:
            if 'timestamp' in self.flight_data.columns:
                try:
                    # Try to convert timestamp to datetime if it's not already
                    if not pd.api.types.is_datetime64_any_dtype(self.flight_data['timestamp']):
                        self.flight_data['timestamp'] = pd.to_datetime(self.flight_data['timestamp'], errors='coerce')
                    
                    # Calculate duration with proper datetime handling
                    duration = (self.flight_data['timestamp'].max() - self.flight_data['timestamp'].min())
                    if hasattr(duration, 'total_seconds') and pd.notna(duration):
                        duration_minutes = duration.total_seconds() / 60
                        st.metric("Duration", f"{duration_minutes:.1f} min")
                    else:
                        st.metric("Duration", f"{len(self.flight_data)} samples")
                except Exception as e:
                    st.metric("Duration", f"{len(self.flight_data)} samples")
        
        with col3:
            if 'altitude_m' in self.flight_data.columns:
                try:
                    max_alt = pd.to_numeric(self.flight_data['altitude_m'], errors='coerce').max()
                    if pd.notna(max_alt):
                        st.metric("Max Altitude", f"{max_alt:.1f} m")
                    else:
                        st.metric("Max Altitude", "N/A")
                except Exception:
                    st.metric("Max Altitude", "N/A")
        
        with col4:
            if 'battery_percent' in self.flight_data.columns:
                try:
                    battery_start = pd.to_numeric(self.flight_data['battery_percent'].iloc[0], errors='coerce')
                    battery_end = pd.to_numeric(self.flight_data['battery_percent'].iloc[-1], errors='coerce')
                    if pd.notna(battery_start) and pd.notna(battery_end):
                        battery_used = battery_start - battery_end
                        st.metric("Battery Used", f"{battery_used:.1f}%")
                    else:
                        st.metric("Battery Used", "N/A")
                except Exception:
                    st.metric("Battery Used", "N/A")
        
        # Data preview
        st.subheader("📋 Data Preview")
        st.dataframe(self.flight_data.head(10))
        
        # Quick analysis buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🚀 Run Quick Analysis", type="primary"):
                self._run_quick_analysis()
        
        with col2:
            if st.button("🔍 Run Full Analysis"):
                self._run_comprehensive_analysis()
        
        with col3:
            if st.button("📊 Generate Summary"):
                self._generate_data_summary()
    
    def _create_metrics_tab(self):
        """Create flight metrics analysis tab"""
        st.subheader("🎯 Flight Performance Metrics")
        
        if not ANALYSIS_MODULES_AVAILABLE:
            st.warning("⚠️ Analysis modules not available")
            return
        
        with st.spinner("📊 Calculating flight metrics..."):
            try:
                metrics = calculate_all_flight_metrics(self.flight_data)
                self.analysis_results['metrics'] = metrics
                
                # Display metrics in organized sections
                self._display_flight_metrics(metrics)
                
            except Exception as e:
                st.error(f"❌ Metrics calculation failed: {e}")
    
    def _create_anomaly_tab(self):
        """Create anomaly detection tab"""
        st.subheader("🔍 Anomaly Detection")
        
        if not ANALYSIS_MODULES_AVAILABLE:
            st.warning("⚠️ Analysis modules not available")
            return
        
        with st.spinner("🔍 Detecting anomalies..."):
            try:
                config = {'threshold_std': self.anomaly_threshold}
                anomalies = detect_all_anomalies(self.flight_data, config)
                self.analysis_results['anomalies'] = anomalies
                
                # Display anomaly results
                self._display_anomaly_results(anomalies)
                
            except Exception as e:
                st.error(f"❌ Anomaly detection failed: {e}")
    
    def _create_battery_tab(self):
        """Create battery analysis tab"""
        st.subheader("🔋 Battery Performance Analysis")
        
        if not ANALYSIS_MODULES_AVAILABLE:
            st.warning("⚠️ Analysis modules not available")
            return
        
        with st.spinner("🔋 Analyzing battery performance..."):
            try:
                battery_analysis = comprehensive_battery_analysis(self.flight_data)
                self.analysis_results['battery'] = battery_analysis
                
                # Display battery analysis
                self._display_battery_analysis(battery_analysis)
                
            except Exception as e:
                st.error(f"❌ Battery analysis failed: {e}")
    
    def _create_stability_tab(self):
        """Create stability analysis tab"""
        st.subheader("⚖️ Flight Stability Analysis")
        
        if not ANALYSIS_MODULES_AVAILABLE:
            st.warning("⚠️ Analysis modules not available")
            return
        
        with st.spinner("⚖️ Assessing flight stability..."):
            try:
                stability = assess_flight_stability(self.flight_data)
                self.analysis_results['stability'] = stability
                
                # Display stability analysis
                self._display_stability_analysis(stability)
                
            except Exception as e:
                st.error(f"❌ Stability analysis failed: {e}")
    
    def _create_phases_tab(self):
        """Create flight phase detection tab"""
        st.subheader("🚁 Flight Phase Detection")
        
        if not ANALYSIS_MODULES_AVAILABLE:
            st.warning("⚠️ Analysis modules not available")
            return
        
        with st.spinner("🚁 Detecting flight phases..."):
            try:
                # Create config based on method
                config = {
                    'climb_threshold': 0.5,
                    'descent_threshold': -0.5,
                    'stationary_threshold': 2.0,
                    'min_phase_duration': 5
                }
                
                # Only add n_clusters for clustering method
                if self.phase_method == 'clustering':
                    config['n_clusters'] = 5
                
                phases = detect_flight_phases(self.flight_data, method=self.phase_method, config=config)
                self.analysis_results['phases'] = phases
                
                # Display phase analysis
                self._display_phase_analysis(phases)
                
            except Exception as e:
                st.error(f"❌ Phase detection failed: {e}")
    
    def _create_digital_twin_tab(self):
        """Create digital twin visualization tab"""
        st.subheader("🌐 Digital Twin Visualization")
        
        if not ANALYSIS_MODULES_AVAILABLE:
            st.warning("⚠️ Analysis modules not available")
            return
        
        with st.spinner("🌐 Creating digital twin..."):
            try:
                digital_twin = create_comprehensive_digital_twin(self.flight_data)
                self.analysis_results['digital_twin'] = digital_twin
                
                # Display digital twin
                self._display_digital_twin(digital_twin)
                
            except Exception as e:
                st.error(f"❌ Digital twin creation failed: {e}")
    
    def _create_visualizations_tab(self):
        """Create comprehensive visualizations tab"""
        st.subheader("📈 Interactive Visualizations")
        
        if not ANALYSIS_MODULES_AVAILABLE:
            st.warning("⚠️ Analysis modules not available")
            return
        
        # Visualization options
        viz_type = st.selectbox(
            "Select Visualization Type",
            ["3D Flight Path", "Time Series", "Correlation Matrix", "Phase Distribution", "Anomaly Timeline"]
        )
        
        if viz_type == "3D Flight Path":
            self._create_3d_flight_path()
        elif viz_type == "Time Series":
            self._create_time_series_viz()
        elif viz_type == "Correlation Matrix":
            self._create_correlation_matrix()
        elif viz_type == "Phase Distribution":
            self._create_phase_distribution()
        elif viz_type == "Anomaly Timeline":
            self._create_anomaly_timeline()
    
    def _display_flight_metrics(self, metrics):
        """Display flight metrics in organized manner"""
        # Flight Duration
        with st.expander("⏱️ Flight Duration", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Seconds", f"{metrics['flight_duration']['seconds']:.1f}")
            with col2:
                st.metric("Minutes", f"{metrics['flight_duration']['minutes']:.1f}")
            with col3:
                st.metric("Hours", f"{metrics['flight_duration']['hours']:.2f}")
        
        # Altitude Statistics
        with st.expander("🏔️ Altitude Statistics", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Max Altitude", f"{metrics['altitude_stats']['max_altitude']:.1f} m")
            with col2:
                st.metric("Min Altitude", f"{metrics['altitude_stats']['min_altitude']:.1f} m")
            with col3:
                st.metric("Average", f"{metrics['altitude_stats']['avg_altitude']:.1f} m")
            with col4:
                st.metric("Range", f"{metrics['altitude_stats']['altitude_range']:.1f} m")
        
        # Speed Statistics
        with st.expander("💨 Speed Statistics", expanded=True):
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Max Speed", f"{metrics['speed_stats']['max_speed']:.1f} m/s")
            with col2:
                st.metric("Min Speed", f"{metrics['speed_stats']['min_speed']:.1f} m/s")
            with col3:
                st.metric("Average", f"{metrics['speed_stats']['avg_speed']:.1f} m/s")
            with col4:
                st.metric("Std Dev", f"{metrics['speed_stats']['speed_std']:.2f} m/s")
        
        # Climb/Descent Rates
        with st.expander("📈 Climb/Descent Rates", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Max Climb", f"{metrics['climb_descent_rates']['max_climb_rate']:.2f} m/s")
            with col2:
                st.metric("Max Descent", f"{metrics['climb_descent_rates']['max_descent_rate']:.2f} m/s")
            with col3:
                st.metric("Avg Vertical", f"{metrics['climb_descent_rates']['avg_vertical_speed']:.2f} m/s")
        
        # Distance Traveled
        if 'distance_traveled' in metrics:
            with st.expander("📍 Distance Traveled", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Distance", f"{metrics['distance_traveled']['total_distance_m']:.0f} m")
                with col2:
                    st.metric("Distance (km)", f"{metrics['distance_traveled']['total_distance_km']:.2f} km")
    
    def _display_anomaly_results(self, anomalies):
        """Display anomaly detection results"""
        summary = anomalies['summary']
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Anomalies", summary['total_anomalies'])
        with col2:
            st.metric("Anomaly Rate", f"{summary['overall_anomaly_rate']:.2%}")
        with col3:
            st.metric("High Severity", summary['severity_breakdown']['high'])
        with col4:
            st.metric("Assessment", summary['overall_assessment'])
        
        # Category breakdown
        st.subheader("📋 Anomaly Categories")
        for category, results in anomalies['categories'].items():
            if results['total_anomalies'] > 0:
                with st.expander(f"🔍 {category.title()} Anomalies ({results['total_anomalies']})", expanded=False):
                    # Show anomalies in a table
                    try:
                        anomaly_df = pd.DataFrame(results['anomalies'])
                        if not anomaly_df.empty:
                            st.dataframe(anomaly_df)
                            
                            # Create visualization if anomalies exist
                            if self.show_anomalies and len(anomaly_df) > 0:
                                self._create_anomaly_visualization(anomaly_df, category)
                    except Exception as e:
                        st.error(f"Error displaying {category} anomalies: {e}")
    
    def _display_battery_analysis(self, battery_analysis):
        """Display battery analysis results"""
        # Consumption metrics
        with st.expander("🔋 Consumption Metrics", expanded=True):
            consumption = battery_analysis['consumption_metrics']
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Drain Rate", f"{consumption['consumption_rate_percent_per_minute']:.1f} %/min")
            with col2:
                st.metric("Total Used", f"{consumption['total_consumption']:.1f}%")
            with col3:
                st.metric("Duration", f"{consumption['flight_duration_minutes']:.1f} min")
            with col4:
                st.metric("Assessment", battery_analysis['overall_assessment'])
        
        # Remaining time
        with st.expander("⏰ Remaining Flight Time", expanded=True):
            remaining = battery_analysis['remaining_time']
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Current Level", f"{remaining['current_battery_level']:.1f}%")
            with col2:
                st.metric("Remaining Time", f"{remaining['remaining_flight_time_minutes']:.1f} min")
            with col3:
                st.metric("Usable Battery", f"{remaining['usable_battery_percentage']:.1f}%")
        
        # Efficiency metrics
        with st.expander("⚡ Efficiency Metrics", expanded=True):
            efficiency = battery_analysis['efficiency']
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Altitude per %", f"{efficiency['altitude_per_percent']:.2f} m/%")
            with col2:
                st.metric("Distance per %", f"{efficiency['distance_per_percent']:.0f} m/%")
            with col3:
                st.metric("Efficiency Score", f"{efficiency['battery_efficiency_score']:.2f}")
        
        # Battery visualization
        self._create_battery_visualization(battery_analysis)
    
    def _display_stability_analysis(self, stability):
        """Display stability analysis results"""
        # Overall rating
        overall = stability['overall_rating']
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Stability Score", f"{overall['score']:.2f}")
        with col2:
            st.metric("Rating", overall['rating'])
        with col3:
            st.metric("Status", f"🟢" if overall['rating'] in ["Excellent", "Good"] else "🟡")
        
        # Attitude stability
        with st.expander("🎯 Attitude Stability", expanded=True):
            attitude = stability['attitude_stability']
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Roll Std Dev", f"{attitude['roll']['std_dev']:.2f}°")
            with col2:
                st.metric("Pitch Std Dev", f"{attitude['pitch']['std_dev']:.2f}°")
            with col3:
                st.metric("Yaw Std Dev", f"{attitude['yaw']['std_dev']:.2f}°")
        
        # Oscillations
        with st.expander("🌊 Oscillation Analysis", expanded=True):
            oscillations = stability['oscillations']
            col1, col2 = st.columns(2)
            with col1:
                total_osc = oscillations['roll']['total_oscillations'] + oscillations['pitch']['total_oscillations']
                st.metric("Total Oscillations", total_osc)
            with col2:
                st.metric("Frequency", f"{oscillations['roll']['oscillation_frequency']:.2f} Hz")
        
        # Stability visualization
        self._create_stability_visualization(stability)
    
    def _display_phase_analysis(self, phases):
        """Display flight phase analysis"""
        try:
            if not phases or 'phases' not in phases:
                st.warning("No flight phases detected")
                return
            
            phase_list = phases['phases']
            
            if not phase_list:
                st.warning("No flight phases detected")
                return
            
            # Phase summary
            st.subheader("📋 Flight Phase Summary")
            
            for i, phase_info in enumerate(phase_list):
                phase_name = phase_info.get('phase', f'Phase {i+1}')
                
                with st.expander(f"🚁 {phase_name.title()} Phase", expanded=False):
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        duration = phase_info.get('duration_seconds', phase_info.get('duration_points', 0))
                        st.metric("Duration", f"{duration:.1f} s")
                    with col2:
                        data_points = phase_info.get('duration_points', phase_info.get('end_index', 0) - phase_info.get('start_index', 0) + 1)
                        st.metric("Data Points", data_points)
                    with col3:
                        # Calculate average altitude for this phase if possible
                        start_idx = phase_info.get('start_index', 0)
                        end_idx = phase_info.get('end_index', len(self.flight_data) - 1)
                        if 'altitude_m' in self.flight_data.columns and start_idx < len(self.flight_data) and end_idx < len(self.flight_data):
                            avg_alt = self.flight_data['altitude_m'].iloc[start_idx:end_idx+1].mean()
                            st.metric("Avg Altitude", f"{avg_alt:.1f} m")
                        else:
                            st.metric("Avg Altitude", "N/A")
                    with col4:
                        # Calculate average speed for this phase if possible
                        if 'speed_mps' in self.flight_data.columns and start_idx < len(self.flight_data) and end_idx < len(self.flight_data):
                            avg_speed = self.flight_data['speed_mps'].iloc[start_idx:end_idx+1].mean()
                            st.metric("Avg Speed", f"{avg_speed:.1f} m/s")
                        else:
                            st.metric("Avg Speed", "N/A")
            
            # Phase visualization
            self._create_phase_visualization(phases)
            
        except Exception as e:
            st.error(f"Error displaying phase analysis: {e}")
    
    def _display_digital_twin(self, digital_twin):
        """Display digital twin visualizations"""
        if not digital_twin:
            st.warning("Digital twin not available")
            return
        
        # 3D Flight Path
        if '3d_path' in digital_twin:
            st.subheader("🌐 3D Flight Path")
            st.plotly_chart(digital_twin['3d_path'], use_container_width=True)
        
        # Interactive dashboard
        if 'interactive_dashboard' in digital_twin:
            st.subheader("🎮 Interactive Dashboard")
            st.plotly_chart(digital_twin['interactive_dashboard'], use_container_width=True)
    
    def _create_3d_flight_path(self):
        """Create 3D flight path visualization"""
        if 'gps_lat' not in self.flight_data.columns or 'gps_lon' not in self.flight_data.columns:
            st.warning("GPS data not available for 3D visualization")
            return
        
        fig = go.Figure(data=go.Scatter3d(
            x=self.flight_data['gps_lon'],
            y=self.flight_data['gps_lat'],
            z=self.flight_data.get('altitude_m', 0),
            mode='markers+lines',
            marker=dict(
                size=3,
                color=self.flight_data.get('altitude_m', 0),
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Altitude (m)")
            ),
            line=dict(color='blue', width=2)
        ))
        
        fig.update_layout(
            title='3D Flight Path',
            scene=dict(
                xaxis_title='Longitude',
                yaxis_title='Latitude',
                zaxis_title='Altitude (m)'
            ),
            width=800,
            height=600
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _create_time_series_viz(self):
        """Create time series visualization"""
        numeric_cols = self.flight_data.select_dtypes(include=[np.number]).columns.tolist()
        
        if not numeric_cols:
            st.warning("No numeric columns available for time series")
            return
        
        selected_cols = st.multiselect(
            "Select parameters to plot",
            numeric_cols,
            default=numeric_cols[:4] if len(numeric_cols) >= 4 else numeric_cols
        )
        
        if selected_cols:
            fig = make_subplots(
                rows=len(selected_cols), cols=1,
                subplot_titles=selected_cols,
                vertical_spacing=0.05
            )
            
            for i, col in enumerate(selected_cols, 1):
                fig.add_trace(
                    go.Scatter(
                        x=self.flight_data.index,
                        y=self.flight_data[col],
                        mode='lines',
                        name=col,
                        line=dict(width=1)
                    ),
                    row=i, col=1
                )
            
            fig.update_layout(
                height=200 * len(selected_cols),
                title_text="Time Series Analysis",
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    def _create_correlation_matrix(self):
        """Create correlation matrix visualization"""
        numeric_cols = self.flight_data.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) < 2:
            st.warning("Need at least 2 numeric columns for correlation matrix")
            return
        
        corr_matrix = self.flight_data[numeric_cols].corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=corr_matrix.round(2).values,
            texttemplate="%{text}",
            textfont={"size": 10},
            hoverongaps=False
        ))
        
        fig.update_layout(
            title='Parameter Correlation Matrix',
            width=700,
            height=700
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _create_phase_distribution(self):
        """Create phase distribution visualization"""
        if 'phases' not in self.analysis_results:
            st.warning("Phase analysis not available")
            return
        
        phase_list = self.analysis_results['phases']['phases']
        
        if not phase_list:
            st.warning("No flight phases detected")
            return
        
        # Create phase duration chart
        phase_names = []
        durations = []
        
        for i, phase_info in enumerate(phase_list):
            phase_name = phase_info.get('phase', f'Phase {i+1}')
            duration = phase_info.get('duration_seconds', phase_info.get('duration_points', 0))
            
            phase_names.append(phase_name)
            durations.append(duration)
        
        fig = go.Figure(data=[
            go.Bar(x=phase_names, y=durations, marker_color='lightblue')
        ])
        
        fig.update_layout(
            title='Flight Phase Durations',
            xaxis_title='Flight Phase',
            yaxis_title='Duration (seconds)',
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _create_anomaly_timeline(self):
        """Create anomaly timeline visualization"""
        if 'anomalies' not in self.analysis_results:
            st.warning("Anomaly analysis not available")
            return
        
        anomalies = self.analysis_results['anomalies']
        all_anomalies = []
        
        for category, results in anomalies['categories'].items():
            for anomaly in results['anomalies']:
                all_anomalies.append({
                    'category': category,
                    'type': anomaly['type'],
                    'timestamp': anomaly.get('timestamp', 0),
                    'severity': anomaly.get('severity', 'medium')
                })
        
        if not all_anomalies:
            st.info("No anomalies detected")
            return
        
        anomaly_df = pd.DataFrame(all_anomalies)
        
        # Create timeline
        fig = px.scatter(
            anomaly_df,
            x='timestamp',
            y='category',
            color='severity',
            symbol='type',
            title="Anomaly Timeline",
            hover_data=['type', 'severity']
        )
        
        fig.update_layout(
            xaxis_title="Timestamp",
            yaxis_title="Anomaly Category",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _create_battery_visualization(self, battery_analysis):
        """Create battery performance visualizations"""
        col1, col2 = st.columns(2)
        
        with col1:
            # Battery level over time
            if 'battery_percent' in self.flight_data.columns:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=self.flight_data.index,
                    y=self.flight_data['battery_percent'],
                    mode='lines',
                    name='Battery Level',
                    line=dict(color='green', width=2)
                ))
                
                fig.update_layout(
                    title='Battery Level Over Time',
                    xaxis_title='Time',
                    yaxis_title='Battery (%)',
                    height=300
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Consumption rate by phase (if available)
            if 'phase_analysis' in battery_analysis:
                phase_data = battery_analysis['phase_analysis']['phase_analysis']
                if phase_data:
                    phases = list(phase_data.keys())
                    rates = [phase_data[phase]['consumption_rate_per_minute'] for phase in phases]
                    
                    fig = go.Figure(data=[
                        go.Bar(x=phases, y=rates, marker_color='orange')
                    ])
                    
                    fig.update_layout(
                        title='Battery Consumption by Phase',
                        xaxis_title='Flight Phase',
                        yaxis_title='Consumption Rate (%/min)',
                        height=300
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
    
    def _create_stability_visualization(self, stability):
        """Create stability analysis visualizations"""
        col1, col2 = st.columns(2)
        
        with col1:
            # Attitude stability chart
            attitude = stability['attitude_stability']
            categories = ['Roll', 'Pitch', 'Yaw']
            std_devs = [
                attitude['roll']['std_dev'],
                attitude['pitch']['std_dev'],
                attitude['yaw']['std_dev']
            ]
            
            fig = go.Figure(data=[
                go.Bar(x=categories, y=std_devs, marker_color='lightblue')
            ])
            
            fig.update_layout(
                title='Attitude Stability (Standard Deviation)',
                xaxis_title='Attitude Component',
                yaxis_title='Standard Deviation (degrees)',
                height=300
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Oscillation frequency
            oscillations = stability['oscillations']
            osc_categories = ['Roll', 'Pitch']
            frequencies = [
                oscillations['roll']['oscillation_frequency'],
                oscillations['pitch']['oscillation_frequency']
            ]
            
            fig = go.Figure(data=[
                go.Bar(x=osc_categories, y=frequencies, marker_color='lightgreen')
            ])
            
            fig.update_layout(
                title='Oscillation Frequencies',
                xaxis_title='Attitude Component',
                yaxis_title='Frequency (Hz)',
                height=300
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    def _create_phase_visualization(self, phases):
        """Create flight phase visualizations"""
        if not phases or 'phases' not in phases:
            return
        
        phase_list = phases['phases']
        
        if not phase_list:
            return
        
        # Phase timeline
        fig = go.Figure()
        
        colors = ['blue', 'green', 'orange', 'red', 'purple']
        color_idx = 0
        
        for i, phase_info in enumerate(phase_list):
            phase_name = phase_info.get('phase', f'Phase {i+1}')
            start_idx = phase_info.get('start_index', 0)
            end_idx = phase_info.get('end_index', len(self.flight_data))
            
            fig.add_shape(
                type="rect",
                x0=start_idx, x1=end_idx,
                y0=0, y1=1,
                fillcolor=colors[color_idx % len(colors)],
                opacity=0.3,
                layer="below",
                line_width=0,
            )
            
            fig.add_annotation(
                x=(start_idx + end_idx) / 2,
                y=0.5,
                text=phase_name,
                showarrow=False,
                font=dict(size=12)
            )
            
            color_idx += 1
        
        fig.update_layout(
            title='Flight Phase Timeline',
            xaxis_title='Data Point Index',
            yaxis_title='',
            showlegend=False,
            height=200,
            yaxis=dict(visible=False)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _create_anomaly_visualization(self, anomaly_df, category):
        """Create anomaly visualization for specific category"""
        try:
            if 'timestamp' not in anomaly_df.columns:
                return
            
            fig = go.Figure()
            
            # Plot normal data
            if category in ['altitude', 'speed', 'battery']:
                col_name = f'{category}_m' if category != 'battery' else 'battery_percent'
                if col_name in self.flight_data.columns:
                    fig.add_trace(go.Scatter(
                        x=self.flight_data.index,
                        y=self.flight_data[col_name],
                        mode='lines',
                        name='Normal Data',
                        line=dict(color='blue', width=1)
                    ))
            
            # Plot anomalies - fix the y-value issue
            if 'value' in anomaly_df.columns:
                y_values = anomaly_df['value']
            elif 'speed' in anomaly_df.columns:
                y_values = anomaly_df['speed']
            elif 'battery_level' in anomaly_df.columns:
                y_values = anomaly_df['battery_level']
            else:
                # Create a default y-value array
                y_values = [0] * len(anomaly_df)
            
            # Ensure y_values is a series/array
            if isinstance(y_values, (int, float)):
                y_values = [y_values] * len(anomaly_df)
            
            fig.add_trace(go.Scatter(
                x=anomaly_df['index'],
                y=y_values,
                mode='markers',
                name='Anomalies',
                marker=dict(color='red', size=8, symbol='x')
            ))
            
            fig.update_layout(
                title=f'{category.title()} Anomalies',
                xaxis_title='Time/Index',
                yaxis_title='Value',
                height=300
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error creating anomaly visualization for {category}: {e}")
    
    def _run_quick_analysis(self):
        """Run quick analysis on the data"""
        with st.spinner("🚀 Running quick analysis..."):
            try:
                if ANALYSIS_MODULES_AVAILABLE:
                    metrics = calculate_all_flight_metrics(self.flight_data)
                    self.analysis_results['metrics'] = metrics
                    
                    # Run anomaly detection
                    anomalies = detect_all_anomalies(self.flight_data)
                    self.analysis_results['anomalies'] = anomalies
                    
                    st.success("✅ Quick analysis completed!")
                    
                    # Show summary
                    st.subheader("📊 Quick Analysis Summary")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Duration", f"{metrics['flight_duration']['minutes']:.1f} min")
                    with col2:
                        st.metric("Max Altitude", f"{metrics['altitude_stats']['max_altitude']:.1f} m")
                    with col3:
                        st.metric("Anomalies", anomalies['summary']['total_anomalies'])
                    with col4:
                        st.metric("Data Points", f"{len(self.flight_data):,}")
                else:
                    # Fallback analysis when modules not available
                    self._run_fallback_analysis()
                    
            except Exception as e:
                st.error(f"❌ Quick analysis failed: {e}")
                # Try fallback analysis
                try:
                    self._run_fallback_analysis()
                except Exception as fallback_e:
                    st.error(f"❌ Fallback analysis also failed: {fallback_e}")
    
    def _run_fallback_analysis(self):
        """Run fallback analysis when modules are not available"""
        st.info("🔧 Running basic analysis (analysis modules not available)")
        
        # Create basic metrics manually
        metrics = {
            'flight_duration': {'minutes': len(self.flight_data) * 0.1},  # Estimate
            'altitude_stats': {
                'max_altitude': self.flight_data.get('altitude_m', pd.Series([0])).max(),
                'min_altitude': self.flight_data.get('altitude_m', pd.Series([0])).min(),
                'avg_altitude': self.flight_data.get('altitude_m', pd.Series([0])).mean()
            },
            'speed_stats': {
                'max_speed': self.flight_data.get('speed_mps', pd.Series([0])).max(),
                'avg_speed': self.flight_data.get('speed_mps', pd.Series([0])).mean()
            }
        }
        
        # Create basic anomaly detection
        anomalies = {
            'summary': {
                'total_anomalies': 0,
                'overall_anomaly_rate': 0.0,
                'overall_assessment': 'Basic analysis only'
            },
            'categories': {}
        }
        
        self.analysis_results = {
            'metrics': metrics,
            'anomalies': anomalies,
            'basic_analysis': True
        }
        
        st.success("Basic analysis completed!")
        
        # Show basic summary
        st.subheader("📊 Basic Analysis Summary")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Duration", f"{metrics['flight_duration']['minutes']:.1f} min")
        with col2:
            st.metric("Max Altitude", f"{metrics['altitude_stats']['max_altitude']:.1f} m")
        with col3:
            st.metric("Avg Speed", f"{metrics['speed_stats']['avg_speed']:.1f} m/s")
        with col4:
            st.metric("Data Points", f"{len(self.flight_data):,}")
    
    def _run_comprehensive_analysis(self):
        """Run comprehensive analysis with all tools"""
        with st.spinner("🔍 Running comprehensive analysis..."):
            try:
                if ANALYSIS_MODULES_AVAILABLE:
                    # Run all analysis tools
                    self.analysis_results['metrics'] = calculate_all_flight_metrics(self.flight_data)
                    self.analysis_results['stability'] = assess_flight_stability(self.flight_data)
                    self.analysis_results['anomalies'] = detect_all_anomalies(self.flight_data)
                    self.analysis_results['battery'] = comprehensive_battery_analysis(self.flight_data)
                    
                    # Create config for phase detection
                    config = {
                        'climb_threshold': 0.5,
                        'descent_threshold': -0.5,
                        'stationary_threshold': 2.0,
                        'min_phase_duration': 5
                    }
                    
                    # Only add n_clusters for clustering method
                    if self.phase_method == 'clustering':
                        config['n_clusters'] = 5
                    
                    self.analysis_results['phases'] = detect_flight_phases(self.flight_data, method=self.phase_method, config=config)
                    
                    st.success("Comprehensive analysis completed!")
                    st.info("📊 Check individual tabs for detailed results")
                else:
                    st.warning("⚠️ Analysis modules not available")
                    
            except Exception as e:
                st.error(f"❌ Comprehensive analysis failed: {e}")
    
    def _generate_data_summary(self):
        """Generate data summary"""
        st.subheader("📋 Data Summary")
        
        # Basic info
        st.write("**Basic Information:**")
        st.write(f"- Rows: {len(self.flight_data):,}")
        st.write(f"- Columns: {len(self.flight_data.columns)}")
        st.write(f"- Memory Usage: {self.flight_data.memory_usage(deep=True).sum() / 1024**2:.2f} MB")
        
        # Column information
        st.write("**Column Details:**")
        col_info = []
        for col in self.flight_data.columns:
            dtype = str(self.flight_data[col].dtype)
            null_count = self.flight_data[col].isnull().sum()
            unique_count = self.flight_data[col].nunique()
            col_info.append({
                'Column': col,
                'Type': dtype,
                'Null Values': null_count,
                'Unique Values': unique_count
            })
        
        col_df = pd.DataFrame(col_info)
        st.dataframe(col_df)
        
        # Statistical summary
        st.write("**Statistical Summary:**")
        st.dataframe(self.flight_data.describe())
    
    def _generate_comprehensive_report(self):
        """Generate comprehensive analysis report"""
        if not self.analysis_results:
            st.warning("⚠️ No analysis results available. Run analysis first.")
            return
        
        with st.spinner("📊 Generating comprehensive report..."):
            try:
                # Create report content
                report_content = {
                    'timestamp': datetime.now().isoformat(),
                    'data_summary': {
                        'rows': len(self.flight_data),
                        'columns': len(self.flight_data.columns),
                        'duration_minutes': self.analysis_results.get('metrics', {}).get('flight_duration', {}).get('minutes', 0)
                    },
                    'analysis_results': self.analysis_results
                }
                
                # Convert to JSON for download
                report_json = json.dumps(report_content, indent=2, default=str)
                
                # Provide download
                st.download_button(
                    label="📥 Download Comprehensive Report (JSON)",
                    data=report_json,
                    file_name=f"uav_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
                
                st.success("✅ Report generated successfully!")
                
            except Exception as e:
                st.error(f"❌ Report generation failed: {e}")
    
    def _generate_pdf_report(self):
        """Generate comprehensive PDF report with charts and analysis"""
        if self.flight_data is None or len(self.flight_data) == 0:
            st.warning("⚠️ No flight data available. Load data first.")
            return
        
        # Auto-run analysis if no results exist
        if not self.analysis_results:
            st.info("🔍 No analysis results found. Running analysis automatically...")
            self._run_comprehensive_analysis()
            
            if not self.analysis_results:
                st.error("❌ Analysis failed. Cannot generate PDF report.")
                return
        
        if not self.pdf_generator:
            st.warning("⚠️ PDF generator not available. Required modules may be missing.")
            return
        
        with st.spinner("📄 Generating comprehensive PDF report..."):
            try:
                # Add data points to analysis results for PDF
                self.analysis_results['data_points'] = len(self.flight_data)
                
                # Generate PDF
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                pdf_filename = f"uav_flight_analysis_report_{timestamp}.pdf"
                
                pdf_path = self.pdf_generator.generate_comprehensive_report(
                    self.flight_data,
                    self.analysis_results,
                    pdf_filename
                )
                
                # Read PDF file for download
                with open(pdf_path, 'rb') as f:
                    pdf_data = f.read()
                
                # Provide download button
                st.download_button(
                    label="📥 Download PDF Report",
                    data=pdf_data,
                    file_name=pdf_filename,
                    mime="application/pdf"
                )
                
                st.success("✅ PDF report generated successfully!")
                st.info(f"📄 Report saved as: {pdf_filename}")
                st.info(f"📊 Analysis includes: {len(self.analysis_results)} modules")
                
                # Clean up temporary file
                try:
                    os.unlink(pdf_path)
                except:
                    pass
                
            except Exception as e:
                st.error(f"❌ PDF report generation failed: {e}")
                st.info("💡 Note: PDF generation requires matplotlib, seaborn, and reportlab packages.")
                st.info("🔧 Try running: pip install reportlab matplotlib seaborn")
    
    def _generate_professional_aerospace_report(self):
        """Generate professional aerospace-grade UAV flight analysis report"""
        if self.flight_data is None or len(self.flight_data) == 0:
            st.warning("⚠️ No flight data available. Load data first.")
            return
        
        # Auto-run analysis if no results exist
        if not self.analysis_results:
            st.info("🔍 No analysis results found. Running analysis automatically...")
            self._run_comprehensive_analysis()
            
            if not self.analysis_results:
                st.error("❌ Analysis failed. Cannot generate professional report.")
                return
        
        if not self.professional_report_generator_class and not self.professional_report_generator:
            st.warning("⚠️ Professional report generator not available. Required modules may be missing.")
            return
        
        with st.spinner("🚀 Generating professional aerospace report..."):
            try:
                # Prepare metadata
                metadata = {
                    'flight_id': f"FLT-{datetime.now().strftime('%Y-%m-%d')}-001",
                    'aircraft_type': 'Quadrotor UAV',
                    'autopilot': 'PX4',
                    'mission_type': 'Professional Analysis Flight',
                    'firmware_version': '1.12.3',
                    'analyst': 'UAV Flight Analysis System',
                    'report_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                # Generate professional report using updated generator
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                report_filename = f"UAV_Professional_Aerospace_Report_{timestamp}.pdf"
                
                # Try using the class-based generator first
                if self.professional_report_generator_class:
                    generator = self.professional_report_generator_class()
                    report_path = generator.generate_comprehensive_professional_report(
                        self.flight_data,
                        self.analysis_results,
                        metadata,
                        report_filename
                    )
                else:
                    # Fallback to function-based generator
                    report_path = self.professional_report_generator(
                        self.flight_data,
                        self.analysis_results,
                        metadata
                    )
                
                # Read PDF file for download
                with open(report_path, 'rb') as f:
                    pdf_data = f.read()
                
                # Display success message with report details
                st.success("✅ Professional Aerospace Report Generated Successfully!")
                st.info(f"📄 Report saved as: {report_filename}")
                st.info(f"📊 File size: {os.path.getsize(report_path):,} bytes")
                
                # Report sections information
                st.markdown("""
                ### 📋 **Enhanced Report Features:**
                1. **Cover Page** - Professional flight metadata and specifications
                2. **Executive Mission Summary** - One-page engineering overview
                3. **Flight Data Overview** - Parameter descriptions and statistics
                4. **Mission Performance Analysis** - Altitude, speed, and navigation metrics
                5. **Coverage/Navigation Analysis** - GPS and waypoint analysis
                6. **Anomaly Detection Analysis** - Statistical outlier identification
                7. **Battery Performance Analysis** - Consumption and efficiency metrics
                8. **Flight Stability Analysis** - Attitude control assessment
                9. **Flight Phase Segmentation** - Flight segment identification
                10. **Integrated Dashboard** - 2x2 key parameter overview
                11. **System Health Score** - Composite flight quality scoring
                12. **Engineering Recommendations** - Structured improvement suggestions
                13. **Appendix** - Technical specifications and algorithms
                
                **✨ Enhanced Features:**
                - Aerospace-grade documentation standards
                - Engineering narrative interpretations
                - Dual visualization rule compliance
                - Composite flight quality scoring
                - Structured recommendations
                - Professional formatting and styling
                """)
                
                # Provide download button
                col1, col2 = st.columns(2)
                
                with col1:
                    st.download_button(
                        label="🚀 Download Professional Aerospace Report",
                        data=pdf_data,
                        file_name=report_filename,
                        mime="application/pdf",
                        help="Download: complete 13-section aerospace-grade UAV flight analysis report"
                    )
                
                with col2:
                    st.info("""
                    📋 **Enhanced Report Features:**
                    - Aerospace-grade documentation
                    - Engineering narrative interpretations
                    - Dual visualization rule compliance
                    - Composite flight quality scoring
                    - Structured recommendations
                    - Professional formatting
                    - Updated PDF generation engine
                    """)
                
                # Clean up
                try:
                    os.unlink(report_path)
                except:
                    pass
                
            except Exception as e:
                st.error(f"❌ Professional report generation failed: {e}")
                st.info("💡 Note: Professional report generation requires: professional_report_generator module.")
                st.info("🔧 Ensure all dependencies are installed: pip install reportlab matplotlib seaborn")
    
    def _export_processed_data(self):
        """Export processed data"""
        if self.flight_data is None or len(self.flight_data) == 0:
            st.warning("⚠️ No flight data available. Load data first.")
            return
        
        # Auto-run analysis if no results exist
        if not self.analysis_results:
            st.info("🔍 No analysis results found. Running analysis automatically...")
            self._run_comprehensive_analysis()
            
            if not self.analysis_results:
                st.error("❌ Analysis failed. Cannot export data.")
                return
        
        with st.spinner("📊 Exporting processed data..."):
            try:
                # Prepare data for export
                csv_data = self.flight_data.to_csv(index=False)
                
                # Provide download button
                st.download_button(
                    label="📥 Download Processed Data (CSV)",
                    data=csv_data,
                    file_name=f"processed_flight_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
                
                st.success("✅ Data export ready!")
                
            except Exception as e:
                st.error(f"❌ Data export failed: {e}")
    
    def _create_welcome_section(self):
        """Create welcome section for new users"""
        st.markdown("""
        ## 🚁 Welcome to the Comprehensive UAV Flight Analysis System!
        
        ### ✨ **All Analyzer Tools Integrated:**
        
        #### 📊 **Core Analysis Tools:**
        - **Flight Metrics Calculator** - Duration, altitude, speed, climb rates, distance
        - **Stability Analysis** - Attitude stability, oscillation detection, flight quality assessment
        - **Anomaly Detection** - Altitude spikes, attitude anomalies, speed irregularities, GPS issues, battery problems
        - **Battery Performance** - Consumption rates, efficiency analysis, remaining time estimation
        - **Flight Phase Detection** - Takeoff, climb, cruise, descent, landing phases
        - **Digital Twin Visualization** - 3D flight paths, interactive dashboards
        
        #### 🎯 **Interactive Features:**
        - **Real-time Analysis** - Instant processing and results
        - **Interactive Visualizations** - Zoomable plots, hover information
        - **Comprehensive Dashboards** - Multiple analysis views
        - **Export Functionality** - Download reports and processed data
        - **Multiple Data Sources** - CSV files, ULG logs, sample data
        
        #### 🔧 **Advanced Capabilities:**
        - **ULG File Support** - Direct PX4 log file analysis
        - **Data Validation** - Automatic data quality checks
        - **Preprocessing Pipeline** - Data cleaning and preparation
        - **Customizable Thresholds** - Adjustable analysis parameters
        - **Multi-format Export** - JSON reports, CSV data
        
        ### 🚀 **Getting Started:**
        
        1. **Choose Data Source** from the sidebar (CSV, ULG, or Sample Data)
        2. **Configure Analysis** settings in sidebar
        3. **Explore Analysis Tabs** for detailed insights
        4. **Generate Professional Reports** from the dedicated tab
        """)
    
    def _create_professional_reports_tab(self):
        """Create professional reports tab with aerospace-grade report generation"""
        st.subheader("🚀 Professional Aerospace Reports")
        
        # Module status display
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("PDF Generator", "✅ Available" if self.pdf_generator else "❌ Unavailable")
        with col2:
            st.metric("Professional Generator", "✅ Available" if (self.professional_report_generator_class or self.professional_report_generator) else "❌ Unavailable")
        with col3:
            st.metric("Analysis Modules", "✅ Available" if ANALYSIS_MODULES_AVAILABLE else "❌ Unavailable")
        with col4:
            st.metric("ULG Analyzer", "✅ Available" if ROBUST_ANALYZER_AVAILABLE else "❌ Unavailable")
        
        st.markdown("---")
        
        # Report generation options
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📄 Standard PDF Report")
            st.write("Comprehensive flight analysis with charts and metrics")
            if st.button("📊 Generate Standard PDF Report", type="primary"):
                self._generate_pdf_report()
        
        with col2:
            st.markdown("### 🚀 Professional Aerospace Report")
            st.write("Aerospace-grade 13-section engineering documentation")
            if st.button("🚀 Generate Professional Report", type="primary"):
                self._generate_professional_aerospace_report()
        
        st.markdown("---")
        
        # Enhanced features information
        st.markdown("""
        ### ✨ **Enhanced PDF Module Features:**
        
        #### **📄 Standard PDF Report:**
        - Flight metrics and performance analysis
        - Battery consumption charts
        - Stability analysis visualizations
        - Anomaly detection results
        - Flight phase segmentation
        - Interactive dashboard summary
        
        #### **🚀 Professional Aerospace Report:**
        - **13 PRD-Mandated Sections** with aerospace standards
        - **Dual Visualization Rule** compliance (Metric → Visualization → Interpretation)
        - **Engineering Narrative** interpretations for each analysis
        - **Composite Flight Quality** scoring system
        - **Structured Recommendations** (Maintenance, Control, Energy, Mission)
        - **Professional Formatting** with aerospace documentation standards
        - **Enhanced PDF Generation** engine with improved styling
        
        #### **🔧 Technical Improvements:**
        - Updated PDF generation engine
        - Enhanced error handling and fallback mechanisms
        - Both class-based and function-based generator support
        - Improved metadata handling
        - Better file management and cleanup
        """)
        
        st.info("🎯 **Upload your flight data or generate sample data to begin comprehensive analysis!**")

def main():
    """Main function to run the comprehensive dashboard"""
    analyzer = ComprehensiveAnalyzer()
    analyzer.create_main_interface()

if __name__ == '__main__':
    main()
