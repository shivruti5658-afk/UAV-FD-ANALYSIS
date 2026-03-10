# 🚁 UAV Flight Analysis System

A comprehensive Python-based system for analyzing UAV flight data with advanced metrics, stability analysis, anomaly detection, and digital twin visualization.

## ✨ Features

### 📊 Core Analysis Modules
- **Flight Metrics**: Duration, altitude, speed, distance calculations
- **Stability Analysis**: Roll/pitch variance, oscillation detection, stability indexing
- **Anomaly Detection**: Multi-parameter anomaly detection with severity assessment
- **Battery Analysis**: Consumption rates, efficiency metrics, remaining flight time
- **Phase Detection**: Automatic identification of takeoff, climb, cruise, descent, landing
- **Digital Twin**: 3D flight path reconstruction and visualization

### 🎨 Visualization & Reporting
- **Interactive Dashboard**: Streamlit-based web interface
- **Comprehensive Plots**: Altitude profiles, GPS tracks, attitude graphs
- **Multi-format Reports**: Markdown, JSON, HTML export options
- **Real-time Digital Twin**: 3D flight path visualization

### 🔧 Data Processing
- **Preprocessing Pipeline**: Missing value handling, noise reduction, outlier removal
- **Data Validation**: Comprehensive dataset structure validation
- **Synthetic Data Generation**: Test data creation for development

## 📁 Project Structure

```
uav-flight-analysis/
│
├── 📂 src/                          # Core analysis modules
│   ├── data_loader.py               # Data loading and validation
│   ├── preprocessing.py             # Data cleaning and preprocessing
│   ├── flight_metrics.py            # Flight performance calculations
│   ├── stability_analysis.py        # Stability assessment
│   ├── anomaly_detection.py         # Anomaly detection algorithms
│   ├── battery_analysis.py          # Battery performance analysis
│   ├── flight_phase_detection.py    # Flight phase identification
│   ├── digital_twin.py              # 3D visualization
│   ├── visualization.py             # Plotting and graphs
│   └── report_generator.py          # Report generation
│
├── 📂 dashboard/                    # Web interface
│   └── app.py                       # Streamlit dashboard
│
├── 📂 utils/                        # Helper utilities
│   └── helpers.py                   # Common functions and tools
│
├── 📂 data/                         # Input data directory
│   └── sample_flight_data.csv       # Sample flight data
│
├── 📂 outputs/                      # Analysis results
│   ├── graphs/                      # Generated plots
│   └── reports/                     # Analysis reports
│
├── 📄 main.py                       # Main CLI application
├── 📄 requirements.txt              # Python dependencies
└── 📄 README.md                     # This file
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the project
cd uav-flight-analysis

# Install dependencies
pip install -r requirements.txt
```

### 2. Generate Sample Data (Optional)

```bash
# Create synthetic flight data for testing
python main.py --generate-sample --output data/sample_flight_data.csv
```

### 3. Run Analysis

#### Command Line Interface
```bash
# Analyze flight data
python main.py --data data/sample_flight_data.csv

# Specify output directory
python main.py --data data/sample_flight_data.csv --output results/

# Skip preprocessing or visualizations
python main.py --data data/sample_flight_data.csv --no-preprocess --no-visualize
```

#### Web Dashboard
```bash
# Launch interactive dashboard
python main.py --dashboard
```

### 4. View Results

Analysis results will be saved to the specified output directory:
- **graphs/**: All generated visualizations
- **reports/**: Analysis reports (Markdown, JSON, HTML)
- **analysis_results.json**: Complete analysis data

## 📊 Data Format

### Required CSV Columns

| Column | Description | Format |
|--------|-------------|--------|
| `timestamp` | Flight timestamp | ISO format or datetime |
| `altitude_m` | Altitude above ground | meters (float) |
| `speed_mps` | Ground speed | m/s (float) |
| `roll_deg` | Roll angle | degrees (float) |
| `pitch_deg` | Pitch angle | degrees (float) |
| `yaw_deg` | Yaw angle | degrees (float) |
| `battery_percent` | Battery level | 0-100 (float) |
| `gps_lat` | GPS latitude | decimal degrees |
| `gps_lon` | GPS longitude | decimal degrees |

### Sample Data Structure

```csv
timestamp,altitude_m,speed_mps,roll_deg,pitch_deg,yaw_deg,battery_percent,gps_lat,gps_lon
2023-06-15 10:00:00,0.0,0.0,0.5,2.1,0.0,100.0,40.7128,-74.0060
2023-06-15 10:00:01,2.1,3.2,1.2,5.4,0.5,99.8,40.7128,-74.0060
...
```

## 🎯 Analysis Modules

### Flight Metrics
- Flight duration and distance
- Altitude and speed statistics
- Climb/descent rates
- Attitude parameter analysis

### Stability Analysis
- Roll/pitch/yaw variance calculation
- Oscillation detection and frequency analysis
- Stability index computation
- Altitude holding accuracy

### Anomaly Detection
- Altitude drops and spikes
- Attitude anomalies (roll/pitch spikes)
- Speed irregularities
- Battery behavior anomalies
- GPS position jumps

### Battery Analysis
- Consumption rate calculation
- Remaining flight time estimation
- Efficiency metrics (altitude/distance per %)
- Phase-based consumption analysis

### Flight Phase Detection
- Hybrid detection method (altitude + speed)
- Support for multiple algorithms:
  - Altitude-based detection
  - Speed-based detection
  - Clustering-based detection
  - Hybrid approach

### Digital Twin
- 3D flight path visualization
- 2D GPS track mapping
- Interactive altitude profiles
- Real-time parameter displays

## 🖥️ Web Dashboard

The Streamlit dashboard provides:

- **Data Upload**: Drag-and-drop CSV file upload
- **Configuration**: Adjustable analysis parameters
- **Real-time Analysis**: Individual module execution
- **Interactive Visualizations**: Plotly-based charts
- **Report Downloads**: One-click report generation

Access at: `http://localhost:8501` (when running)

## 🔧 Configuration

### Default Settings
```python
DEFAULT_CONFIG = {
    'preprocessing': {
        'missing_strategy': 'interpolate',
        'smoothing_method': 'savgol',
        'smoothing_window': 5,
        'outlier_method': 'iqr',
        'outlier_threshold': 1.5
    },
    'anomaly_detection': {
        'threshold_std': 3.0,
        'min_anomaly_severity': 'medium'
    },
    'phase_detection': {
        'climb_threshold': 0.5,
        'descent_threshold': -0.5,
        'stationary_threshold': 2.0,
        'min_phase_duration': 5
    }
}
```

### Custom Configuration
Create a JSON configuration file and use with `--config` parameter:

```bash
python main.py --data flight.csv --config my_config.json
```

## 📈 Command Line Options

```bash
# Basic usage
python main.py --data <file>

# Output options
python main.py --data <file> --output <directory>

# Analysis options
python main.py --data <file> --no-preprocess --no-visualize --no-reports

# Phase detection method
python main.py --data <file> --phase-method hybrid

# Logging level
python main.py --data <file> --log-level DEBUG

# Dashboard
python main.py --dashboard

# Sample data generation
python main.py --generate-sample --output <file>
```

## 🧪 Testing & Development

### Synthetic Data Generation
```python
from utils.helpers import create_synthetic_flight_data

# Generate 10-minute flight data at 10Hz
df = create_synthetic_flight_data(
    duration_seconds=600,
    sampling_rate=10.0,
    max_altitude=150.0,
    cruise_speed=12.0
)
```

### Individual Module Testing
```python
# Test specific modules
from src.flight_metrics import calculate_all_flight_metrics
from src.stability_analysis import assess_flight_stability

# Load data
df = pd.read_csv('flight_data.csv')

# Run individual analyses
metrics = calculate_all_flight_metrics(df)
stability = assess_flight_stability(df)
```

## 📋 System Requirements

- **Python**: 3.8 or higher
- **Memory**: 4GB+ recommended for large datasets
- **Storage**: 100MB+ for outputs (depends on data size)

### Dependencies
See `requirements.txt` for complete list:
- pandas, numpy, scipy
- matplotlib, seaborn, plotly
- scikit-learn
- streamlit
- jinja2

## 🐛 Troubleshooting

### Common Issues

1. **ModuleNotFoundError**: Install dependencies with `pip install -r requirements.txt`
2. **Data validation errors**: Check CSV format and required columns
3. **Memory issues**: Process data in chunks for very large datasets
4. **Visualization errors**: Ensure all required columns are present

### Logging
Enable debug logging for troubleshooting:

```bash
python main.py --data flight.csv --log-level DEBUG
```

## 📚 API Reference

### Core Functions

#### Data Loading
```python
from src.data_loader import load_csv, validate_dataset
df = load_csv('flight_data.csv')
validation = validate_dataset(df)
```

#### Flight Metrics
```python
from src.flight_metrics import calculate_all_flight_metrics
metrics = calculate_all_flight_metrics(df)
```

#### Stability Analysis
```python
from src.stability_analysis import assess_flight_stability
stability = assess_flight_stability(df)
```

#### Anomaly Detection
```python
from src.anomaly_detection import detect_all_anomalies
anomalies = detect_all_anomalies(df)
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Make changes and test thoroughly
4. Submit pull request

## 📄 License

This project is licensed under the MIT License - see the project documentation for details.

## 🙏 Acknowledgments

- Built with Python scientific computing ecosystem
- Visualization powered by Plotly and Matplotlib
- Web interface using Streamlit
- Machine learning utilities from scikit-learn

---

**UAV Flight Analysis System v1.0.0**  
*Professional-grade flight data analysis for UAV operations*
#   U A V - F D - A N A L Y S I S  
 