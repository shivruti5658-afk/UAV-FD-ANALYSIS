@echo off
echo 🚁 Starting Comprehensive UAV Flight Analysis Dashboard...
echo 📊 All analyzer tools integrated
echo 🎯 Interactive UI with real-time analysis
echo 🔋 Battery, stability, anomaly, and phase analysis
echo 🌐 Digital twin visualizations
echo.

cd /d "%~dp0"

echo 🌐 Launching dashboard on http://localhost:8504
echo 📱 Dashboard will open in your browser
echo.

streamlit run comprehensive_interactive_dashboard.py --server.port 8504 --server.headless false --browser.gatherUsageStats false

pause
