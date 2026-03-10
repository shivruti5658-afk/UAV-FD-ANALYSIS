#!/usr/bin/env python3
"""
Debug script to check what's in globals
"""

import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def debug_globals():
    """Debug what's available in globals"""
    print("🔍 Debugging Global Variables")
    print("=" * 40)
    
    # Test imports
    try:
        import pandas as pd
        import numpy as np
        import scipy
        import sklearn
        import plotly.graph_objects as go
        import streamlit
        import reportlab
        import matplotlib
        import seaborn
        
        print("✅ All imports successful")
        
        # Check globals
        available_packages = []
        if 'pd' in globals():
            available_packages.append('pd')
        if 'np' in globals():
            available_packages.append('np')
        if 'scipy' in globals():
            available_packages.append('scipy')
        if 'sklearn' in globals():
            available_packages.append('sklearn')
        if 'go' in globals():
            available_packages.append('go')
        if 'streamlit' in globals():
            available_packages.append('streamlit')
        if 'reportlab' in globals():
            available_packages.append('reportlab')
        if 'matplotlib' in globals():
            available_packages.append('matplotlib')
        if 'seaborn' in globals():
            available_packages.append('seaborn')
        
        print(f"📦 Available packages in globals: {available_packages}")
        print(f"📊 Total packages: {len(available_packages)}")
        
        # Check basic functionality
        basic_available = ('pd' in globals() and 'np' in globals() and 'scipy' in globals() and 'sklearn' in globals() and 'go' in globals() and 'streamlit' in globals())
        pdf_available = ('reportlab' in globals() and 'matplotlib' in globals() and 'seaborn' in globals())
        
        print(f"🎯 Basic available: {basic_available}")
        print(f"📄 PDF available: {pdf_available}")
        
        if basic_available and pdf_available:
            print("\n🎉 ALL SYSTEMS GO!")
        elif basic_available:
            print("\n✅ Dashboard ready!")
        else:
            print("\n❌ Some packages missing")
            
    except ImportError as e:
        print(f"❌ Import error: {e}")

if __name__ == "__main__":
    debug_globals()
