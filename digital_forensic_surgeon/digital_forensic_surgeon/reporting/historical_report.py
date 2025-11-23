"""
Historical Report Generator
Creates detailed reports from browser history analysis
"""

import csv
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

from ..scanners.browser_history_scanner import HistoricalEvent
from ..scanners.tracking_reconstructor import TrackingTimeline


class HistoricalReportGenerator:
    """Generates reports from historical tracking data"""
    
    def __init__(self, timeline: TrackingTimeline, events: List[HistoricalEvent]):
        self.timeline = timeline
        self.events = events
    
    def generate_csv_report(self, output_path: str) -> None:
        """Generate CSV export of all tracking events"""
        
        print(f"\n📄 Generating CSV report...")
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                'Timestamp',
                'Date',
                'Time',
                'Browser',
                'Event Type',
                'Tracker Company',
                'Category',
                'Risk Score',
                'URL',
                'Domain',
                'Page Title',
                'Cookie Name'
            ])
            
            # Process events - showing ALL events with tracker identification
            from ..scanners.data_broker_database import DataBrokerDatabase
            db = DataBrokerDatabase()
            
            for event in sorted(self.events, key=lambda x: x.timestamp, reverse=True):
                classification = db.classify_url(event.url)
                
                if classification['is_tracker']:
                    writer.writerow([
                        event.timestamp.isoformat(),
                        event.timestamp.strftime('%Y-%m-%d'),
                        event.timestamp.strftime('%H:%M:%S'),
                        event.browser,
                        event.event_type,
                        classification['entity_name'],
                        classification['category'],
                        f"{classification['risk_score']:.1f}",
                        event.url,
                        event.domain,
                        event.title or '',
                        event.cookie_name or ''
                    ])
        
        print(f"  ✓ CSV saved to: {output_path}")
    
    def generate_html_report(self, output_path: str) -> None:
        """Generate HTML report with visualizations"""
        
        print(f"\n📊 Generating HTML report...")
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Tracking History Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: #1a1a1a;
            color: #ffffff;
        }}
        .header {{
            background: linear-gradient(135deg, #ff4444, #cc0000);
            padding: 30px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 30px;
        }}
        .header h1 {{
            margin: 0;
            font-size: 36px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: #2a2a2a;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #ff4444;
        }}
        .stat-value {{
            font-size: 48px;
            font-weight: bold;
            color: #ff4444;
        }}
        .stat-label {{
            font-size: 14px;
            color: #aaa;
            margin-top: 5px;
        }}
        .section {{
            background: #2a2a2a;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        .section h2 {{
            color: #ff4444;
            margin-top: 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #444;
        }}
        th {{
            background: #333;
            color: #ff4444;
            font-weight: bold;
        }}
        tr:hover {{
            background: #333;
        }}
        .risk-high {{
            color: #ff4444;
            font-weight: bold;
        }}
        .risk-medium {{
            color: #ffaa00;
        }}
        .risk-low {{
            color: #00ff00;
        }}
        .date-range {{
            color: #aaa;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔥 Tracking History Report</h1>
        <p class="date-range">
            {self.timeline.date_range[0].strftime('%B %d, %Y')} - {self.timeline.date_range[1].strftime('%B %d, %Y')}
        </p>
    </div>
    
    <div class="stats">
        <div class="stat-card">
            <div class="stat-value">{self.timeline.total_events:,}</div>
            <div class="stat-label">Total Browser Events</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{self.timeline.tracking_events + self.timeline.tracking_cookies:,}</div>
            <div class="stat-label">Tracking Events Found</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{self.timeline.unique_trackers}</div>
            <div class="stat-label">Unique Companies Tracking You</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{len(self.timeline.high_risk_events):,}</div>
            <div class="stat-label">High-Risk Events</div>
        </div>
    </div>
    
    <div class="section">
        <h2>📊 Top Trackers</h2>
        <table>
            <tr>
                <th>Rank</th>
                <th>Company</th>
                <th>Events</th>
                <th>Percentage</th>
            </tr>
"""
        
        total_tracking = self.timeline.tracking_events + self.timeline.tracking_cookies
        for idx, (tracker, count) in enumerate(self.timeline.top_trackers[:15], 1):
            percentage = (count / total_tracking * 100) if total_tracking > 0 else 0
            html += f"""
            <tr>
                <td>{idx}</td>
                <td>{tracker}</td>
                <td>{count:,}</td>
                <td>{percentage:.1f}%</td>
            </tr>
"""
        
        html += """
        </table>
    </div>
    
    <div class="section">
        <h2>🎯 Tracking Categories</h2>
        <table>
            <tr>
                <th>Category</th>
                <th>Count</th>
            </tr>
"""
        
        for category, count in sorted(self.timeline.categories.items(), key=lambda x: x[1], reverse=True):
            html += f"""
            <tr>
                <td>{category}</td>
                <td>{count:,}</td>
            </tr>
"""
        
        html += """
        </table>
    </div>
    
    <div class="section">
        <h2>⚠️ High-Risk Tracking Events (Top 50)</h2>
        <table>
            <tr>
                <th>Timestamp</th>
                <th>Company</th>
                <th>Category</th>
                <th>Risk</th>
                <th>URL</th>
            </tr>
"""
        
        for event in self.timeline.high_risk_events[:50]:
            risk_class = "risk-high" if event['risk_score'] >= 9 else "risk-medium"
            html += f"""
            <tr>
                <td>{event['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}</td>
                <td>{event['tracker']}</td>
                <td>{event['category']}</td>
                <td class="{risk_class}">{event['risk_score']:.1f}/10</td>
                <td style="max-width: 400px; overflow: hidden; text-overflow: ellipsis;">{event['url']}</td>
            </tr>
"""
        
        html += """
        </table>
    </div>
    
    <div class="section">
        <h2>📅 Tracking Activity by Date (Last 30 Days)</h2>
        <table>
            <tr>
                <th>Date</th>
                <th>Tracking Events</th>
            </tr>
"""
        
        # Get last 30 days
        sorted_dates = sorted(self.timeline.events_by_date.items(), reverse=True)[:30]
        for date, count in sorted_dates:
            html += f"""
            <tr>
                <td>{date}</td>
                <td>{count:,}</td>
            </tr>
"""
        
        html += """
        </table>
    </div>
    
    <div class="section" style="text-align: center; padding: 40px;">
        <p style="color: #aaa;">
            Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
            Digital Forensic Surgeon - Reality Check System
        </p>
    </div>
</body>
</html>
"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"  ✓ HTML report saved to: {output_path}")
    
    def print_summary(self) -> None:
        """Print summary to console"""
        print("\n" + "="*70)
        print("  📊 TRACKING HISTORY SUMMARY")
        print("="*70)
        print(f"  Date Range: {self.timeline.date_range[0].strftime('%Y-%m-%d')} to {self.timeline.date_range[1].strftime('%Y-%m-%d')}")
        print(f"  Total Events: {self.timeline.total_events:,}")
        print(f"  Tracking Events: {self.timeline.tracking_events + self.timeline.tracking_cookies:,}")
        print(f"  Unique Trackers: {self.timeline.unique_trackers}")
        print(f"  High-Risk Events: {len(self.timeline.high_risk_events):,}")
        print("\n  🎯 Top 10 Trackers:")
        for idx, (tracker, count) in enumerate(self.timeline.top_trackers[:10], 1):
            print(f"     {idx}. {tracker}: {count:,} events")
        print("="*70)
