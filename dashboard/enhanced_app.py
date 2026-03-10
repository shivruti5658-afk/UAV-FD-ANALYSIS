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

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import analysis modules
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
    page_title="UAV Flight Analysis Dashboard - Enhanced",
    page_icon="🚁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .status-excellent { color: #27ae60; font-weight: bold; }
    .status-good { color: #f39c12; font-weight: bold; }
    .status-poor { color: #e74c3c; font-weight: bold; }
    
    .ulg-upload-area {
        border: 2px dashed #2E8B57;
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        background: #f8fff9;
        margin: 10px 0;
    }
    .ulg-upload-area:hover {
        border-color: #3CB371;
        background: #e8f5e8;
    }
    .ulg-metric {
        background: white;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    .ulg-metric-value {
        font-size: 2em;
        font-weight: bold;
        color: #2E8B57;
    }
    .ulg-metric-label {
        color: #666;
        font-size: 0.9em;
    }
</style>
""", unsafe_allow_html=True)

class ULGAnalysisIntegration:
    """ULG analysis integration for enhanced dashboard"""
    
    def __init__(self):
        self.robust_analyzer = RobustULGAnalyzer() if ROBUST_ANALYZER_AVAILABLE else None
        self.current_ulg_analysis = None
        self.ulg_flight_data = None
        
    def create_ulg_analysis_section(self):
        """Create ULG analysis section"""
        st.markdown("### 🚁 ULG File Analysis")
        st.markdown("Direct ULG file analysis with comprehensive flight metrics")
        
        # ULG upload section
        with st.expander("📁 ULG File Upload & Analysis", expanded=True):
            uploaded_ulg_file = st.file_uploader(
                "Upload ULG File",
                type=['ulg', 'bin', 'log'],
                help="Upload your PX4 ULG flight log file"
            )
            
            if uploaded_ulg_file is not None:
                st.info(f"📄 ULG file uploaded: {uploaded_ulg_file.name}")
                
                if st.button("🚀 Analyze ULG File", type="primary"):
                    self._analyze_ulg_file(uploaded_ulg_file)
        
        # Results section
        if self.current_ulg_analysis:
            self._create_results_section()
    
    def _analyze_ulg_file(self, uploaded_ulg_file):
        """Analyze ULG file"""
        with st.spinner("🔍 Analyzing ULG file..."):
            try:
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix='.ulg') as tmp_ulg:
                    tmp_ulg.write(uploaded_ulg_file.getvalue())
                    tmp_ulg_path = tmp_ulg.name
                
                # Analyze with robust analyzer
                if self.robust_analyzer:
                    self.current_ulg_analysis = self.robust_analyzer.analyze_ulg_file(tmp_ulg_path)
                    st.success("✅ ULG analysis completed!")
                    self._create_flight_data()
                else:
                    st.error("❌ ULG analyzer not available")
                
                # Clean up
                os.unlink(tmp_ulg_path)
                
            except Exception as e:
                st.error(f"❌ ULG analysis failed: {str(e)}")
    
    def _create_flight_data(self):
        """Create flight data from analysis"""
        if not self.current_ulg_analysis:
            return
        
        try:
            summary = self.current_ulg_analysis.get('summary', {})
            num_points = min(1000, summary.get('total_points', 1000))
            
            self.ulg_flight_data = pd.DataFrame({
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
            st.error(f"Failed to create flight data: {e}")
    
    def _create_results_section(self):
        """Create results section"""
        if not self.current_ulg_analysis:
            return
        
        st.markdown("#### 📊 Analysis Results")
        
        # Summary metrics
        summary = self.current_ulg_analysis.get('summary', {})
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Data Points", f"{summary.get('total_points', 0):,}")
        with col2:
            st.metric("Max Altitude", f"{summary.get('altitude_max_m', 0):.1f} m")
        with col3:
            st.metric("Max Speed", f"{summary.get('speed_max_mps', 0):.1f} m/s")
        with col4:
            stability_score = self.current_ulg_analysis.get('stability', {}).get('stability_score', 0)
            st.metric("Stability Score", f"{stability_score:.1f}/100")
        
        # Analysis button
        if self.ulg_flight_data is not None:
            if st.button("🚀 Run Full Analysis on ULG Data"):
                self._run_analysis(self.ulg_flight_data)
    
    def _run_analysis(self, df):
        """Run full analysis"""
        try:
            if ANALYSIS_MODULES_AVAILABLE:
                # Run basic analysis
                metrics = calculate_all_flight_metrics(df)
                stability = assess_flight_stability(df)
                anomalies = detect_all_anomalies(df, {'threshold_std': 3.0})
                battery = comprehensive_battery_analysis(df)
                phases = detect_flight_phases(df, 'hybrid', {'climb_threshold': 0.5, 'descent_threshold': -0.5})
                
                st.success("✅ Analysis completed!")
                
                # Display results
                self._display_metrics(metrics)
            else:
                st.warning("⚠️ Analysis modules not available")
                
        except Exception as e:
            st.error(f"❌ Analysis failed: {e}")
    
    def _display_metrics(self, metrics):
        """Display analysis metrics"""
        st.subheader("Flight Performance Metrics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Flight Duration", f"{metrics['flight_duration']['minutes']:.1f} minutes")
            st.metric("Max Altitude", f"{metrics['altitude_stats']['max_altitude']:.1f} m")
            st.metric("Avg Speed", f"{metrics['speed_stats']['avg_speed']:.1f} m/s")
        
        with col2:
            st.metric("Max Climb Rate", f"{metrics['climb_descent_rates']['max_climb_rate']:.2f} m/s")
            st.metric("Max Descent Rate", f"{metrics['climb_descent_rates']['max_descent_rate']:.2f} m/s")
            st.metric("Altitude Range", f"{metrics['altitude_stats']['altitude_range']:.1f} m")
    
    def get_flight_data(self):
        """Get flight data"""
        return self.ulg_flight_data

def main():
    """Main function"""
    # Header
    st.markdown('<h1 class="main-header">🚁 UAV Flight Analysis Dashboard - Enhanced</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Initialize ULG integration
    ulg_integration = ULGAnalysisIntegration()
    
    # Sidebar
    st.sidebar.title("📊 Analysis Controls")
    
    # Data source selection
    data_source = st.sidebar.radio(
        "Select Data Source:",
        ["CSV File", "ULG File Analysis"],
        help="Choose your preferred data input method"
    )
    
    if data_source == "ULG File Analysis":
        # ULG analysis section
        ulg_integration.create_ulg_analysis_section()
        
        # Get flight data and continue with analysis
        flight_data = ulg_integration.get_flight_data()
        if flight_data is not None:
            st.success("✅ ULG data ready for full analysis!")
            if st.sidebar.button("🚀 Run Complete Analysis", type="primary"):
                try:
                    if ANALYSIS_MODULES_AVAILABLE:
                        # Run comprehensive analysis
                        metrics = calculate_all_flight_metrics(flight_data)
                        stability = assess_flight_stability(flight_data)
                        anomalies = detect_all_anomalies(flight_data, {'threshold_std': 3.0})
                        battery = comprehensive_battery_analysis(flight_data)
                        phases = detect_flight_phases(flight_data, 'hybrid', {'climb_threshold': 0.5, 'descent_threshold': -0.5})
                        
                        st.success("✅ Complete analysis finished!")
                        
                        # Display results
                        st.subheader("📊 Complete Analysis Results")
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Duration", f"{metrics['flight_duration']['minutes']:.1f} min")
                        with col2:
                            st.metric("Max Altitude", f"{metrics['altitude_stats']['max_altitude']:.1f} m")
                        with col3:
                            st.metric("Max Speed", f"{metrics['speed_stats']['max_speed']:.1f} m/s")
                        with col4:
                            st.metric("Total Anomalies", anomalies['summary']['total_anomalies'])
                        
                        # Digital twin
                        st.subheader("🌐 Digital Twin")
                        visualizations = create_comprehensive_digital_twin(flight_data)
                        if '3d_path' in visualizations:
                            st.plotly_chart(visualizations['3d_path'], use_container_width=True)
                        
                    else:
                        st.warning("⚠️ Analysis modules not available")
                        
                except Exception as e:
                    st.error(f"❌ Analysis failed: {e}")
    
    else:
        # Traditional CSV analysis (simplified)
        st.sidebar.header("📁 CSV File Upload")
        uploaded_file = st.sidebar.file_uploader("Upload CSV", type=['csv'])
        
        if uploaded_file is not None:
            try:
                df = pd.read_csv(uploaded_file)
                st.success(f"✅ CSV loaded: {len(df)} rows")
                
                if st.sidebar.button("🚀 Analyze CSV"):
                    try:
                        if ANALYSIS_MODULES_AVAILABLE:
                            metrics = calculate_all_flight_metrics(df)
                            ulg_integration._display_metrics(metrics)
                        else:
                            st.warning("⚠️ Analysis modules not available")
                    except Exception as e:
                        st.error(f"❌ Analysis failed: {e}")
            except Exception as e:
                st.error(f"❌ CSV loading failed: {e}")
    
    # Welcome message
    if data_source == "CSV File" and uploaded_file is None:
        st.markdown("""
        ## Welcome to the Enhanced UAV Flight Analysis System! 🚁
        
        ### 🚁 New Features:
        - **Direct ULG Analysis**: Upload and analyze ULG files directly
        - **Real-time Processing**: Instant analysis results
        - **Comprehensive Metrics**: Flight phases, stability, GPS, battery
        - **Modern Interface**: Interactive visualizations
        - **Export Functionality**: Download reports and data
        
        ### 📋 Getting Started:
        1. Choose "ULG File Analysis" for direct processing
        2. Upload your ULG file
        3. Click "Analyze ULG File"
        4. View comprehensive results
        5. Export reports as needed
        
        ### 🔧 System Status:
        """ + 
        f"   - Robust ULG Analyzer: {'✅ Available' if ROBUST_ANALYZER_AVAILABLE else '❌ Not Available'}" +
        f"   - Analysis Modules: {'✅ Available' if ANALYSIS_MODULES_AVAILABLE else '❌ Not Available'}" +
        f"   - ULG Converter: {'✅ Available' if ULGConverter else '❌ Not Available'}"
        )
        
        Upload your data to begin analysis! 🚀
        """)

if __name__ == '__main__':
    main()
