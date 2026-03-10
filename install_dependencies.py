#!/usr/bin/env python3
"""
Installation script for UAV Flight Analysis dependencies
"""

import subprocess
import sys
import os

def install_package(package):
    """Install a single package"""
    try:
        print(f"📦 Installing {package}...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"✅ {package} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package}: {e}")
        return False

def main():
    """Install all required packages"""
    print("🚁 UAV Flight Analysis - Dependency Installer")
    print("=" * 50)
    
    # Required packages for basic functionality
    basic_packages = [
        "pandas>=1.3.0",
        "numpy>=1.20.0", 
        "scipy>=1.7.0",
        "scikit-learn>=1.0.0",
        "plotly>=5.0.0",
        "streamlit>=1.50.0"
    ]
    
    # Packages for PDF export
    pdf_packages = [
        "reportlab>=3.6.0",
        "matplotlib>=3.5.0", 
        "seaborn>=0.11.0"
    ]
    
    # Optional packages for ULG analysis
    optional_packages = [
        "pyulog>=0.8.0"
    ]
    
    print("\n📦 Installing basic packages...")
    basic_success = 0
    for package in basic_packages:
        if install_package(package):
            basic_success += 1
    
    print(f"\n✅ Basic packages: {basic_success}/{len(basic_packages)} installed")
    
    print("\n📄 Installing PDF export packages...")
    pdf_success = 0
    for package in pdf_packages:
        if install_package(package):
            pdf_success += 1
    
    print(f"\n✅ PDF packages: {pdf_success}/{len(pdf_packages)} installed")
    
    print("\n🔧 Installing optional packages...")
    opt_success = 0
    for package in optional_packages:
        if install_package(package):
            opt_success += 1
        else:
            print(f"⚠️ {package} is optional - continuing...")
    
    print(f"\n✅ Optional packages: {opt_success}/{len(optional_packages)} installed")
    
    # Summary
    total_packages = len(basic_packages) + len(pdf_packages) + len(optional_packages)
    total_success = basic_success + pdf_success + opt_success
    
    print("\n" + "=" * 50)
    print(f"📊 Installation Summary: {total_success}/{total_packages} packages installed")
    
    if basic_success == len(basic_packages):
        print("✅ All basic packages installed - Dashboard should work!")
    else:
        print("⚠️ Some basic packages failed - Dashboard may have limited functionality")
    
    if pdf_success == len(pdf_packages):
        print("✅ PDF export packages installed - PDF reports available!")
    else:
        print("⚠️ PDF packages failed - PDF export may not work")
    
    if opt_success == len(optional_packages):
        print("✅ Optional packages installed - Full functionality available!")
    else:
        print("⚠️ Some optional packages failed - Some features may be limited")
    
    print("\n🚀 Next steps:")
    print("1. Restart the dashboard: python run_dashboard.py")
    print("2. Load your flight data and run analysis")
    print("3. Generate PDF reports if needed")

if __name__ == "__main__":
    main()
