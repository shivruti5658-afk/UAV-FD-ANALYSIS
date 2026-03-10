#!/usr/bin/env python3
"""
Quick Launch Enhanced Dashboard
Simple launcher for the enhanced UAV Flight Analysis Dashboard
"""

import os
import sys
import subprocess
from pathlib import Path

def main():
    """Main launcher function"""
    print("🚁 UAV FLIGHT ANALYSIS DASHBOARD - ENHANCED")
    print("=" * 60)
    
    # Check if enhanced app exists
    enhanced_app = Path("dashboard/enhanced_app.py")
    
    if enhanced_app.exists():
        print("✅ Enhanced dashboard found!")
        print(f"📁 Location: {enhanced_app.absolute()}")
        
        print("\n🎯 Enhanced Features:")
        print("   • 🚁 Direct ULG file analysis (no CSV conversion needed)")
        print("   • 📊 Comprehensive flight metrics")
        print("   • 🎯 Stability analysis with radar charts")
        print("   • 📍 GPS coverage analysis")
        print("   • 🔋 Battery efficiency metrics")
        print("   • 📋 Raw data export")
        print("   • 🎨 Modern UI with tabs and visualizations")
        print("   • ⚡ Real-time processing")
        
        print("\n📊 ULG Analysis Capabilities:")
        print("   • Multiple analysis methods (direct + CSV conversion)")
        print("   • Robust error handling for problematic ULG files")
        print("   • Flight phase detection")
        print("   • Stability scoring system")
        print("   • GPS coverage visualization")
        print("   • Battery consumption analysis")
        
        print("\n🔗 Data Source Options:")
        print("   • 🚁 ULG File Analysis - Direct processing (recommended)")
        print("   • 📊 CSV File - Traditional analysis pipeline")
        print("   • 🔄 ULG to CSV Conversion - Convert then analyze")
        
        print("\n🚀 Launch Options:")
        print("1. Run Streamlit dashboard (recommended)")
        print("2. View help documentation")
        
        choice = input("\nEnter your choice (1-2): ").strip()
        
        if choice == "1":
            print("\n🌐 Starting enhanced Streamlit dashboard...")
            try:
                # Change to dashboard directory
                os.chdir("dashboard")
                
                # Run Streamlit
                subprocess.run([
                    sys.executable, "-m", "streamlit", "run", 
                    "enhanced_app.py", "--server.port", "8501",
                    "--server.headless", "true"
                ], check=True)
                
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to start Streamlit: {e}")
                print("💡 Make sure Streamlit is installed: pip install streamlit")
                print("🔧 Manual launch:")
                print("   cd dashboard")
                print("   streamlit run enhanced_app.py")
        
        elif choice == "2":
            print("\n📖 Enhanced Dashboard Help:")
            print("\n🎯 How to Use ULG Analysis:")
            print("1. Select 'ULG File Analysis' from data source options")
            print("2. Upload your ULG file using drag & drop")
            print("3. Choose analysis method (Direct Analysis recommended)")
            print("4. Click 'Analyze ULG File' button")
            print("5. View results in organized tabs:")
            print("   • 📈 Flight Performance - Data points, altitude, speed, phases")
            print("   • 🎯 Stability Analysis - Attitude stability, scoring, radar charts")
            print("   • 📍 GPS Analysis - Coverage, distance, flight path")
            print("   • 🔋 Battery Analysis - Usage, efficiency, drain rate")
            print("   • 📋 Raw Data - Exportable analysis data")
            print("6. Export reports and data as needed")
            
            print("\n🔧 Troubleshooting:")
            print("• If direct analysis fails, try CSV conversion")
            print("• Ensure ULG file is not corrupted")
            print("• Check file format compatibility")
            print("• View error messages for specific issues")
            
            print("\n📊 Analysis Sections:")
            print("• Flight Performance - Comprehensive metrics and phase analysis")
            print("• Stability Analysis - Attitude stability with visual scoring")
            print("• GPS Analysis - Coverage maps and flight path visualization")
            print("• Battery Analysis - Consumption patterns and efficiency metrics")
            print("• Raw Data - Complete analysis data export")
        
        else:
            print("❌ Invalid choice. Please try again.")
            
    else:
        print("❌ Enhanced dashboard not found!")
        print("📁 Expected location: dashboard/enhanced_app.py")
    
    print("\n" + "=" * 60)
    print("🚁 ENHANCED UAV FLIGHT ANALYSIS DASHBOARD")
    print("=" * 60)

if __name__ == '__main__':
    main()
