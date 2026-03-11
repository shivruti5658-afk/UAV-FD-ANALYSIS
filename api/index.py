#!/usr/bin/env python3
"""
Vercel Serverless Function for UAV Flight Analysis Dashboard
"""

import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

def handler(request):
    """Main handler for Vercel serverless function"""
    try:
        # Import Streamlit app
        from dashboard.comprehensive_interactive_dashboard import main
        
        # For now, return a simple response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html',
            },
            'body': '''
            <!DOCTYPE html>
            <html>
            <head>
                <title>UAV Flight Analysis Dashboard</title>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                    .container { max-width: 800px; margin: 0 auto; background: white; padding: 40px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
                    h1 { color: #1f77b4; text-align: center; }
                    .status { background: #e8f5e8; padding: 20px; border-radius: 5px; border-left: 4px solid #27ae60; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🚁 UAV Flight Analysis Dashboard</h1>
                    <div class="status">
                        <h3>System Status: Operational</h3>
                        <p>The UAV Flight Analysis System is running successfully on Vercel.</p>
                        <p><strong>Features Available:</strong></p>
                        <ul>
                            <li>Flight Data Analysis</li>
                            <li>Battery Performance Monitoring</li>
                            <li>Stability Assessment</li>
                            <li>Anomaly Detection</li>
                            <li>Professional Report Generation</li>
                        </ul>
                    </div>
                    <p><em>Note: Full Streamlit interface requires additional configuration. This is a temporary landing page.</em></p>
                </div>
            </body>
            </html>
            '''
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
            },
            'body': str(e)
        }

# For Vercel compatibility
def lambda_handler(event, context):
    return handler(event)
