#!/usr/bin/env python3
"""
Test PDF generation directly from dashboard components
"""

import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), 'dashboard'))

def test_dashboard_pdf_generation():
    """Test PDF generation using dashboard components"""
    print("🧪 Testing Dashboard PDF Generation")
    print("=" * 50)
    
    try:
        # Import dashboard components
        from comprehensive_interactive_dashboard import ComprehensiveAnalyzer
        from pdf_report_generator import PDFReportGenerator
        
        print("✅ Dashboard components imported successfully")
        
        # Create analyzer instance
        analyzer = ComprehensiveAnalyzer()
        print("✅ Analyzer instance created")
        
        # Generate sample flight data
        print("🎯 Generating sample flight data...")
        num_points = 2000
        flight_data = pd.DataFrame({
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
        
        analyzer.flight_data = flight_data
        print(f"✅ Generated {len(flight_data)} flight data points")
        
        # Run analysis
        print("🔍 Running comprehensive analysis...")
        analyzer._run_comprehensive_analysis()
        print("✅ Analysis completed")
        
        # Check if analysis results exist
        if analyzer.analysis_results:
            print(f"✅ Analysis results available: {list(analyzer.analysis_results.keys())}")
        else:
            print("❌ No analysis results found")
            return False
        
        # Test PDF generation
        print("📄 Testing PDF generation...")
        if analyzer.pdf_generator:
            print("✅ PDF generator available")
            
            # Add data points to analysis results
            analyzer.analysis_results['data_points'] = len(analyzer.flight_data)
            
            # Generate PDF
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pdf_filename = f"dashboard_test_report_{timestamp}.pdf"
            
            try:
                pdf_path = analyzer.pdf_generator.generate_comprehensive_report(
                    analyzer.flight_data,
                    analyzer.analysis_results,
                    pdf_filename
                )
                
                print(f"✅ PDF generated successfully: {pdf_filename}")
                print(f"📁 File location: {os.path.abspath(pdf_path)}")
                
                # Verify file exists
                if os.path.exists(pdf_path):
                    file_size = os.path.getsize(pdf_path)
                    print(f"📊 File size: {file_size:,} bytes")
                    return True
                else:
                    print("❌ PDF file not found")
                    return False
                    
            except Exception as e:
                print(f"❌ PDF generation error: {e}")
                return False
        else:
            print("❌ PDF generator not available")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def main():
    """Main test function"""
    success = test_dashboard_pdf_generation()
    
    if success:
        print("\n🎉 SUCCESS! Dashboard PDF generation is working!")
        print("\n💡 If PDF generation is not working in the dashboard:")
        print("   1. Make sure analysis has been run first")
        print("   2. Check that flight data is loaded")
        print("   3. Verify all analysis modules are available")
        print("   4. Try running 'Quick Analysis' first, then generate PDF")
    else:
        print("\n❌ Dashboard PDF generation test failed")
        print("💡 Check the error messages above for troubleshooting")

if __name__ == "__main__":
    main()
