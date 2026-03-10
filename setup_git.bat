@echo off
echo 🚁 Setting up Git repository for UAV Flight Analysis
echo.

cd /d "%~dp0"

echo 📦 Initializing Git repository...
git init
if %errorlevel% neq 0 (
    echo ❌ Git initialization failed
    pause
    exit /b 1
)

echo 📝 Adding all files to Git...
git add .
if %errorlevel% neq 0 (
    echo ❌ Failed to add files
    pause
    exit /b 1
)

echo 💾 Creating initial commit...
git commit -m "Initial commit: Comprehensive UAV Flight Analysis Dashboard

Features:
- Complete interactive dashboard with all analyzer tools
- Flight metrics, anomaly detection, battery analysis, stability assessment
- Flight phase detection and digital twin visualization
- PDF report generation with charts and analysis
- Multiple data sources: CSV, ULG files, sample data
- Real-time analysis and interactive visualizations
- Export functionality for reports and processed data"
if %errorlevel% neq 0 (
    echo ❌ Failed to create commit
    pause
    exit /b 1
)

echo 🔗 Adding remote repository...
git remote add origin https://github.com/shivruti5658-afk/UAV-FD-ANALYSIS.git
if %errorlevel% neq 0 (
    echo ⚠️ Remote may already exist, continuing...
)

echo 🚀 Pushing to GitHub...
git branch -M main
git push -u origin main
if %errorlevel% neq 0 (
    echo ❌ Failed to push to GitHub
    echo 💡 Please check your GitHub credentials and repository access
    pause
    exit /b 1
)

echo.
echo ✅ Successfully pushed to GitHub repository!
echo 🌐 Repository: https://github.com/shivruti5658-afk/UAV-FD-ANALYSIS
echo.
pause
