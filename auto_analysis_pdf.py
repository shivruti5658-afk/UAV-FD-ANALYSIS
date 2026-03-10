#!/usr/bin/env python3
"""
Run analysis and generate PDF report automatically
"""

import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def generate_sample_data():
    """Generate sample flight data for analysis"""
    print("🎯 Generating sample flight data...")
    
    num_points = 2000
    flight_data = pd.DataFrame({
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
    
    print(f"✅ Generated {len(flight_data)} flight data points")
    return flight_data

def run_comprehensive_analysis(flight_data):
    """Run comprehensive analysis on flight data"""
    print("🔍 Running comprehensive analysis...")
    
    analysis_results = {}
    
    try:
        # Import analysis modules
        from flight_metrics import calculate_all_flight_metrics
        from stability_analysis import assess_flight_stability
        from anomaly_detection import detect_all_anomalies
        from battery_analysis import comprehensive_battery_analysis
        from flight_phase_detection import detect_flight_phases
        
        # Run all analysis
        print("   📊 Calculating flight metrics...")
        analysis_results['metrics'] = calculate_all_flight_metrics(flight_data)
        
        print("   ⚖️ Assessing flight stability...")
        analysis_results['stability'] = assess_flight_stability(flight_data)
        
        print("   🔍 Detecting anomalies...")
        analysis_results['anomalies'] = detect_all_anomalies(flight_data, {'threshold_std': 3.0})
        
        print("   🔋 Analyzing battery performance...")
        analysis_results['battery'] = comprehensive_battery_analysis(flight_data)
        
        print("   🚁 Detecting flight phases...")
        config = {
            'climb_threshold': 0.5,
            'descent_threshold': -0.5,
            'stationary_threshold': 2.0,
            'min_phase_duration': 5
        }
        analysis_results['phases'] = detect_flight_phases(flight_data, method='hybrid', config=config)
        
        print("✅ Analysis completed successfully!")
        return analysis_results
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return None
    except Exception as e:
        print(f"❌ Analysis error: {e}")
        return None

def generate_pdf_report(flight_data, analysis_results):
    """Generate comprehensive PDF report"""
    print("📄 Generating PDF report...")
    
    try:
        from pdf_report_generator import PDFReportGenerator
        
        # Create PDF generator
        pdf_generator = PDFReportGenerator()
        
        # Add data points to analysis results
        analysis_results['data_points'] = len(flight_data)
        
        # Generate PDF
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename = f"uav_flight_analysis_report_{timestamp}.pdf"
        
        pdf_path = pdf_generator.generate_comprehensive_report(
            flight_data,
            analysis_results,
            pdf_filename
        )
        
        print(f"✅ PDF report generated: {pdf_filename}")
        print(f"📁 File saved at: {os.path.abspath(pdf_path)}")
        
        return pdf_path
        
    except ImportError as e:
        print(f"❌ PDF generator import error: {e}")
        print("💡 Install PDF packages: pip install reportlab matplotlib seaborn")
        return None
    except Exception as e:
        print(f"❌ PDF generation error: {e}")
        return None

def main():
    """Main function to run analysis and generate PDF"""
    print("🚁 UAV Flight Analysis - Auto Analysis & PDF Generation")
    print("=" * 60)
    
    # Step 1: Generate sample data
    flight_data = generate_sample_data()
    
    # Step 2: Run comprehensive analysis
    analysis_results = run_comprehensive_analysis(flight_data)
    
    if analysis_results is None:
        print("❌ Analysis failed. Please check dependencies.")
        return
    
    # Step 3: Generate PDF report
    pdf_path = generate_pdf_report(flight_data, analysis_results)
    
    if pdf_path:
        print("\n🎉 SUCCESS! Analysis and PDF report completed!")
        print(f"📄 PDF Report: {pdf_path}")
        print("\n📊 Analysis Summary:")
        
        # Show summary
        if 'metrics' in analysis_results:
            metrics = analysis_results['metrics']
            print(f"   • Flight Duration: {metrics['flight_duration']['minutes']:.1f} minutes")
            print(f"   • Max Altitude: {metrics['altitude_stats']['max_altitude']:.1f} m")
            print(f"   • Average Speed: {metrics['speed_stats']['avg_speed']:.1f} m/s")
        
        if 'anomalies' in analysis_results:
            anomalies = analysis_results['anomalies']
            print(f"   • Total Anomalies: {anomalies['summary']['total_anomalies']}")
            print(f"   • Assessment: {anomalies['summary']['overall_assessment']}")
        
        if 'battery' in analysis_results:
            battery = analysis_results['battery']
            print(f"   • Battery Assessment: {battery['overall_assessment']}")
        
        if 'stability' in analysis_results:
            stability = analysis_results['stability']
            print(f"   • Stability Rating: {stability['overall_rating']['rating']}")
        
        if 'phases' in analysis_results:
            phases = analysis_results['phases']
            if 'phases' in phases:
                print(f"   • Flight Phases: {len(phases['phases'])} detected")
        
        print(f"\n🚀 Next Steps:")
        print(f"   1. Open the PDF report: {pdf_path}")
        print(f"   2. Review the comprehensive analysis")
        print(f"   3. Share the report with stakeholders")
        
    else:
        print("❌ PDF generation failed. Please check PDF dependencies.")

if __name__ == "__main__":
    main()
