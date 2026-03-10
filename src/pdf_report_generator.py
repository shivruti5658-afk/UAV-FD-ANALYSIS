#!/usr/bin/env python3
"""
PDF Report Generator for UAV Flight Analysis
Comprehensive PDF reports with graphs, analysis data, and explanations
"""

import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, Any, List, Optional
import io
import base64
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.backends.backend_pdf import PdfPages
import seaborn as sns
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import plotly.graph_objects as go
import plotly.io as pio
import tempfile
import os

# Set matplotlib style
plt.style.use('default')
sns.set_palette("husl")


class PDFReportGenerator:
    """Generate comprehensive PDF reports for UAV flight analysis"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
    def _setup_custom_styles(self):
        """Setup custom styles for the PDF report"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.darkblue,
            alignment=TA_CENTER,
            borderWidth=0,
            borderColor=colors.darkblue
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=20,
            textColor=colors.darkgreen,
            alignment=TA_LEFT,
            borderWidth=0
        ))
        
        # Normal text with justification
        self.styles.add(ParagraphStyle(
            name='CustomNormal',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            alignment=TA_JUSTIFY,
            textColor=colors.black
        ))
        
        # Metric style
        self.styles.add(ParagraphStyle(
            name='MetricStyle',
            parent=self.styles['Normal'],
            fontSize=12,
            spaceAfter=8,
            alignment=TA_LEFT,
            textColor=colors.darkblue,
            fontName='Helvetica-Bold'
        ))
    
    def generate_comprehensive_report(self, 
                                    flight_data: pd.DataFrame,
                                    analysis_results: Dict[str, Any],
                                    output_path: str = None) -> str:
        """
        Generate comprehensive PDF report with all analysis data and visualizations
        
        Args:
            flight_data: Original flight data
            analysis_results: All analysis results from the dashboard
            output_path: Optional output path for the PDF
            
        Returns:
            str: Path to the generated PDF file
        """
        # Generate filename if not provided
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"uav_flight_analysis_report_{timestamp}.pdf"
        
        # Create PDF document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Build story (content)
        story = []
        
        # Title page
        story.extend(self._create_title_page(analysis_results))
        story.append(PageBreak())
        
        # Executive summary
        story.extend(self._create_executive_summary(flight_data, analysis_results))
        story.append(Spacer(1, 20))
        
        # Data overview
        story.extend(self._create_data_overview(flight_data))
        story.append(Spacer(1, 20))
        
        # Flight metrics analysis
        if 'metrics' in analysis_results:
            story.extend(self._create_flight_metrics_section(analysis_results['metrics']))
            story.append(Spacer(1, 20))
        
        # Anomaly detection analysis
        if 'anomalies' in analysis_results:
            story.extend(self._create_anomaly_analysis_section(analysis_results['anomalies']))
            story.append(Spacer(1, 20))
        
        # Battery analysis
        if 'battery' in analysis_results:
            story.extend(self._create_battery_analysis_section(analysis_results['battery']))
            story.append(Spacer(1, 20))
        
        # Stability analysis
        if 'stability' in analysis_results:
            story.extend(self._create_stability_analysis_section(analysis_results['stability']))
            story.append(Spacer(1, 20))
        
        # Flight phase analysis
        if 'phases' in analysis_results:
            story.extend(self._create_flight_phases_section(analysis_results['phases']))
            story.append(Spacer(1, 20))
        
        # Visualizations
        story.extend(self._create_visualizations_section(flight_data, analysis_results))
        
        # Conclusions and recommendations
        story.extend(self._create_conclusions_section(analysis_results))
        
        # Build PDF
        doc.build(story)
        
        return output_path
    
    def _create_title_page(self, analysis_results: Dict[str, Any]) -> List:
        """Create title page with report information"""
        content = []
        
        # Main title
        content.append(Paragraph("UAV Flight Analysis Report", self.styles['CustomTitle']))
        content.append(Spacer(1, 30))
        
        # Subtitle
        content.append(Paragraph("Comprehensive Flight Data Analysis and Performance Evaluation", 
                               self.styles['CustomSubtitle']))
        content.append(Spacer(1, 40))
        
        # Report information
        report_info = [
            f"<b>Generated on:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            f"<b>Analysis Type:</b> Comprehensive Flight Performance Analysis",
            f"<b>Data Points Analyzed:</b> {analysis_results.get('data_points', 'N/A'):,}",
            f"<b>Analysis Modules:</b> Flight Metrics, Anomaly Detection, Battery Analysis, Stability Assessment, Flight Phase Detection"
        ]
        
        for info in report_info:
            content.append(Paragraph(info, self.styles['CustomNormal']))
            content.append(Spacer(1, 12))
        
        # Disclaimer
        content.append(Spacer(1, 30))
        content.append(Paragraph(
            "<i>This report contains comprehensive analysis of UAV flight data including performance metrics, anomaly detection, battery consumption patterns, flight stability assessment, and phase-based analysis. All visualizations and metrics are generated automatically from the provided flight data.</i>",
            self.styles['CustomNormal']
        ))
        
        return content
    
    def _create_executive_summary(self, flight_data: pd.DataFrame, analysis_results: Dict[str, Any]) -> List:
        """Create executive summary section"""
        content = []
        
        content.append(Paragraph("Executive Summary", self.styles['CustomSubtitle']))
        content.append(Spacer(1, 12))
        
        # Generate summary based on available analysis results
        summary_text = self._generate_executive_summary_text(flight_data, analysis_results)
        content.append(Paragraph(summary_text, self.styles['CustomNormal']))
        content.append(Spacer(1, 20))
        
        # Key metrics table
        if 'metrics' in analysis_results:
            metrics = analysis_results['metrics']
            key_metrics_data = [
                ['Metric', 'Value', 'Assessment'],
                ['Flight Duration', f"{metrics.get('flight_duration', {}).get('minutes', 0):.1f} minutes", self._get_duration_assessment(metrics)],
                ['Maximum Altitude', f"{metrics.get('altitude_stats', {}).get('max_altitude', 0):.1f} m", self._get_altitude_assessment(metrics)],
                ['Average Speed', f"{metrics.get('speed_stats', {}).get('avg_speed', 0):.1f} m/s", self._get_speed_assessment(metrics)],
                ['Total Anomalies', f"{analysis_results.get('anomalies', {}).get('summary', {}).get('total_anomalies', 0)}", self._get_anomaly_assessment(analysis_results)]
            ]
            
            table = Table(key_metrics_data, colWidths=[2*inch, 2*inch, 2*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            content.append(table)
        
        return content
    
    def _create_data_overview(self, flight_data: pd.DataFrame) -> List:
        """Create data overview section"""
        content = []
        
        content.append(Paragraph("Data Overview", self.styles['CustomSubtitle']))
        content.append(Spacer(1, 12))
        
        # Dataset information
        overview_text = f"""
        The analysis was performed on a dataset containing {len(flight_data):,} data points 
        with {len(flight_data.columns)} different parameters. The data includes essential flight 
        parameters such as altitude, speed, attitude angles, battery level, and GPS coordinates. 
        This comprehensive dataset allows for detailed analysis of flight performance, anomaly detection, 
        and flight quality assessment.
        """
        
        content.append(Paragraph(overview_text, self.styles['CustomNormal']))
        content.append(Spacer(1, 20))
        
        # Data statistics table
        stats_data = [['Parameter', 'Count', 'Data Type', 'Missing Values']]
        
        for col in flight_data.columns:
            count = flight_data[col].count()
            dtype = str(flight_data[col].dtype)
            missing = flight_data[col].isnull().sum()
            stats_data.append([col, f"{count:,}", dtype, f"{missing}"])
        
        table = Table(stats_data, colWidths=[2*inch, 1*inch, 1.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8)
        ]))
        
        content.append(table)
        
        return content
    
    def _create_flight_metrics_section(self, metrics: Dict[str, Any]) -> List:
        """Create flight metrics analysis section"""
        content = []
        
        content.append(Paragraph("Flight Performance Metrics", self.styles['CustomSubtitle']))
        content.append(Spacer(1, 12))
        
        # Overall performance assessment
        duration = metrics.get('flight_duration', {})
        max_alt = metrics.get('altitude_stats', {})
        speed = metrics.get('speed_stats', {})
        distance = metrics.get('distance_traveled', {})
        
        # Performance grade calculation
        duration_score = min(100, (duration.get('minutes', 0) / 30) * 100)
        altitude_score = min(100, (max_alt.get('max_altitude', 0) / 200) * 100)
        speed_score = min(100, (speed.get('avg_speed', 0) / 20) * 100)
        overall_score = (duration_score + altitude_score + speed_score) / 3
        
        performance_grade = "Excellent" if overall_score > 80 else "Good" if overall_score > 60 else "Fair" if overall_score > 40 else "Poor"
        
        content.append(Paragraph(f"<b>Overall Performance Grade: {performance_grade} ({overall_score:.1f}/100)</b>", self.styles['MetricStyle']))
        content.append(Spacer(1, 8))
        
        # Detailed flight duration analysis
        content.append(Paragraph("<b>Flight Duration Analysis</b>", self.styles['MetricStyle']))
        duration_text = f"""
        The total flight duration was {duration.get('minutes', 0):.1f} minutes ({duration.get('hours', 0):.2f} hours), 
        covering {duration.get('data_points', 0):,} data points at a sampling rate of approximately {duration.get('data_points', 0)/duration.get('minutes', 1):.1f} Hz.
        """
        
        if duration.get('minutes', 0) < 5:
            duration_text += """
            This duration indicates a short-duration mission typical of quick surveillance, 
            system testing, or precision inspection operations.
            """
        elif duration.get('minutes', 0) < 15:
            duration_text += """
            This represents a medium-duration mission suitable for area monitoring, 
            infrastructure inspection, or moderate-range survey operations.
            """
        elif duration.get('minutes', 0) < 30:
            duration_text += """
            This extended duration supports comprehensive mapping, long-range surveillance, 
            or detailed survey missions with extensive data collection requirements.
            """
        else:
            duration_text += """
            This long-duration mission demonstrates excellent endurance capabilities 
            suitable for large-scale survey operations, extended monitoring, or 
            complex multi-objective missions.
            """
        
        content.append(Paragraph(duration_text, self.styles['CustomNormal']))
        content.append(Spacer(1, 12))
        
        # Comprehensive altitude analysis
        content.append(Paragraph("<b>Altitude Performance Analysis</b>", self.styles['MetricStyle']))
        altitude_text = f"""
        The aircraft reached a maximum altitude of {max_alt.get('max_altitude', 0):.1f} meters and maintained 
        an average altitude of {max_alt.get('avg_altitude', 0):.1f} meters throughout the flight. 
        The altitude range of {max_alt.get('altitude_range', 0):.1f} meters demonstrates the aircraft's 
        vertical operational capabilities.
        """
        
        # Altitude profile classification
        if max_alt.get('max_altitude', 0) < 50:
            altitude_profile = "low-altitude operations typical of close-range inspection or urban surveillance"
        elif max_alt.get('max_altitude', 0) < 150:
            altitude_profile = "medium-altitude operations suitable for general surveillance and mapping"
        elif max_alt.get('max_altitude', 0) < 300:
            altitude_profile = "high-altitude operations for extended range and improved obstacle clearance"
        else:
            altitude_profile = "very high-altitude operations demonstrating exceptional performance capabilities"
        
        altitude_text += f"""
        The altitude profile indicates {altitude_profile}. 
        The altitude stability (standard deviation of {max_alt.get('std_dev', 0):.2f} meters) 
        shows {'excellent' if max_alt.get('std_dev', 0) < 10 else 'good' if max_alt.get('std_dev', 0) < 25 else 'moderate'} altitude control precision.
        """
        
        content.append(Paragraph(altitude_text, self.styles['CustomNormal']))
        content.append(Spacer(1, 12))
        
        # Detailed speed analysis
        content.append(Paragraph("<b>Speed Performance Analysis</b>", self.styles['MetricStyle']))
        speed_text = f"""
        The aircraft maintained an average speed of {speed.get('avg_speed', 0):.1f} m/s with a maximum 
        speed of {speed.get('max_speed', 0):.1f} m/s and minimum speed of {speed.get('min_speed', 0):.1f} m/s. 
        The speed standard deviation of {speed.get('speed_std', 0):.2f} m/s indicates {'very consistent' if speed.get('speed_std', 0) < 2 else 'stable' if speed.get('speed_std', 0) < 5 else 'variable'} speed control.
        """
        
        # Speed efficiency analysis
        if speed.get('avg_speed', 0) > 15:
            speed_text += """
            The high average speed indicates efficient mission execution with excellent 
            coverage capabilities and optimal time utilization.
            """
        elif speed.get('avg_speed', 0) > 8:
            speed_text += """
            The moderate average speed provides good balance between mission efficiency 
            and precision operations, suitable for most standard UAV applications.
            """
        else:
            speed_text += """
            The lower average speed suggests precision operations or potential 
            optimization opportunities for improved mission efficiency.
            """
        
        content.append(Paragraph(speed_text, self.styles['CustomNormal']))
        content.append(Spacer(1, 12))
        
        # Distance and coverage analysis
        if distance.get('total_distance_m', 0) > 0:
            content.append(Paragraph("<b>Distance and Coverage Analysis</b>", self.styles['MetricStyle']))
            distance_text = f"""
            The total ground distance covered was {distance.get('total_distance_m', 0):.1f} meters 
            ({distance.get('total_distance_m', 0)/1000:.2f} km) with an average ground speed 
            of {distance.get('avg_ground_speed_mps', speed.get('avg_speed', 0)):.1f} m/s.
            """
            
            # Coverage efficiency
            coverage_efficiency = distance.get('total_distance_m', 0) / duration.get('minutes', 1)
            if coverage_efficiency > 100:
                distance_text += f"""
                The coverage efficiency of {coverage_efficiency:.1f} meters per minute indicates 
                excellent mission effectiveness and optimal flight path planning.
                """
            elif coverage_efficiency > 50:
                distance_text += f"""
                The coverage efficiency of {coverage_efficiency:.1f} meters per minute shows 
                good operational effectiveness with reasonable flight path utilization.
                """
            else:
                distance_text += f"""
                The coverage efficiency of {coverage_efficiency:.1f} meters per minute suggests 
                potential optimization opportunities for flight path planning.
                """
            
            content.append(Paragraph(distance_text, self.styles['CustomNormal']))
            content.append(Spacer(1, 12))
        
        # Create enhanced charts
        content.extend(self._create_enhanced_metrics_charts(metrics))
        
        return content
    
    def _create_enhanced_metrics_charts(self, metrics: Dict[str, Any]) -> List:
        """Create enhanced charts for flight metrics"""
        content = []
        
        try:
            # Create comprehensive metrics visualization
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
            
            # 1. Performance radar chart
            duration_score = min(100, (metrics.get('flight_duration', {}).get('minutes', 0) / 30) * 100)
            altitude_score = min(100, (metrics.get('altitude_stats', {}).get('max_altitude', 0) / 200) * 100)
            speed_score = min(100, (metrics.get('speed_stats', {}).get('avg_speed', 0) / 20) * 100)
            
            categories = ['Duration', 'Altitude', 'Speed']
            scores = [duration_score, altitude_score, speed_score]
            
            # Create bar chart for performance metrics
            bars = ax1.bar(categories, scores, color=['blue', 'green', 'orange'])
            ax1.set_title('Performance Scores')
            ax1.set_ylabel('Score (0-100)')
            ax1.set_ylim(0, 100)
            
            # Add value labels on bars
            for bar, score in zip(bars, scores):
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                          f'{score:.1f}', ha='center', va='bottom')
            
            # 2. Altitude profile
            altitude_stats = metrics.get('altitude_stats', {})
            altitude_values = [altitude_stats.get('min_altitude', 0), 
                              altitude_stats.get('avg_altitude', 0), 
                              altitude_stats.get('max_altitude', 0)]
            altitude_labels = ['Min', 'Avg', 'Max']
            
            ax2.bar(altitude_labels, altitude_values, color=['lightblue', 'blue', 'darkblue'])
            ax2.set_title('Altitude Statistics (m)')
            ax2.set_ylabel('Altitude (m)')
            
            # 3. Speed distribution
            speed_stats = metrics.get('speed_stats', {})
            speed_values = [speed_stats.get('min_speed', 0), 
                           speed_stats.get('avg_speed', 0), 
                           speed_stats.get('max_speed', 0)]
            speed_labels = ['Min', 'Avg', 'Max']
            
            ax3.bar(speed_labels, speed_values, color=['lightgreen', 'green', 'darkgreen'])
            ax3.set_title('Speed Statistics (m/s)')
            ax3.set_ylabel('Speed (m/s)')
            
            # 4. Flight efficiency
            distance = metrics.get('distance_traveled', {})
            duration = metrics.get('flight_duration', {})
            
            if distance.get('total_distance_m', 0) > 0 and duration.get('minutes', 0) > 0:
                efficiency = distance.get('total_distance_m', 0) / duration.get('minutes', 0)
                
                # Create efficiency gauge
                ax4.bar(['Coverage Efficiency'], [efficiency], color='purple')
                ax4.set_title(f'Coverage Efficiency: {efficiency:.1f} m/min')
                ax4.set_ylabel('Meters per minute')
                ax4.axhline(y=100, color='green', linestyle='--', alpha=0.7, label='Excellent')
                ax4.axhline(y=50, color='orange', linestyle='--', alpha=0.7, label='Good')
                ax4.legend()
            else:
                ax4.text(0.5, 0.5, 'No distance data available', ha='center', va='center', transform=ax4.transAxes)
                ax4.set_title('Coverage Efficiency')
            
            plt.tight_layout()
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                plt.savefig(tmp.name, dpi=150, bbox_inches='tight')
                plt.close()
                
                # Add to PDF
                img = Image(tmp.name, width=7*inch, height=5*inch)
                content.append(img)
                content.append(Spacer(1, 12))
                
                # Clean up
                os.unlink(tmp.name)
                
        except Exception as e:
            content.append(Paragraph(f"Enhanced metrics chart generation error: {e}", self.styles['CustomNormal']))
        
        return content
    
    def _create_anomaly_analysis_section(self, anomalies: Dict[str, Any]) -> List:
        """Create anomaly detection analysis section"""
        content = []
        
        content.append(Paragraph("Anomaly Detection Analysis", self.styles['CustomSubtitle']))
        content.append(Spacer(1, 12))
        
        summary = anomalies.get('summary', {})
        
        # Anomaly summary
        anomaly_text = f"""
        The anomaly detection system identified {summary.get('total_anomalies', 0)} anomalies across 
        {len(anomalies.get('categories', {}))} different categories, representing an overall 
        anomaly rate of {summary.get('overall_anomaly_rate', 0):.2%}. The assessment indicates 
        {summary.get('overall_assessment', 'unknown')} flight quality.
        """
        
        content.append(Paragraph(anomaly_text, self.styles['CustomNormal']))
        content.append(Spacer(1, 20))
        
        # Category breakdown
        if 'categories' in anomalies:
            content.append(Paragraph("<b>Anomaly Categories</b>", self.styles['MetricStyle']))
            
            for category, results in anomalies['categories'].items():
                if results.get('total_anomalies', 0) > 0:
                    category_text = f"""
                    <b>{category.title()} Anomalies:</b> {results.get('total_anomalies', 0)} detected
                    """
                    content.append(Paragraph(category_text, self.styles['CustomNormal']))
                    content.append(Spacer(1, 8))
        
        # Create anomaly visualization
        content.extend(self._create_anomaly_charts(anomalies))
        
        return content
    
    def _create_battery_analysis_section(self, battery: Dict[str, Any]) -> List:
        """Create battery analysis section"""
        content = []
        
        content.append(Paragraph("Battery Performance Analysis", self.styles['CustomSubtitle']))
        content.append(Spacer(1, 12))
        
        # Battery consumption
        consumption = battery.get('consumption_metrics', {})
        consumption_text = f"""
        The battery consumption rate was {consumption.get('consumption_rate_percent_per_minute', 0):.1f}% per minute, 
        with a total consumption of {consumption.get('total_consumption', 0):.1f}% over the flight duration 
        of {consumption.get('flight_duration_minutes', 0):.1f} minutes.
        """
        
        content.append(Paragraph(consumption_text, self.styles['CustomNormal']))
        content.append(Spacer(1, 12))
        
        # Remaining flight time
        remaining = battery.get('remaining_time', {})
        remaining_text = f"""
        At the current consumption rate, the estimated remaining flight time is 
        {remaining.get('remaining_flight_time_minutes', 0):.1f} minutes with a current battery level 
        of {remaining.get('current_battery_level', 0):.1f}%.
        """
        
        content.append(Paragraph(remaining_text, self.styles['CustomNormal']))
        content.append(Spacer(1, 12))
        
        # Efficiency metrics
        efficiency = battery.get('efficiency', {})
        efficiency_text = f"""
        The battery efficiency analysis shows {efficiency.get('battery_efficiency_score', 0):.2f} efficiency score, 
        with altitude efficiency of {efficiency.get('altitude_per_percent', 0):.2f} meters per percent battery 
        and distance efficiency of {efficiency.get('distance_per_percent', 0):.0f} meters per percent battery.
        """
        
        content.append(Paragraph(efficiency_text, self.styles['CustomNormal']))
        content.append(Spacer(1, 12))
        
        # Overall assessment
        content.append(Paragraph(f"<b>Overall Assessment:</b> {battery.get('overall_assessment', 'Unknown')}", 
                               self.styles['MetricStyle']))
        
        # Create battery charts
        content.extend(self._create_battery_charts(battery))
        
        return content
    
    def _create_stability_analysis_section(self, stability: Dict[str, Any]) -> List:
        """Create stability analysis section"""
        content = []
        
        content.append(Paragraph("Flight Stability Analysis", self.styles['CustomSubtitle']))
        content.append(Spacer(1, 12))
        
        # Overall stability
        overall = stability.get('overall_rating', {})
        stability_text = f"""
        The overall flight stability rating is {overall.get('rating', 'Unknown')} with a stability 
        score of {overall.get('score', 0):.2f}/100. This indicates {'excellent' if overall.get('score', 0) > 80 else 'good' if overall.get('score', 0) > 60 else 'fair' if overall.get('score', 0) > 40 else 'poor'} 
        flight stability characteristics.
        """
        
        content.append(Paragraph(stability_text, self.styles['CustomNormal']))
        content.append(Spacer(1, 12))
        
        # Attitude stability
        attitude = stability.get('attitude_stability', {})
        content.append(Paragraph("<b>Attitude Stability</b>", self.styles['MetricStyle']))
        attitude_text = f"""
        Roll stability shows a standard deviation of {attitude.get('roll', {}).get('std_dev', 0):.2f}°, 
        while pitch stability shows {attitude.get('pitch', {}).get('std_dev', 0):.2f}°. 
        These values indicate {'good' if attitude.get('roll', {}).get('std_dev', 0) < 5 and attitude.get('pitch', {}).get('std_dev', 0) < 5 else 'moderate'} 
        attitude control during the flight.
        """
        
        content.append(Paragraph(attitude_text, self.styles['CustomNormal']))
        content.append(Spacer(1, 12))
        
        # Oscillation analysis
        oscillations = stability.get('oscillations', {})
        total_osc = oscillations.get('roll', {}).get('total_oscillations', 0) + oscillations.get('pitch', {}).get('total_oscillations', 0)
        oscillation_text = f"""
        A total of {total_osc} oscillations were detected during the flight, with a frequency of 
        {oscillations.get('roll', {}).get('oscillation_frequency', 0):.2f} Hz. This level of oscillation 
        is {'normal' if total_osc < 10 else 'elevated'} for typical UAV operations.
        """
        
        content.append(Paragraph(oscillation_text, self.styles['CustomNormal']))
        
        # Create stability charts
        content.extend(self._create_stability_charts(stability))
        
        return content
    
    def _create_flight_phases_section(self, phases: Dict[str, Any]) -> List:
        """Create flight phases analysis section"""
        content = []
        
        content.append(Paragraph("Flight Phase Analysis", self.styles['CustomSubtitle']))
        content.append(Spacer(1, 12))
        
        phase_list = phases.get('phases', [])
        
        if not phase_list:
            content.append(Paragraph("No flight phases were detected during this analysis.", self.styles['CustomNormal']))
            return content
        
        phases_text = f"""
        The flight phase detection system identified {len(phase_list)} distinct phases during the flight. 
        Each phase represents a different flight segment with unique characteristics and performance metrics.
        """
        
        content.append(Paragraph(phases_text, self.styles['CustomNormal']))
        content.append(Spacer(1, 20))
        
        # Phase details
        content.append(Paragraph("<b>Phase Breakdown</b>", self.styles['MetricStyle']))
        
        for i, phase_info in enumerate(phase_list):
            phase_name = phase_info.get('phase', f'Phase {i+1}')
            duration = phase_info.get('duration_seconds', 0)
            
            phase_detail = f"""
            <b>{phase_name.title()}:</b> Duration of {duration:.1f} seconds
            """
            content.append(Paragraph(phase_detail, self.styles['CustomNormal']))
            content.append(Spacer(1, 8))
        
        # Create phase charts
        content.extend(self._create_phase_charts(phases))
        
        return content
    
    def _create_visualizations_section(self, flight_data: pd.DataFrame, analysis_results: Dict[str, Any]) -> List:
        """Create visualizations section"""
        content = []
        
        content.append(Paragraph("Flight Visualizations", self.styles['CustomSubtitle']))
        content.append(Spacer(1, 12))
        
        viz_text = """
        The following visualizations provide comprehensive insights into the flight characteristics, 
        including altitude profiles, speed variations, attitude changes, and battery consumption patterns.
        """
        
        content.append(Paragraph(viz_text, self.styles['CustomNormal']))
        content.append(Spacer(1, 20))
        
        # Create main flight visualizations
        content.extend(self._create_main_flight_charts(flight_data))
        
        return content
    
    def _create_conclusions_section(self, analysis_results: Dict[str, Any]) -> List:
        """Create conclusions and recommendations section"""
        content = []
        
        content.append(Paragraph("Conclusions and Recommendations", self.styles['CustomSubtitle']))
        content.append(Spacer(1, 12))
        
        # Generate conclusions based on analysis results
        conclusions = self._generate_conclusions(analysis_results)
        content.append(Paragraph("<b>Flight Performance Conclusions</b>", self.styles['MetricStyle']))
        content.append(Paragraph(conclusions, self.styles['CustomNormal']))
        content.append(Spacer(1, 20))
        
        # Generate recommendations
        recommendations = self._generate_recommendations(analysis_results)
        content.append(Paragraph("<b>Recommendations</b>", self.styles['MetricStyle']))
        content.append(Paragraph(recommendations, self.styles['CustomNormal']))
        content.append(Spacer(1, 20))
        
        # Final note
        final_note = """
        This comprehensive analysis provides valuable insights into the UAV flight performance and 
        can be used for mission planning, pilot training, and system optimization. Regular analysis 
        of flight data is recommended to maintain optimal performance and safety standards.
        """
        
        content.append(Paragraph(final_note, self.styles['CustomNormal']))
        
        return content
    
    def _create_metrics_charts(self, metrics: Dict[str, Any]) -> List:
        """Create charts for flight metrics"""
        content = []
        
        try:
            # Altitude chart
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
            
            # Altitude distribution
            altitude_stats = metrics.get('altitude_stats', {})
            ax1.bar(['Min', 'Avg', 'Max'], 
                   [altitude_stats.get('min_altitude', 0), 
                    altitude_stats.get('avg_altitude', 0), 
                    altitude_stats.get('max_altitude', 0)],
                   color=['lightblue', 'blue', 'darkblue'])
            ax1.set_title('Altitude Statistics (m)')
            ax1.set_ylabel('Altitude (m)')
            
            # Speed statistics
            speed_stats = metrics.get('speed_stats', {})
            ax2.bar(['Min', 'Avg', 'Max'], 
                   [speed_stats.get('min_speed', 0), 
                    speed_stats.get('avg_speed', 0), 
                    speed_stats.get('max_speed', 0)],
                   color=['lightgreen', 'green', 'darkgreen'])
            ax2.set_title('Speed Statistics (m/s)')
            ax2.set_ylabel('Speed (m/s)')
            
            plt.tight_layout()
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                plt.savefig(tmp.name, dpi=150, bbox_inches='tight')
                plt.close()
                
                # Add to PDF
                img = Image(tmp.name, width=6*inch, height=2*inch)
                content.append(img)
                content.append(Spacer(1, 12))
                
                # Clean up
                os.unlink(tmp.name)
                
        except Exception as e:
            content.append(Paragraph(f"Chart generation error: {e}", self.styles['CustomNormal']))
        
        return content
    
    def _create_anomaly_charts(self, anomalies: Dict[str, Any]) -> List:
        """Create charts for anomaly analysis"""
        content = []
        
        try:
            # Anomaly distribution chart
            categories = list(anomalies.get('categories', {}).keys())
            counts = [anomalies['categories'].get(cat, {}).get('total_anomalies', 0) for cat in categories]
            
            if categories and any(counts):
                fig, ax = plt.subplots(figsize=(10, 6))
                bars = ax.bar(categories, counts, color=['red', 'orange', 'yellow', 'green', 'blue'][:len(categories)])
                ax.set_title('Anomaly Distribution by Category')
                ax.set_ylabel('Number of Anomalies')
                ax.set_xlabel('Anomaly Category')
                
                # Add value labels on bars
                for bar, count in zip(bars, counts):
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{int(count)}' if count > 0 else '0',
                           ha='center', va='bottom')
                
                plt.xticks(rotation=45)
                plt.tight_layout()
                
                # Save to temporary file
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                    plt.savefig(tmp.name, dpi=150, bbox_inches='tight')
                    plt.close()
                    
                    # Add to PDF
                    img = Image(tmp.name, width=6*inch, height=3*inch)
                    content.append(img)
                    content.append(Spacer(1, 12))
                    
                    # Clean up
                    os.unlink(tmp.name)
                    
        except Exception as e:
            content.append(Paragraph(f"Anomaly chart generation error: {e}", self.styles['CustomNormal']))
        
        return content
    
    def _create_battery_charts(self, battery: Dict[str, Any]) -> List:
        """Create charts for battery analysis"""
        content = []
        
        try:
            # Battery consumption chart
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
            
            # Consumption metrics
            consumption = battery.get('consumption_metrics', {})
            metrics = ['Consumption Rate', 'Total Used', 'Duration']
            values = [consumption.get('consumption_rate_percent_per_minute', 0),
                     consumption.get('total_consumption', 0),
                     consumption.get('flight_duration_minutes', 0)]
            
            ax1.bar(metrics, values, color=['orange', 'red', 'blue'])
            ax1.set_title('Battery Consumption Metrics')
            ax1.set_ylabel('Value')
            
            # Efficiency metrics
            efficiency = battery.get('efficiency', {})
            eff_metrics = ['Altitude/%', 'Distance/%', 'Efficiency Score']
            eff_values = [efficiency.get('altitude_per_percent', 0),
                         efficiency.get('distance_per_percent', 0),
                         efficiency.get('battery_efficiency_score', 0)*10]  # Scale for visibility
            
            ax2.bar(eff_metrics, eff_values, color=['green', 'lightgreen', 'darkgreen'])
            ax2.set_title('Battery Efficiency Metrics')
            ax2.set_ylabel('Value')
            
            plt.tight_layout()
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                plt.savefig(tmp.name, dpi=150, bbox_inches='tight')
                plt.close()
                
                # Add to PDF
                img = Image(tmp.name, width=6*inch, height=2*inch)
                content.append(img)
                content.append(Spacer(1, 12))
                
                # Clean up
                os.unlink(tmp.name)
                
        except Exception as e:
            content.append(Paragraph(f"Battery chart generation error: {e}", self.styles['CustomNormal']))
        
        return content
    
    def _create_stability_charts(self, stability: Dict[str, Any]) -> List:
        """Create charts for stability analysis"""
        content = []
        
        try:
            # Stability metrics chart
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
            
            # Attitude stability
            attitude = stability.get('attitude_stability', {})
            components = ['Roll', 'Pitch', 'Yaw']
            std_devs = [attitude.get('roll', {}).get('std_dev', 0),
                       attitude.get('pitch', {}).get('std_dev', 0),
                       attitude.get('yaw', {}).get('std_dev', 0)]
            
            ax1.bar(components, std_devs, color=['red', 'green', 'blue'])
            ax1.set_title('Attitude Stability (Standard Deviation)')
            ax1.set_ylabel('Standard Deviation (degrees)')
            
            # Overall stability score
            overall = stability.get('overall_rating', {})
            score = overall.get('score', 0)
            
            # Create gauge-like chart for stability score
            ax2.bar(['Stability Score'], [score], color='darkgreen' if score > 80 else 'orange' if score > 60 else 'red')
            ax2.set_ylim(0, 100)
            ax2.set_title(f'Overall Stability Score: {score:.1f}/100')
            ax2.set_ylabel('Score')
            ax2.axhline(y=80, color='green', linestyle='--', alpha=0.7, label='Excellent')
            ax2.axhline(y=60, color='orange', linestyle='--', alpha=0.7, label='Good')
            ax2.legend()
            
            plt.tight_layout()
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                plt.savefig(tmp.name, dpi=150, bbox_inches='tight')
                plt.close()
                
                # Add to PDF
                img = Image(tmp.name, width=6*inch, height=2*inch)
                content.append(img)
                content.append(Spacer(1, 12))
                
                # Clean up
                os.unlink(tmp.name)
                
        except Exception as e:
            content.append(Paragraph(f"Stability chart generation error: {e}", self.styles['CustomNormal']))
        
        return content
    
    def _create_phase_charts(self, phases: Dict[str, Any]) -> List:
        """Create charts for flight phases"""
        content = []
        
        try:
            phase_list = phases.get('phases', [])
            
            if phase_list:
                # Phase duration chart
                phase_names = []
                durations = []
                
                for i, phase_info in enumerate(phase_list):
                    phase_name = phase_info.get('phase', f'Phase {i+1}')
                    duration = phase_info.get('duration_seconds', 0)
                    
                    phase_names.append(phase_name)
                    durations.append(duration)
                
                fig, ax = plt.subplots(figsize=(10, 6))
                colors = plt.cm.Set3(np.linspace(0, 1, len(phase_names)))
                bars = ax.bar(phase_names, durations, color=colors)
                ax.set_title('Flight Phase Durations')
                ax.set_ylabel('Duration (seconds)')
                ax.set_xlabel('Flight Phase')
                
                # Add value labels on bars
                for bar, duration in zip(bars, durations):
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height,
                           f'{duration:.1f}s',
                           ha='center', va='bottom')
                
                plt.xticks(rotation=45)
                plt.tight_layout()
                
                # Save to temporary file
                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                    plt.savefig(tmp.name, dpi=150, bbox_inches='tight')
                    plt.close()
                    
                    # Add to PDF
                    img = Image(tmp.name, width=6*inch, height=3*inch)
                    content.append(img)
                    content.append(Spacer(1, 12))
                    
                    # Clean up
                    os.unlink(tmp.name)
                    
        except Exception as e:
            content.append(Paragraph(f"Phase chart generation error: {e}", self.styles['CustomNormal']))
        
        return content
    
    def _create_main_flight_charts(self, flight_data: pd.DataFrame) -> List:
        """Create main flight visualizations"""
        content = []
        
        try:
            # Create altitude and speed time series
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 8))
            
            # Altitude over time
            if 'altitude_m' in flight_data.columns:
                ax1.plot(flight_data.index, flight_data['altitude_m'], 'b-', linewidth=1)
                ax1.set_title('Altitude Profile')
                ax1.set_ylabel('Altitude (m)')
                ax1.grid(True, alpha=0.3)
            
            # Speed over time
            if 'speed_mps' in flight_data.columns:
                ax2.plot(flight_data.index, flight_data['speed_mps'], 'g-', linewidth=1)
                ax2.set_title('Speed Profile')
                ax2.set_ylabel('Speed (m/s)')
                ax2.grid(True, alpha=0.3)
            
            # Roll and Pitch
            if 'roll_deg' in flight_data.columns and 'pitch_deg' in flight_data.columns:
                ax3.plot(flight_data.index, flight_data['roll_deg'], 'r-', linewidth=1, label='Roll')
                ax3.plot(flight_data.index, flight_data['pitch_deg'], 'orange', linewidth=1, label='Pitch')
                ax3.set_title('Attitude Angles')
                ax3.set_ylabel('Angle (degrees)')
                ax3.legend()
                ax3.grid(True, alpha=0.3)
            
            # Battery level
            if 'battery_percent' in flight_data.columns:
                ax4.plot(flight_data.index, flight_data['battery_percent'], 'purple', linewidth=1)
                ax4.set_title('Battery Level')
                ax4.set_ylabel('Battery (%)')
                ax4.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                plt.savefig(tmp.name, dpi=150, bbox_inches='tight')
                plt.close()
                
                # Add to PDF
                img = Image(tmp.name, width=7*inch, height=5*inch)
                content.append(img)
                content.append(Spacer(1, 12))
                
                # Clean up
                os.unlink(tmp.name)
                
        except Exception as e:
            content.append(Paragraph(f"Main flight charts generation error: {e}", self.styles['CustomNormal']))
        
        return content
    
    def _generate_executive_summary_text(self, flight_data: pd.DataFrame, analysis_results: Dict[str, Any]) -> str:
        """Generate executive summary text"""
        summary_parts = []
        
        # Overall flight assessment
        if 'metrics' in analysis_results:
            metrics = analysis_results['metrics']
            duration = metrics.get('flight_duration', {}).get('minutes', 0)
            max_alt = metrics.get('altitude_stats', {}).get('max_altitude', 0)
            avg_speed = metrics.get('speed_stats', {}).get('avg_speed', 0)
            distance = metrics.get('distance_traveled', {}).get('total_distance_m', 0)
            
            summary_parts.append(f"""
            The UAV flight analysis reveals a comprehensive {duration:.1f}-minute mission covering a total distance 
            of {distance:.1f} meters. The aircraft successfully reached a maximum altitude of {max_alt:.1f} meters 
            while maintaining an average speed of {avg_speed:.1f} m/s throughout the operation.
            """)
            
            # Flight profile classification
            if duration < 10:
                flight_type = "short-duration surveillance or inspection mission"
            elif duration < 30:
                flight_type = "medium-duration mapping or monitoring operation"
            else:
                flight_type = "long-range survey or extended mission"
            
            summary_parts.append(f"""
            Based on the flight characteristics, this appears to be a {flight_type} 
            with {'stable and controlled' if max_alt < 200 else 'high-altitude'} flight parameters.
            """)
        
        # Anomaly assessment
        if 'anomalies' in analysis_results:
            anomalies = analysis_results['anomalies']
            total_anomalies = anomalies.get('summary', {}).get('total_anomalies', 0)
            anomaly_rate = anomalies.get('summary', {}).get('overall_anomaly_rate', 0)
            assessment = anomalies.get('summary', {}).get('overall_assessment', 'unknown')
            
            summary_parts.append(f"""
            Anomaly detection identified {total_anomalies} anomalies throughout the flight, 
            representing an overall anomaly rate of {anomaly_rate:.2%}. The assessment indicates 
            {assessment} flight quality, requiring {'immediate attention and corrective action' if total_anomalies > 50 else 'monitoring and potential optimization'}.
            """)
            
            # Anomaly breakdown insights
            if 'categories' in anomalies:
                high_risk_categories = []
                for category, results in anomalies['categories'].items():
                    if results.get('total_anomalies', 0) > 10:
                        high_risk_categories.append(category)
                
                if high_risk_categories:
                    summary_parts.append(f"""
                    Critical anomaly concentrations were detected in {', '.join(high_risk_categories)} systems, 
                    indicating potential areas requiring immediate maintenance or system calibration.
                    """)
        
        # Battery performance
        if 'battery' in analysis_results:
            battery = analysis_results['battery']
            consumption_rate = battery.get('consumption_metrics', {}).get('consumption_rate_percent_per_minute', 0)
            assessment = battery.get('overall_assessment', 'unknown')
            remaining_time = battery.get('remaining_time', {}).get('remaining_flight_time_minutes', 0)
            
            summary_parts.append(f"""
            Battery performance analysis shows a consumption rate of {consumption_rate:.2f}% per minute 
            with an estimated remaining flight time of {remaining_time:.1f} minutes. The {assessment.lower()} 
            battery performance suggests {'optimal power management' if consumption_rate < 2 else 'potential efficiency improvements'} for future missions.
            """)
            
            # Battery efficiency insights
            if 'efficiency' in battery:
                efficiency = battery['efficiency']
                altitude_eff = efficiency.get('altitude_per_percent', 0)
                distance_eff = efficiency.get('distance_per_percent', 0)
                
                summary_parts.append(f"""
                Battery efficiency metrics indicate {altitude_eff:.2f} meters of altitude gain per percent battery 
                and {distance_eff:.0f} meters of distance covered per percent battery, providing valuable 
                benchmarks for mission planning and optimization.
                """)
        
        # Stability assessment
        if 'stability' in analysis_results:
            stability = analysis_results['stability']
            rating = stability.get('overall_rating', {}).get('rating', 'unknown')
            score = stability.get('overall_rating', {}).get('score', 0)
            
            summary_parts.append(f"""
            Flight stability analysis indicates {rating.lower()} overall performance with a stability 
            score of {score:.1f}/100. This rating suggests {'excellent control system performance' if score > 80 else 'good flight characteristics with room for improvement' if score > 60 else 'need for control system optimization'}.
            """)
            
            # Stability insights
            if 'attitude_stability' in stability:
                attitude = stability['attitude_stability']
                roll_std = attitude.get('roll', {}).get('std_dev', 0)
                pitch_std = attitude.get('pitch', {}).get('std_dev', 0)
                
                if roll_std < 5 and pitch_std < 5:
                    summary_parts.append("""
                    Excellent attitude control was demonstrated with minimal roll and pitch deviations, 
                    indicating precise flight control system calibration and pilot proficiency.
                    """)
        
        # Flight phase insights
        if 'phases' in analysis_results:
            phases = analysis_results['phases']
            phase_list = phases.get('phases', [])
            
            if phase_list:
                summary_parts.append(f"""
                The flight was successfully segmented into {len(phase_list)} distinct phases, 
                providing detailed insights into mission progression and operational efficiency.
                """)
                
                # Phase duration analysis
                total_duration = sum([phase.get('duration_seconds', 0) for phase in phase_list])
                avg_phase_duration = total_duration / len(phase_list) if phase_list else 0
                
                summary_parts.append(f"""
                With an average phase duration of {avg_phase_duration:.1f} seconds, the flight 
                demonstrated {'efficient phase transitions' if avg_phase_duration < 60 else 'extended operational periods'} 
                typical of {'automated flight operations' if avg_phase_duration < 30 else 'complex mission requirements'}.
                """)
        
        # Overall mission assessment
        summary_parts.append(f"""
        Overall, this flight demonstrates {'professional-grade operational capabilities' if duration > 20 and max_alt > 100 else 'solid flight performance with potential for optimization'}. 
        The comprehensive analysis provides actionable insights for improving future mission planning, 
        system maintenance, and operational efficiency.
        """)
        
        return " ".join(summary_parts) if summary_parts else "Flight analysis completed successfully with comprehensive data collection and processing."
    
    def _get_duration_assessment(self, metrics: Dict[str, Any]) -> str:
        """Get duration assessment"""
        duration = metrics.get('flight_duration', {}).get('minutes', 0)
        if duration < 5:
            return "Very Short"
        elif duration < 15:
            return "Short"
        elif duration < 30:
            return "Medium"
        else:
            return "Long"
    
    def _get_altitude_assessment(self, metrics: Dict[str, Any]) -> str:
        """Get altitude assessment"""
        max_alt = metrics.get('altitude_stats', {}).get('max_altitude', 0)
        if max_alt < 50:
            return "Low"
        elif max_alt < 150:
            return "Medium"
        else:
            return "High"
    
    def _get_speed_assessment(self, metrics: Dict[str, Any]) -> str:
        """Get speed assessment"""
        avg_speed = metrics.get('speed_stats', {}).get('avg_speed', 0)
        if avg_speed < 5:
            return "Slow"
        elif avg_speed < 15:
            return "Normal"
        else:
            return "Fast"
    
    def _get_anomaly_assessment(self, analysis_results: Dict[str, Any]) -> str:
        """Get anomaly assessment"""
        total_anomalies = analysis_results.get('anomalies', {}).get('summary', {}).get('total_anomalies', 0)
        if total_anomalies == 0:
            return "Clean"
        elif total_anomalies < 5:
            return "Minor"
        elif total_anomalies < 20:
            return "Moderate"
        else:
            return "Significant"
    
    def _generate_conclusions(self, analysis_results: Dict[str, Any]) -> str:
        """Generate conclusions based on analysis results"""
        conclusions = []
        
        # Flight performance conclusion
        if 'metrics' in analysis_results:
            metrics = analysis_results['metrics']
            duration = metrics.get('flight_duration', {}).get('minutes', 0)
            max_alt = metrics.get('altitude_stats', {}).get('max_altitude', 0)
            avg_speed = metrics.get('speed_stats', {}).get('avg_speed', 0)
            distance = metrics.get('distance_traveled', {}).get('total_distance_m', 0)
            
            if duration > 0:
                performance_grade = "excellent" if duration > 20 and max_alt > 100 else "good" if duration > 10 and max_alt > 50 else "satisfactory"
                conclusions.append(f"""
                The flight demonstrated {performance_grade} mission execution with a duration of {duration:.1f} minutes, 
                covering {distance:.1f} meters at an average speed of {avg_speed:.1f} m/s. 
                The aircraft successfully maintained controlled flight parameters throughout the operation, 
                indicating reliable system performance and operational readiness.
                """)
                
                # Performance efficiency analysis
                if avg_speed > 10 and max_alt > 50:
                    conclusions.append("""
                    The combination of speed and altitude performance suggests optimal flight efficiency 
                    with effective power management and aerodynamic performance characteristics.
                    """)
                elif avg_speed < 5:
                    conclusions.append("""
                    The lower average speed indicates either precision flight operations or potential 
                    optimization opportunities for mission efficiency and time management.
                    """)
        
        # Anomaly conclusion
        if 'anomalies' in analysis_results:
            anomalies = analysis_results['anomalies']
            total_anomalies = anomalies.get('summary', {}).get('total_anomalies', 0)
            assessment = anomalies.get('summary', {}).get('overall_assessment', 'unknown')
            anomaly_rate = anomalies.get('summary', {}).get('overall_anomaly_rate', 0)
            
            if total_anomalies == 0:
                conclusions.append("""
                No significant anomalies were detected throughout the flight, indicating excellent system 
                performance, proper calibration, and optimal operational conditions. This level of flight 
                quality demonstrates professional-grade equipment and operational procedures.
                """)
            elif total_anomalies < 10:
                conclusions.append(f"""
                Minimal anomalies detected ({total_anomalies}) suggest high-quality flight operations 
                with well-maintained systems and effective operational protocols. The {assessment.lower()} 
                assessment indicates continued system reliability with opportunities for minor optimizations.
                """)
            elif total_anomalies < 50:
                conclusions.append(f"""
                Moderate anomaly levels ({total_anomalies}, {anomaly_rate:.1%} rate) indicate {assessment.lower()} 
                flight quality with several areas requiring attention. System performance is acceptable 
                but would benefit from preventive maintenance and calibration improvements.
                """)
            else:
                conclusions.append(f"""
                High anomaly count ({total_anomalies}) with {anomaly_rate:.1%} anomaly rate indicates 
                {assessment.lower()} flight quality requiring immediate attention. Multiple systems 
                show performance issues that could impact mission safety and effectiveness.
                """)
        
        # Battery conclusion
        if 'battery' in analysis_results:
            battery = analysis_results['battery']
            assessment = battery.get('overall_assessment', 'unknown')
            consumption_rate = battery.get('consumption_metrics', {}).get('consumption_rate_percent_per_minute', 0)
            remaining_time = battery.get('remaining_time', {}).get('remaining_flight_time_minutes', 0)
            
            if consumption_rate < 2:
                conclusions.append(f"""
                Battery performance was {assessment.lower()} with an excellent consumption rate of 
                {consumption_rate:.2f}% per minute, indicating optimal power management and efficient 
                energy utilization. The estimated remaining flight time of {remaining_time:.1f} minutes 
                provides good operational margins for mission planning.
                """)
            elif consumption_rate < 4:
                conclusions.append(f"""
                Battery performance showed {assessment.lower()} characteristics with a moderate consumption 
                rate of {consumption_rate:.2f}% per minute. While acceptable for current operations, 
                there are opportunities for power optimization to extend flight endurance and mission range.
                """)
            else:
                conclusions.append(f"""
                Battery consumption rate of {consumption_rate:.2f}% per minute indicates {assessment.lower()} 
                efficiency requiring immediate attention. The high consumption rate limits operational 
                endurance and may indicate system inefficiencies or battery degradation.
                """)
        
        # Stability conclusion
        if 'stability' in analysis_results:
            stability = analysis_results['stability']
            rating = stability.get('overall_rating', {}).get('rating', 'unknown')
            score = stability.get('overall_rating', {}).get('score', 0)
            
            if score > 80:
                conclusions.append(f"""
                Flight stability analysis revealed {rating.lower()} performance with a stability score 
                of {score:.1f}/100. The exceptional stability characteristics indicate precise control 
                system calibration, minimal environmental interference, and excellent flight dynamics.
                """)
            elif score > 60:
                conclusions.append(f"""
                Overall flight stability was rated as {rating.lower()} with a score of {score:.1f}/100, 
                indicating good flight control characteristics. While generally stable, there are 
                opportunities for fine-tuning control parameters to enhance precision and reduce oscillations.
                """)
            else:
                conclusions.append(f"""
                Flight stability assessment of {rating.lower()} with a score of {score:.1f}/100 suggests 
                the need for control system optimization. The stability issues detected could impact 
                mission precision and require immediate attention to ensure safe and reliable operations.
                """)
        
        # Flight phase conclusion
        if 'phases' in analysis_results:
            phases = analysis_results['phases']
            phase_list = phases.get('phases', [])
            
            if phase_list and len(phase_list) > 0:
                phase_efficiency = "highly efficient" if len(phase_list) > 5 else "well-structured" if len(phase_list) > 2 else "basic"
                conclusions.append(f"""
                Flight phase detection identified {len(phase_list)} distinct operational phases, 
                demonstrating {phase_efficiency} mission execution. The clear phase segmentation 
                indicates proper flight planning and systematic progression through mission objectives.
                """)
        
        # Overall operational assessment
        conclusions.append("""
        The comprehensive flight analysis provides valuable insights into system performance, 
        operational efficiency, and mission effectiveness. The data collected enables evidence-based 
        decision making for maintenance scheduling, operational planning, and system optimization.
        """)
        
        return " ".join(conclusions) if conclusions else "Flight analysis completed successfully with comprehensive data collection and evaluation."
    
    def _generate_recommendations(self, analysis_results: Dict[str, Any]) -> str:
        """Generate recommendations based on analysis results"""
        recommendations = []
        
        # Anomaly-based recommendations
        if 'anomalies' in analysis_results:
            anomalies = analysis_results['anomalies']
            total_anomalies = anomalies.get('summary', {}).get('total_anomalies', 0)
            
            if total_anomalies > 50:
                recommendations.append("""
                **IMMEDIATE ACTIONS REQUIRED:**
                • Schedule comprehensive system inspection and maintenance
                • Review and recalibrate all flight control systems
                • Implement enhanced pre-flight check procedures
                • Consider temporary operational restrictions until issues resolved
                """)
            elif total_anomalies > 20:
                recommendations.append("""
                **SHORT-TERM RECOMMENDATIONS:**
                • Conduct targeted maintenance on high-anomaly systems
                • Review flight control parameters and settings
                • Implement additional monitoring during future flights
                • Schedule preventive maintenance within next 30 days
                """)
            elif total_anomalies > 0:
                recommendations.append("""
                **ROUTINE MAINTENANCE:**
                • Continue regular monitoring of anomaly patterns
                • Schedule routine system checks and calibrations
                • Document anomaly sources for future reference
                • Consider preventive maintenance during next service cycle
                """)
        
        # Battery-based recommendations
        if 'battery' in analysis_results:
            battery = analysis_results['battery']
            consumption_rate = battery.get('consumption_metrics', {}).get('consumption_rate_percent_per_minute', 0)
            remaining_time = battery.get('remaining_time', {}).get('remaining_flight_time_minutes', 0)
            
            if consumption_rate > 4:
                recommendations.append("""
                **BATTERY OPTIMIZATION:**
                • Conduct comprehensive battery health assessment
                • Review power management system settings
                • Consider battery replacement or upgrade
                • Optimize flight profiles to reduce power consumption
                • Implement battery monitoring and alerting systems
                """)
            elif consumption_rate > 2:
                recommendations.append("""
                **POWER EFFICIENCY IMPROVEMENTS:**
                • Review current flight patterns for efficiency opportunities
                • Optimize cruise speeds and altitude profiles
                • Consider aerodynamic improvements
                • Implement power-saving flight modes where appropriate
                """)
            else:
                recommendations.append("""
                **BATTERY MAINTENANCE:**
                • Continue current excellent power management practices
                • Regular battery health monitoring
                • Document efficient flight profiles for future reference
                • Share best practices with operational team
                """)
        
        # Stability-based recommendations
        if 'stability' in analysis_results:
            stability = analysis_results['stability']
            score = stability.get('overall_rating', {}).get('score', 0)
            
            if score < 60:
                recommendations.append("""
                **STABILITY IMPROVEMENTS:**
                • Conduct comprehensive flight control system calibration
                • Review and adjust PID controller parameters
                • Check for mechanical issues affecting stability
                • Implement enhanced stabilization systems
                • Consider pilot training for improved control inputs
                """)
            elif score < 80:
                recommendations.append("""
                **STABILITY OPTIMIZATION:**
                • Fine-tune control parameters for improved precision
                • Review environmental factors affecting flight stability
                • Consider advanced stabilization features
                • Implement regular stability monitoring protocols
                """)
            else:
                recommendations.append("""
                **STABILITY MAINTENANCE:**
                • Maintain current excellent stability performance
                • Document optimal control settings
                • Share stability best practices with team
                • Continue regular system monitoring
                """)
        
        # Performance-based recommendations
        if 'metrics' in analysis_results:
            metrics = analysis_results['metrics']
            avg_speed = metrics.get('speed_stats', {}).get('avg_speed', 0)
            max_alt = metrics.get('altitude_stats', {}).get('max_altitude', 0)
            
            if avg_speed < 5:
                recommendations.append("""
                **PERFORMANCE OPTIMIZATION:**
                • Review mission requirements and speed optimization
                • Consider aerodynamic improvements
                • Evaluate power-to-weight ratio
                • Optimize flight profiles for efficiency
                """)
            
            if max_alt < 50:
                recommendations.append("""
                **OPERATIONAL ENHANCEMENT:**
                • Evaluate altitude requirements for mission types
                • Consider performance improvements for higher altitude operations
                • Review environmental limitations and constraints
                • Plan for varied altitude mission profiles
                """)
        
        # General operational recommendations
        recommendations.extend([
            """
            **CONTINUOUS IMPROVEMENT:**
            • Implement regular flight data analysis routines
            • Establish performance benchmarks and standards
            • Create comprehensive maintenance schedules
            • Develop pilot training programs based on analysis insights
            """,
            """
            **SAFETY AND COMPLIANCE:**
            • Review and update safety procedures based on analysis findings
            • Ensure compliance with regulatory requirements
            • Implement risk mitigation strategies
            • Maintain detailed operational documentation
            """,
            """
            **TECHNOLOGY UPGRADES:**
            • Consider advanced sensor integration for enhanced monitoring
            • Evaluate automated flight control systems
            • Implement real-time anomaly detection and alerting
            • Explore AI-powered flight optimization systems
            """,
            """
            **DATA MANAGEMENT:**
            • Establish comprehensive data collection and storage systems
            • Implement automated analysis and reporting workflows
            • Create historical performance databases
            • Develop predictive maintenance algorithms
            """
        ])
        
        return " ".join(recommendations) if recommendations else "Continue current flight operations with regular monitoring and maintenance schedules."
