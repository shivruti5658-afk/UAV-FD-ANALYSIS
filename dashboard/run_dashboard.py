#!/usr/bin/env python3
"""
Dashboard launcher script
"""

import subprocess
import sys
import os

def main():
    """Launch the comprehensive dashboard"""
    dashboard_path = os.path.join(os.path.dirname(__file__), 'comprehensive_interactive_dashboard.py')
    
    print("🚁 Launching Comprehensive UAV Flight Analysis Dashboard...")
    print("📊 All analyzer tools integrated")
    print("🎯 Interactive UI with real-time analysis")
    print("🔋 Battery, stability, anomaly, and phase analysis")
    print("🌐 Digital twin visualizations")
    print("---")
    
    try:
        # Launch streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            dashboard_path,
            "--server.port", "8502",
            "--server.headless", "false",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error launching dashboard: {e}")

if __name__ == "__main__":
    main()
