#!/usr/bin/env python3
"""
Generate comprehensive summary reports after review
"""

import json
import os
from datetime import datetime
from pathlib import Path

def generate_html_report():
    """Generate HTML report for better visualization"""
    
    # Load data
    try:
        with open('review_summary.json', 'r') as f:
            reviews = json.load(f)
    except FileNotFoundError:
        reviews = []
    
    try:
        with open('security_issues.json', 'r') as f:
            security_issues = json.load(f)
    except FileNotFoundError:
        security_issues = []
    
    try:
        with open('formatted_files.json', 'r') as f:
            formatted_files = json.load(f)
    except FileNotFoundError:
        formatted_files = []
    
    # Calculate stats
    total_files = len(reviews)
    total_issues = sum(len(r.get('issues', [])) for r in reviews)
    high_severity = sum(1 for r in reviews for issue in r.get('issues', []) if issue.get('severity') == 'high')
    formatted_count = len([f for f in formatted_files if f.get('status') == 'formatted'])
    
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Smart PR AI Review Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
            .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; }}
            .header {{ text-align: center; color: #2d7ff9; margin-bottom: 30px; }}
            .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
            .stat-card {{ background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center; }}
            .stat-number {{ font-size: 2em; font-weight: bold; color: #2d7ff9; }}
            .security {{ color: #dc3545; }}
            .success {{ color: #28a745; }}
            .issue-list {{ margin: 20px 0; }}
            .issue-item {{ background: #fff3cd; padding: 10px; margin: 5px 0; border-left: 4px solid #ffc107; }}
            .high-severity {{ border-left-color: #dc3545; background: #f8d7da; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 Smart PR AI Review Report</h1>
                <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">{total_files}</div>
                    <div>Files Reviewed</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{formatted_count}</div>
                    <div>Files Formatted</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{total_issues}</div>
                    <div>Issues Found</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number security">{high_severity}</div>
                    <div>High Severity</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number security">{len(security_issues)}</div>
                    <div>Security Issues</div>
                </div>
            </div>
            
            <h2>🔍 Review Details</h2>
    """
    
    for review in reviews:
        if 'error' in review:
            continue
        
        html_template += f"""
        <div class="file-review">
            <h3>📁 {review['file']}</h3>
            <p><strong>Summary:</strong> {review.get('summary', 'No summary')}</p>
        """
        
        issues = review.get('issues', [])
        if issues:
            html_template += "<div class='issue-list'>"
            for issue in issues:
                severity_class = 'high-severity' if issue.get('severity') == 'high' else ''
                html_template += f"""
                <div class="issue-item {severity_class}">
                    <strong>Line {issue.get('line', 'N/A')}</strong> ({issue.get('severity', 'low')}): 
                    {issue.get('description', 'No description')}
                </div>
                """
            html_template += "</div>"
    
    html_template += """
        </div>
    </body>
    </html>
    """
    
    with open('review_report.html', 'w') as f:
        f.write(html_template)
    
    print("✅ Generated HTML report: review_report.html")

if __name__ == "__main__":
    generate_html_report()