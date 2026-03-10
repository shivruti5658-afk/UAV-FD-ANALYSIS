#!/usr/bin/env python3
"""
Quick test script to load sample data and test PDF generation in dashboard
"""

import streamlit as st
import pandas as pd
import numpy as np
import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

def main():
    """Main function for quick testing"""
    st.title("🚁 Quick PDF Generation Test")
    
    # Import dashboard components
    try:
        from comprehensive_interactive_dashboard import ComprehensiveAnalyzer
        analyzer = ComprehensiveAnalyzer()
        st.success("✅ Dashboard components loaded successfully")
    except Exception as e:
        st.error(f"❌ Failed to load dashboard: {e}")
        return
    
    # Generate sample data button
    if st.button("🎯 Generate Sample Data", type="primary"):
        with st.spinner("Generating sample flight data..."):
            num_points = 2000
            sample_data = pd.DataFrame({
                'timestamp': pd.date_range(start='2023-01-01', periods=num_points, freq='s'),
                'altitude_m': [max(0, 50 + 100*np.sin(i*0.01) + i*0.05 + np.random.normal(0, 2)) for i in range(num_points)],
                'speed_mps': [15 + 8*np.sin(i*0.02) + np.random.normal(0, 1) for i in range(num_points)],
                'roll_deg': [np.sin(i*0.03) * 8 + np.random.normal(0, 1) for i in range(num_points)],
                'pitch_deg': [np.sin(i*0.025) * 4 + np.random.normal(0, 0.5) for i in range(num_points)],
                'yaw_deg': [(i * 2) % 360 for i in range(num_points)],
                'battery_percent': [max(10, 100 - i*0.04 + np.random.normal(0, 0.5)) for i in range(num_points)],
                'gps_lat': [37.7749 + np.sin(i*0.001) * 0.02 + np.random.normal(0, 0.0001) for i in range(num_points)],
                'gps_lon': [-122.4194 + np.cos(i*0.001) * 0.02 + np.random.normal(0, 0.0001) for i in range(num_points)]
            })
            
            analyzer.flight_data = sample_data
            st.success(f"✅ Generated {len(sample_data)} flight data points")
            st.dataframe(sample_data.head(5))
    
    # Test PDF generation button
    if st.button("📄 Test PDF Generation", type="primary"):
        if analyzer.flight_data is None:
            st.warning("⚠️ Please generate sample data first")
            return
        
        with st.spinner("Testing PDF generation..."):
            try:
                # Run analysis automatically
                analyzer._run_comprehensive_analysis()
                
                if analyzer.analysis_results:
                    st.success(f"✅ Analysis completed with {len(analyzer.analysis_results)} modules")
                    st.write("Analysis results:", list(analyzer.analysis_results.keys()))
                    
                    # Generate PDF
                    analyzer._generate_pdf_report()
                else:
                    st.error("❌ Analysis failed")
                    
            except Exception as e:
                st.error(f"❌ Test failed: {e}")
    
    # Show current status
    st.subheader("📊 Current Status")
    
    col1, col2 = st.columns(2)
    with col1:
        if analyzer.flight_data is not None:
            st.metric("Data Points", len(analyzer.flight_data))
            st.metric("Columns", len(analyzer.flight_data.columns))
        else:
            st.metric("Data Points", "N/A")
            st.metric("Columns", "N/A")
    
    with col2:
        if analyzer.analysis_results:
            st.metric("Analysis Modules", len(analyzer.analysis_results))
            st.metric("PDF Generator", "✅ Available" if analyzer.pdf_generator else "❌ Missing")
        else:
            st.metric("Analysis Modules", "N/A")
            st.metric("PDF Generator", "✅ Available" if analyzer.pdf_generator else "❌ Missing")
    
    # Instructions
    st.subheader("📋 Instructions")
    st.write("""
    1. Click **"Generate Sample Data"** to create test flight data
    2. Click **"Test PDF Generation"** to run analysis and generate PDF
    3. Download the generated PDF report
    4. Check the analysis results in the dashboard
    
    This test verifies that the PDF generation works correctly with the dashboard components.
    """)

if __name__ == "__main__":
    main()
