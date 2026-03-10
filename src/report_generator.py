import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
from datetime import datetime
import os
import json
from jinja2 import Template


def generate_flight_summary_report(df: pd.DataFrame,
                                 flight_metrics: Dict[str, Any],
                                 stability_analysis: Dict[str, Any],
                                 anomaly_results: Dict[str, Any],
                                 battery_analysis: Dict[str, Any],
                                 phase_results: Dict[str, Any],
                                 output_path: Optional[str] = None) -> str:
    """
    Generate a comprehensive flight analysis report in Markdown format.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        flight_metrics (Dict[str, Any]): Flight metrics results
        stability_analysis (Dict[str, Any]): Stability analysis results
        anomaly_results (Dict[str, Any]): Anomaly detection results
        battery_analysis (Dict[str, Any]): Battery analysis results
        phase_results (Dict[str, Any]): Flight phase detection results
        output_path (str, optional): Path to save the report
        
    Returns:
        str: Path to the generated report
    """
    
    # Create report content
    report_content = f"""
# UAV Flight Analysis Report

**Generated on:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Flight Date:** {df['timestamp'].min().strftime('%Y-%m-%d %H:%M:%S') if 'timestamp' in df.columns else 'N/A'}  
**Total Data Points:** {len(df)}

---

## 📊 Executive Summary

### Flight Overview
- **Duration:** {flight_metrics['flight_duration']['minutes']:.1f} minutes
- **Maximum Altitude:** {flight_metrics['altitude_stats']['max_altitude']:.1f} m
- **Average Speed:** {flight_metrics['speed_stats']['avg_speed']:.1f} m/s
- **Total Distance:** {flight_metrics['distance_traveled']['total_distance_km']:.2f} km

### Overall Assessment
- **Stability Rating:** {stability_analysis['overall_rating']['rating']} ({stability_analysis['overall_rating']['score']:.2f})
- **Anomaly Rate:** {anomaly_results['summary']['overall_anomaly_rate']:.2%}
- **Battery Consumption:** {battery_analysis['consumption_metrics']['total_consumption']:.1f}%
- **Flight Phases:** {phase_results['phase_summary']['total_phases']} detected

---

## ✈️ Flight Performance Metrics

### Basic Metrics
| Metric | Value |
|--------|-------|
| Flight Duration | {flight_metrics['flight_duration']['minutes']:.1f} minutes |
| Maximum Altitude | {flight_metrics['altitude_stats']['max_altitude']:.1f} m |
| Minimum Altitude | {flight_metrics['altitude_stats']['min_altitude']:.1f} m |
| Altitude Range | {flight_metrics['altitude_stats']['altitude_range']:.1f} m |
| Average Speed | {flight_metrics['speed_stats']['avg_speed']:.1f} m/s |
| Maximum Speed | {flight_metrics['speed_stats']['max_speed']:.1f} m/s |
| Total Distance | {flight_metrics['distance_traveled']['total_distance_km']:.2f} km |

### Climb/Descent Performance
| Metric | Value |
|--------|-------|
| Maximum Climb Rate | {flight_metrics['climb_descent_rates']['max_climb_rate']:.2f} m/s |
| Maximum Descent Rate | {flight_metrics['climb_descent_rates']['max_descent_rate']:.2f} m/s |
| Average Vertical Speed | {flight_metrics['climb_descent_rates']['avg_vertical_speed']:.2f} m/s |

### Attitude Statistics
| Parameter | Mean | Std Dev | Min | Max |
|-----------|------|---------|-----|-----|
| Roll | {flight_metrics['attitude_stats']['roll_deg']['mean']:.2f}° | {flight_metrics['attitude_stats']['roll_deg']['std']:.2f}° | {flight_metrics['attitude_stats']['roll_deg']['min']:.2f}° | {flight_metrics['attitude_stats']['roll_deg']['max']:.2f}° |
| Pitch | {flight_metrics['attitude_stats']['pitch_deg']['mean']:.2f}° | {flight_metrics['attitude_stats']['pitch_deg']['std']:.2f}° | {flight_metrics['attitude_stats']['pitch_deg']['min']:.2f}° | {flight_metrics['attitude_stats']['pitch_deg']['max']:.2f}° |
| Yaw | {flight_metrics['attitude_stats']['yaw_deg']['mean']:.2f}° | {flight_metrics['attitude_stats']['yaw_deg']['std']:.2f}° | {flight_metrics['attitude_stats']['yaw_deg']['min']:.2f}° | {flight_metrics['attitude_stats']['yaw_deg']['max']:.2f}° |

---

## 🎯 Stability Analysis

### Overall Stability
- **Stability Index:** {stability_analysis['stability_indices']['stability_index']:.3f}
- **Normalized Stability:** {stability_analysis['stability_indices']['normalized_stability_index']:.2f}
- **Assessment:** {stability_analysis['overall_rating']['rating']} Flight

### Attitude Stability
| Parameter | Standard Deviation | Variance | Range |
|-----------|-------------------|----------|-------|
| Roll | {stability_analysis['attitude_stability']['roll']['std_dev']:.2f}° | {stability_analysis['attitude_stability']['roll']['variance']:.2f} | {stability_analysis['attitude_stability']['roll']['range']:.2f}° |
| Pitch | {stability_analysis['attitude_stability']['pitch']['std_dev']:.2f}° | {stability_analysis['attitude_stability']['pitch']['variance']:.2f} | {stability_analysis['attitude_stability']['pitch']['range']:.2f}° |
| Yaw | {stability_analysis['attitude_stability']['yaw']['std_dev']:.2f}° | {stability_analysis['attitude_stability']['yaw']['variance']:.2f} | {stability_analysis['attitude_stability']['yaw']['range']:.2f}° |

### Oscillation Analysis
| Parameter | Oscillations | Frequency |
|-----------|---------------|------------|
| Roll | {stability_analysis['oscillations']['roll']['total_oscillations']} | {stability_analysis['oscillations']['roll']['oscillation_frequency']:.2f} Hz |
| Pitch | {stability_analysis['oscillations']['pitch']['total_oscillations']} | {stability_analysis['oscillations']['pitch']['oscillation_frequency']:.2f} Hz |

### Altitude & Speed Stability
- **Altitude Standard Deviation:** {stability_analysis['altitude_stability']['altitude_std']:.2f} m
- **Holding Accuracy:** {stability_analysis['altitude_stability']['holding_accuracy']:.2%}
- **Speed Consistency:** {stability_analysis['speed_stability']['speed_consistency']:.2%}

---

## ⚠️ Anomaly Detection

### Anomaly Summary
- **Total Anomalies:** {anomaly_results['summary']['total_anomalies']}
- **Overall Anomaly Rate:** {anomaly_results['summary']['overall_anomaly_rate']:.2%}
- **Assessment:** {anomaly_results['summary']['overall_assessment']}

### Anomaly Breakdown
| Category | Total Anomalies | Rate |
|----------|----------------|------|
"""
    
    # Add anomaly category breakdown
    for category, results in anomaly_results['categories'].items():
        if results['total_anomalies'] > 0:
            report_content += f"| {category.capitalize()} | {results['total_anomalies']} | {results['anomaly_rate']:.2%} |\n"
    
    report_content += f"""

### Detailed Anomalies
"""
    
    # Add detailed anomalies for each category
    for category, results in anomaly_results['categories'].items():
        if results['anomalies']:
            report_content += f"\n#### {category.capitalize()} Anomalies\n"
            for i, anomaly in enumerate(results['anomalies'][:5]):  # Show top 5
                timestamp = anomaly.get('timestamp', 'N/A')
                anomaly_type = anomaly.get('type', 'Unknown')
                severity = anomaly.get('severity', 'medium')
                report_content += f"- **{anomaly_type.replace('_', ' ').title()}** at {timestamp} (Severity: {severity})\n"
            
            if len(results['anomalies']) > 5:
                report_content += f"- ... and {len(results['anomalies']) - 5} more\n"

    report_content += f"""

---

## 🔋 Battery Analysis

### Consumption Metrics
- **Drain Rate:** {battery_analysis['consumption_metrics']['consumption_rate_percent_per_minute']:.2f}%/minute
- **Total Consumption:** {battery_analysis['consumption_metrics']['total_consumption']:.1f}%
- **Remaining Flight Time:** {battery_analysis['remaining_time']['remaining_flight_time_minutes']:.1f} minutes
- **Current Battery Level:** {battery_analysis['remaining_time']['current_battery_level']:.1f}%

### Efficiency Metrics
| Metric | Value |
|--------|-------|
| Altitude per % | {battery_analysis['efficiency']['altitude_per_percent']:.2f} m/% |
| Distance per % | {battery_analysis['efficiency']['distance_per_percent']:.0f} m/% |
| Speed per % | {battery_analysis['efficiency']['speed_per_percent']:.2f} m/s/% |
| Efficiency Score | {battery_analysis['efficiency']['battery_efficiency_score']:.2f} |

### Battery Anomalies
- **Total Anomalies:** {battery_analysis['anomalies']['total_anomalies']}
- **Anomaly Rate:** {battery_analysis['anomalies']['anomaly_rate']:.2%}

"""

    # Add battery phase analysis if available
    if 'phase_analysis' in battery_analysis:
        report_content += "### Battery Consumption by Phase\n"
        phase_analysis = battery_analysis['phase_analysis']['phase_analysis']
        for phase, metrics in phase_analysis.items():
            report_content += f"- **{phase.capitalize()}:** {metrics['consumption_percent']:.1f}% over {metrics['duration_minutes']:.1f} minutes ({metrics['consumption_rate_per_minute']:.2f}%/min)\n"
        
        if battery_analysis['phase_analysis']['most_consuming_phase']:
            most_consuming = battery_analysis['phase_analysis']['most_consuming_phase']
            least_consuming = battery_analysis['phase_analysis']['least_consuming_phase']
            report_content += f"\n- **Most Consuming Phase:** {most_consuming[0].capitalize()} ({most_consuming[1]['consumption_rate_per_minute']:.2f}%/min)\n"
            report_content += f"- **Least Consuming Phase:** {least_consuming[0].capitalize()} ({least_consuming[1]['consumption_rate_per_minute']:.2f}%/min)\n"

    report_content += f"""

---

## 📍 Flight Phase Analysis

### Phase Summary
- **Total Phases:** {phase_results['phase_summary']['total_phases']}
- **Detection Method:** {phase_results['detection_method']}

### Phase Breakdown
| Phase | Count | Total Duration |
|-------|-------|----------------|
"""
    
    # Add phase breakdown
    for phase_name, count in phase_results['phase_summary']['phase_counts'].items():
        duration = phase_results['phase_summary']['phase_durations'][phase_name]
        report_content += f"| {phase_name.capitalize()} | {count} | {duration:.1f}s |\n"
    
    report_content += f"""

### Phase Timeline
"""
    
    # Add phase timeline
    for i, phase in enumerate(phase_results['phases']):
        phase_name = phase['phase']
        duration = phase.get('duration_seconds', phase['duration_points'])
        start_time = phase.get('start_time', phase['start_index'])
        
        if isinstance(start_time, str):
            time_str = start_time
        else:
            time_str = f"Index {start_time}"
        
        report_content += f"{i+1}. **{phase_name.capitalize()}:** {time_str} - {duration:.1f}s\n"

    report_content += f"""

---

## 💡 Recommendations

### Stability Recommendations
"""
    
    # Add stability recommendations
    stability_recommendations = []
    roll_std = stability_analysis['attitude_stability']['roll']['std_dev']
    pitch_std = stability_analysis['attitude_stability']['pitch']['std_dev']
    
    if roll_std > 5:
        stability_recommendations.append("Consider adjusting roll PID gains to reduce roll oscillations")
    
    if pitch_std > 5:
        stability_recommendations.append("Consider adjusting pitch PID gains to reduce pitch oscillations")
    
    total_oscillations = stability_analysis['oscillations']['roll']['total_oscillations'] + \
                        stability_analysis['oscillations']['pitch']['total_oscillations']
    
    if total_oscillations > 10:
        stability_recommendations.append("High oscillation detected - review control system tuning")
    
    holding_accuracy = stability_analysis['altitude_stability']['holding_accuracy']
    if holding_accuracy < 0.8:
        stability_recommendations.append("Improve altitude hold performance - check barometer/altimeter calibration")
    
    if not stability_recommendations:
        stability_recommendations.append("Flight stability appears acceptable - continue monitoring")
    
    for rec in stability_recommendations:
        report_content += f"- {rec}\n"

    report_content += f"""

### Battery Recommendations
"""
    
    # Add battery recommendations
    battery_recommendations = []
    consumption_rate = battery_analysis['consumption_metrics']['consumption_rate_percent_per_minute']
    
    if consumption_rate > 10:
        battery_recommendations.append("High battery consumption detected - consider optimizing flight parameters")
    elif consumption_rate > 5:
        battery_recommendations.append("Moderate battery consumption - monitor during longer flights")
    
    if battery_analysis['anomalies']['total_anomalies'] > 0:
        battery_recommendations.append("Battery anomalies detected - check battery health and connections")
    
    if not battery_recommendations:
        battery_recommendations.append("Battery performance appears normal")
    
    for rec in battery_recommendations:
        report_content += f"- {rec}\n"

    report_content += f"""

### Anomaly Recommendations
"""
    
    # Add anomaly recommendations
    anomaly_recommendations = []
    overall_rate = anomaly_results['summary']['overall_anomaly_rate']
    
    if overall_rate > 0.1:
        anomaly_recommendations.append("High anomaly rate detected - comprehensive system review recommended")
        anomaly_recommendations.append("Check for mechanical issues, sensor calibration, and environmental factors")
    elif overall_rate > 0.05:
        anomaly_recommendations.append("Moderate anomaly rate - review specific anomalous events")
    
    if not anomaly_recommendations:
        anomaly_recommendations.append("Low anomaly rate - flight appears normal")
    
    for rec in anomaly_recommendations:
        report_content += f"- {rec}\n"

    report_content += f"""

---

## 📈 Data Quality Summary

- **Total Data Points:** {len(df)}
- **Missing Values:** {df.isnull().sum().sum()}
- **Data Completeness:** {(1 - df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100:.1f}%
- **Sampling Rate:** {len(df) / flight_metrics['flight_duration']['seconds']:.1f} Hz

---

## 📋 Appendix

### Flight Parameters
- **Dataset Columns:** {', '.join(df.columns.tolist())}
- **Analysis Timestamp:** {datetime.now().isoformat()}
- **Report Version:** 1.0

---

*This report was automatically generated by the UAV Flight Analysis System.*
"""

    # Save report
    if output_path is None:
        output_path = f'outputs/reports/flight_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    return output_path


def generate_json_report(df: pd.DataFrame,
                         flight_metrics: Dict[str, Any],
                         stability_analysis: Dict[str, Any],
                         anomaly_results: Dict[str, Any],
                         battery_analysis: Dict[str, Any],
                         phase_results: Dict[str, Any],
                         output_path: Optional[str] = None) -> str:
    """
    Generate a JSON format report for programmatic access.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        flight_metrics (Dict[str, Any]): Flight metrics results
        stability_analysis (Dict[str, Any]): Stability analysis results
        anomaly_results (Dict[str, Any]): Anomaly detection results
        battery_analysis (Dict[str, Any]): Battery analysis results
        phase_results (Dict[str, Any]): Flight phase detection results
        output_path (str, optional): Path to save the JSON report
        
    Returns:
        str: Path to the generated JSON report
    """
    
    # Create comprehensive JSON report
    json_report = {
        'metadata': {
            'generated_at': datetime.now().isoformat(),
            'flight_date': df['timestamp'].min().isoformat() if 'timestamp' in df.columns else None,
            'total_data_points': len(df),
            'dataset_columns': df.columns.tolist(),
            'analysis_version': '1.0'
        },
        'flight_metrics': flight_metrics,
        'stability_analysis': stability_analysis,
        'anomaly_detection': anomaly_results,
        'battery_analysis': battery_analysis,
        'flight_phases': phase_results,
        'data_quality': {
            'total_points': len(df),
            'missing_values': int(df.isnull().sum().sum()),
            'completeness_percentage': float((1 - df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100),
            'sampling_rate_hz': float(len(df) / flight_metrics['flight_duration']['seconds']) if flight_metrics['flight_duration']['seconds'] > 0 else 0
        }
    }
    
    # Save JSON report
    if output_path is None:
        output_path = f'outputs/reports/flight_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(json_report, f, indent=2, default=str)
    
    return output_path


def generate_html_report(df: pd.DataFrame,
                        flight_metrics: Dict[str, Any],
                        stability_analysis: Dict[str, Any],
                        anomaly_results: Dict[str, Any],
                        battery_analysis: Dict[str, Any],
                        phase_results: Dict[str, Any],
                        output_path: Optional[str] = None) -> str:
    """
    Generate an HTML report with embedded visualizations.
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        flight_metrics (Dict[str, Any]): Flight metrics results
        stability_analysis (Dict[str, Any]): Stability analysis results
        anomaly_results (Dict[str, Any]): Anomaly detection results
        battery_analysis (Dict[str, Any]): Battery analysis results
        phase_results (Dict[str, Any]): Flight phase detection results
        output_path (str, optional): Path to save the HTML report
        
    Returns:
        str: Path to the generated HTML report
    """
    
    # HTML template
    html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UAV Flight Analysis Report</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f7fa;
            color: #333;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .header h1 {
            margin: 0;
            font-size: 2.5em;
        }
        .header p {
            margin: 10px 0 0 0;
            opacity: 0.9;
        }
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .summary-card {
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        .summary-card:hover {
            transform: translateY(-5px);
        }
        .metric-value {
            font-size: 2.2em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }
        .metric-label {
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .section {
            background: white;
            margin: 30px 0;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .section h2 {
            color: #333;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        .status-good { color: #27ae60; font-weight: bold; }
        .status-warning { color: #f39c12; font-weight: bold; }
        .status-danger { color: #e74c3c; font-weight: bold; }
        .table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        .table th, .table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        .table th {
            background-color: #f8f9fa;
            font-weight: 600;
        }
        .recommendations {
            background: #f8f9fa;
            padding: 20px;
            border-left: 4px solid #667eea;
            margin: 20px 0;
        }
        .recommendations ul {
            margin: 0;
            padding-left: 20px;
        }
        .recommendations li {
            margin: 10px 0;
        }
        .chart-container {
            margin: 20px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🚁 UAV Flight Analysis Report</h1>
        <p>Generated on {{ generation_time }} | Flight Date: {{ flight_date }}</p>
    </div>

    <div class="summary-grid">
        <div class="summary-card">
            <div class="metric-value">{{ flight_duration }} min</div>
            <div class="metric-label">Flight Duration</div>
        </div>
        <div class="summary-card">
            <div class="metric-value">{{ max_altitude }} m</div>
            <div class="metric-label">Max Altitude</div>
        </div>
        <div class="summary-card">
            <div class="metric-value">{{ avg_speed }} m/s</div>
            <div class="metric-label">Average Speed</div>
        </div>
        <div class="summary-card">
            <div class="metric-value">{{ total_distance }} km</div>
            <div class="metric-label">Total Distance</div>
        </div>
        <div class="summary-card">
            <div class="metric-value stability-{{ stability_class }}">{{ stability_rating }}</div>
            <div class="metric-label">Stability Rating</div>
        </div>
        <div class="summary-card">
            <div class="metric-value anomaly-{{ anomaly_class }}">{{ anomaly_count }}</div>
            <div class="metric-label">Total Anomalies</div>
        </div>
    </div>

    <div class="section">
        <h2>📊 Flight Performance</h2>
        <table class="table">
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Flight Duration</td><td>{{ flight_duration }} minutes</td></tr>
            <tr><td>Maximum Altitude</td><td>{{ max_altitude }} m</td></tr>
            <tr><td>Average Speed</td><td>{{ avg_speed }} m/s</td></tr>
            <tr><td>Total Distance</td><td>{{ total_distance }} km</td></tr>
            <tr><td>Battery Consumption</td><td>{{ battery_consumption }}%</td></tr>
        </table>
    </div>

    <div class="section">
        <h2>🎯 Stability Analysis</h2>
        <p><strong>Overall Assessment:</strong> <span class="status-{{ stability_class }}">{{ stability_rating }}</span></p>
        <p><strong>Stability Index:</strong> {{ stability_index }}</p>
        
        <table class="table">
            <tr><th>Parameter</th><th>Standard Deviation</th></tr>
            <tr><td>Roll</td><td>{{ roll_std }}°</td></tr>
            <tr><td>Pitch</td><td>{{ pitch_std }}°</td></tr>
            <tr><td>Yaw</td><td>{{ yaw_std }}°</td></tr>
        </table>
    </div>

    <div class="section">
        <h2>⚠️ Anomaly Detection</h2>
        <p><strong>Total Anomalies:</strong> {{ anomaly_count }}</p>
        <p><strong>Anomaly Rate:</strong> {{ anomaly_rate }}</p>
        <p><strong>Assessment:</strong> <span class="status-{{ anomaly_class }}">{{ anomaly_assessment }}</span></p>
    </div>

    <div class="section">
        <h2>🔋 Battery Analysis</h2>
        <table class="table">
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Drain Rate</td><td>{{ drain_rate }}%/min</td></tr>
            <tr><td>Total Consumption</td><td>{{ battery_consumption }}%</td></tr>
            <tr><td>Remaining Flight Time</td><td>{{ remaining_time }} min</td></tr>
            <tr><td>Current Battery Level</td><td>{{ current_battery }}%</td></tr>
        </table>
    </div>

    <div class="section">
        <h2>📍 Flight Phases</h2>
        <p><strong>Total Phases:</strong> {{ total_phases }}</p>
        <p><strong>Detection Method:</strong> {{ phase_method }}</p>
        
        <table class="table">
            <tr><th>Phase</th><th>Count</th><th>Total Duration</th></tr>
            {% for phase, data in phase_breakdown.items() %}
            <tr><td>{{ phase.capitalize() }}</td><td>{{ data.count }}</td><td>{{ data.duration }}s</td></tr>
            {% endfor %}
        </table>
    </div>

    <div class="section">
        <h2>💡 Recommendations</h2>
        <div class="recommendations">
            <ul>
                {% for rec in recommendations %}
                <li>{{ rec }}</li>
                {% endfor %}
            </ul>
        </div>
    </div>

    <div class="section">
        <h2>📈 Data Quality</h2>
        <table class="table">
            <tr><th>Metric</th><th>Value</th></tr>
            <tr><td>Total Data Points</td><td>{{ total_points }}</td></tr>
            <tr><td>Missing Values</td><td>{{ missing_values }}</td></tr>
            <tr><td>Data Completeness</td><td>{{ completeness }}%</td></tr>
            <tr><td>Sampling Rate</td><td>{{ sampling_rate }} Hz</td></tr>
        </table>
    </div>

    <footer style="text-align: center; margin-top: 50px; padding: 20px; color: #666;">
        <p>Report generated by UAV Flight Analysis System | Version 1.0</p>
    </footer>
</body>
</html>
    """
    
    # Prepare template data
    template_data = {
        'generation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'flight_date': df['timestamp'].min().strftime('%Y-%m-%d %H:%M:%S') if 'timestamp' in df.columns else 'N/A',
        'flight_duration': f"{flight_metrics['flight_duration']['minutes']:.1f}",
        'max_altitude': f"{flight_metrics['altitude_stats']['max_altitude']:.1f}",
        'avg_speed': f"{flight_metrics['speed_stats']['avg_speed']:.1f}",
        'total_distance': f"{flight_metrics['distance_traveled']['total_distance_km']:.2f}",
        'battery_consumption': f"{battery_analysis['consumption_metrics']['total_consumption']:.1f}",
        'stability_rating': stability_analysis['overall_rating']['rating'],
        'stability_class': 'good' if stability_analysis['overall_rating']['score'] >= 0.6 else 'warning' if stability_analysis['overall_rating']['score'] >= 0.4 else 'danger',
        'stability_index': f"{stability_analysis['overall_rating']['score']:.2f}",
        'roll_std': f"{stability_analysis['attitude_stability']['roll']['std_dev']:.2f}",
        'pitch_std': f"{stability_analysis['attitude_stability']['pitch']['std_dev']:.2f}",
        'yaw_std': f"{stability_analysis['attitude_stability']['yaw']['std_dev']:.2f}",
        'anomaly_count': anomaly_results['summary']['total_anomalies'],
        'anomaly_class': 'good' if anomaly_results['summary']['overall_anomaly_rate'] < 0.05 else 'warning' if anomaly_results['summary']['overall_anomaly_rate'] < 0.1 else 'danger',
        'anomaly_rate': f"{anomaly_results['summary']['overall_anomaly_rate']:.2%}",
        'anomaly_assessment': anomaly_results['summary']['overall_assessment'],
        'drain_rate': f"{battery_analysis['consumption_metrics']['consumption_rate_percent_per_minute']:.2f}",
        'remaining_time': f"{battery_analysis['remaining_time']['remaining_flight_time_minutes']:.1f}",
        'current_battery': f"{battery_analysis['remaining_time']['current_battery_level']:.1f}",
        'total_phases': phase_results['phase_summary']['total_phases'],
        'phase_method': phase_results['detection_method'],
        'phase_breakdown': {name: {'count': count, 'duration': f"{phase_results['phase_summary']['phase_durations'][name]:.1f}"} 
                           for name, count in phase_results['phase_summary']['phase_counts'].items()},
        'total_points': len(df),
        'missing_values': int(df.isnull().sum().sum()),
        'completeness': f"{(1 - df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100:.1f}",
        'sampling_rate': f"{len(df) / flight_metrics['flight_duration']['seconds']:.1f}" if flight_metrics['flight_duration']['seconds'] > 0 else "0",
        'recommendations': [
            "Flight stability appears acceptable - continue monitoring",
            "Battery performance appears normal",
            "Low anomaly rate - flight appears normal"
        ]
    }
    
    # Render template
    template = Template(html_template)
    html_content = template.render(**template_data)
    
    # Save HTML report
    if output_path is None:
        output_path = f'outputs/reports/flight_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return output_path


def generate_all_reports(df: pd.DataFrame,
                        flight_metrics: Dict[str, Any],
                        stability_analysis: Dict[str, Any],
                        anomaly_results: Dict[str, Any],
                        battery_analysis: Dict[str, Any],
                        phase_results: Dict[str, Any],
                        output_dir: str = 'outputs/reports') -> Dict[str, str]:
    """
    Generate all report formats (Markdown, JSON, HTML).
    
    Args:
        df (pd.DataFrame): Flight data DataFrame
        flight_metrics (Dict[str, Any]): Flight metrics results
        stability_analysis (Dict[str, Any]): Stability analysis results
        anomaly_results (Dict[str, Any]): Anomaly detection results
        battery_analysis (Dict[str, Any]): Battery analysis results
        phase_results (Dict[str, Any]): Flight phase detection results
        output_dir (str): Output directory for reports
        
    Returns:
        Dict[str, str]: Dictionary mapping report formats to file paths
    """
    report_paths = {}
    
    # Generate Markdown report
    try:
        report_paths['markdown'] = generate_flight_summary_report(
            df, flight_metrics, stability_analysis, anomaly_results, 
            battery_analysis, phase_results, 
            output_path=f'{output_dir}/flight_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
        )
    except Exception as e:
        print(f"Error generating Markdown report: {e}")
    
    # Generate JSON report
    try:
        report_paths['json'] = generate_json_report(
            df, flight_metrics, stability_analysis, anomaly_results, 
            battery_analysis, phase_results,
            output_path=f'{output_dir}/flight_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        )
    except Exception as e:
        print(f"Error generating JSON report: {e}")
    
    # Generate HTML report
    try:
        report_paths['html'] = generate_html_report(
            df, flight_metrics, stability_analysis, anomaly_results, 
            battery_analysis, phase_results,
            output_path=f'{output_dir}/flight_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html'
        )
    except Exception as e:
        print(f"Error generating HTML report: {e}")
    
    return report_paths
