#!/usr/bin/env python3
"""
Test script to check all dependencies and modules
"""

import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test all required imports"""
    print("🚁 Testing UAV Flight Analysis Dependencies")
    print("=" * 50)
    
    modules_available = {}
    
    # Test basic Python packages
    try:
        import pandas as pd
        modules_available['pandas'] = True
        print("✅ pandas - Available")
    except ImportError:
        modules_available['pandas'] = False
        print("❌ pandas - Missing")
    
    try:
        import numpy as np
        modules_available['numpy'] = True
        print("✅ numpy - Available")
    except ImportError:
        modules_available['numpy'] = False
        print("❌ numpy - Missing")
    
    try:
        import scipy
        modules_available['scipy'] = True
        print("✅ scipy - Available")
    except ImportError:
        modules_available['scipy'] = False
        print("❌ scipy - Missing")
    
    try:
        import sklearn
        modules_available['sklearn'] = True
        print("✅ scikit-learn - Available")
    except ImportError:
        modules_available['sklearn'] = False
        print("❌ scikit-learn - Missing")
    
    try:
        import plotly.graph_objects as go
        modules_available['plotly'] = True
        print("✅ plotly - Available")
    except ImportError:
        modules_available['plotly'] = False
        print("❌ plotly - Missing")
    
    try:
        import streamlit
        modules_available['streamlit'] = True
        print("✅ streamlit - Available")
    except ImportError:
        modules_available['streamlit'] = False
        print("❌ streamlit - Missing")
    
    # Test PDF packages
    try:
        import reportlab
        modules_available['reportlab'] = True
        print("✅ reportlab - Available")
    except ImportError:
        modules_available['reportlab'] = False
        print("❌ reportlab - Missing (PDF export may not work)")
    
    try:
        import matplotlib
        modules_available['matplotlib'] = True
        print("✅ matplotlib - Available")
    except ImportError:
        modules_available['matplotlib'] = False
        print("❌ matplotlib - Missing (PDF charts may not work)")
    
    try:
        import seaborn
        modules_available['seaborn'] = True
        print("✅ seaborn - Available")
    except ImportError:
        modules_available['seaborn'] = False
        print("❌ seaborn - Missing (PDF charts may not work)")
    
    print("\n📊 Testing Analysis Modules...")
    
    # Test analysis modules
    analysis_modules = [
        'data_loader',
        'preprocessing', 
        'flight_metrics',
        'stability_analysis',
        'anomaly_detection',
        'battery_analysis',
        'flight_phase_detection',
        'digital_twin',
        'visualization',
        'report_generator'
    ]
    
    for module in analysis_modules:
        try:
            __import__(module)
            modules_available[module] = True
            print(f"✅ {module} - Available")
        except ImportError as e:
            modules_available[module] = False
            print(f"❌ {module} - Error: {e}")
    
    # Test PDF generator
    try:
        from pdf_report_generator import PDFReportGenerator
        modules_available['pdf_report_generator'] = True
        print("✅ pdf_report_generator - Available")
    except ImportError as e:
        modules_available['pdf_report_generator'] = False
        print(f"❌ pdf_report_generator - Error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Dependency Test Complete!")
    
    # Check if dashboard should work
    basic_available = (modules_available.get('pandas', False) and 
                      modules_available.get('numpy', False) and 
                      modules_available.get('scipy', False) and 
                      modules_available.get('sklearn', False) and 
                      modules_available.get('plotly', False) and 
                      modules_available.get('streamlit', False))
    
    if basic_available:
        print("✅ Dashboard should work with basic functionality")
    else:
        print("❌ Install missing packages: pip install pandas numpy scipy scikit-learn plotly streamlit")
    
    pdf_available = (modules_available.get('reportlab', False) and 
                    modules_available.get('matplotlib', False) and 
                    modules_available.get('seaborn', False))
    
    if pdf_available:
        print("✅ PDF export should work")
    else:
        print("❌ Install PDF packages: pip install reportlab matplotlib seaborn")
    
    # Overall status
    if basic_available and pdf_available:
        print("\n🎉 ALL SYSTEMS GO! Dashboard and PDF export are ready!")
    elif basic_available:
        print("\n✅ Dashboard ready! PDF export needs reportlab installation.")
    else:
        print("\n❌ Install missing packages for full functionality.")
    
    return modules_available

if __name__ == "__main__":
    test_imports()
