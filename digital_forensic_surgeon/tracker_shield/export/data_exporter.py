"""
Data Export System
Export detected trackers in multiple formats
"""

import json
import csv
from pathlib import Path
from datetime import datetime
from typing import List, Dict
import xml.etree.ElementTree as ET

class DataExporter:
    """Export tracking data in various formats"""
    
    def __init__(self, events_file: Path = None):
        if events_file is None:
            events_file = Path.home() / ".trackershield" / "events.jsonl"
        self.events_file = events_file
    
    def load_events(self, event_type: str = None, limit: int = None) -> List[Dict]:
        """
        Load events from file
        
        Args:
            event_type: Filter by event type (e.g., 'tracker_detected')
            limit: Max events to load
        
        Returns:
            List of events
        """
        if not self.events_file.exists():
            return []
        
        events = []
        with open(self.events_file, 'r') as f:
            for line in f:
                try:
                    event = json.loads(line)
                    
                    if event_type and event.get('type') != event_type:
                        continue
                    
                    events.append(event)
                    
                    if limit and len(events) >= limit:
                        break
                except:
                    pass
        
        return events
    
    def export_csv(self, output_path: Path, event_type: str = 'tracker_detected'):
        """
        Export to CSV
        
        Args:
            output_path: Output file path
            event_type: Event type to export
        """
        events = self.load_events(event_type)
        
        if not events:
            print("No events to export")
            return
        
        # Flatten events
        rows = []
        for event in events:
            row = {
                'timestamp': event.get('timestamp'),
                'type': event.get('type'),
            }
            
            # Add data fields
            data = event.get('data', {})
            for key, value in data.items():
                row[f'data_{key}'] = value
            
            rows.append(row)
        
        # Write CSV
        if rows:
            keys = rows[0].keys()
            with open(output_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(rows)
            
            print(f"✅ Exported {len(rows)} events to {output_path}")
    
    def export_json(self, output_path: Path, event_type: str = None, pretty: bool = True):
        """
        Export to JSON
        
        Args:
            output_path: Output file path
            event_type: Event type to export (None = all)
            pretty: Pretty print JSON
        """
        events = self.load_events(event_type)
        
        with open(output_path, 'w') as f:
            if pretty:
                json.dump(events, f, indent=2)
            else:
                json.dump(events, f)
        
        print(f"✅ Exported {len(events)} events to {output_path}")
    
    def export_xml(self, output_path: Path, event_type: str = 'tracker_detected'):
        """
        Export to XML
        
        Args:
            output_path: Output file path
            event_type: Event type to export
        """
        events = self.load_events(event_type)
        
        root = ET.Element('trackershield_export')
        root.set('version', '1.0')
        root.set('exported_at', datetime.now().isoformat())
        root.set('total_events', str(len(events)))
        
        for event in events:
            event_elem = ET.SubElement(root, 'event')
            event_elem.set('type', event.get('type', ''))
            event_elem.set('timestamp', event.get('timestamp', ''))
            
            data_elem = ET.SubElement(event_elem, 'data')
            for key, value in event.get('data', {}).items():
                field = ET.SubElement(data_elem, key)
                field.text = str(value)
        
        tree = ET.ElementTree(root)
        tree.write(output_path, encoding='utf-8', xml_declaration=True)
        
        print(f"✅ Exported {len(events)} events to {output_path}")
    
    def export_html_report(self, output_path: Path):
        """
        Export as HTML report
        
        Args:
            output_path: Output file path
        """
        events = self.load_events('tracker_detected')
        
        # Group by company
        by_company = {}
        for event in events:
            company = event.get('data', {}).get('company', 'Unknown')
            if company not in by_company:
                by_company[company] = []
            by_company[company].append(event)
        
        # Generate HTML
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>TrackerShield Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        h1 {{ color: #ff3b3b; }}
        .stats {{ background: #f5f5f5; padding: 20px; border-radius: 8px; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #f5f5f5; }}
    </style>
</head>
<body>
    <h1>🛡️ TrackerShield Report</h1>
    <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    
    <div class="stats">
        <h2>Summary</h2>
        <p><strong>Total Trackers Detected:</strong> {len(events)}</p>
        <p><strong>Unique Companies:</strong> {len(by_company)}</p>
    </div>
    
    <h2>Detections by Company</h2>
    <table>
        <tr>
            <th>Company</th>
            <th>Detections</th>
        </tr>
"""
        
        for company, company_events in sorted(by_company.items(), key=lambda x: len(x[1]), reverse=True):
            html += f"""        <tr>
            <td>{company}</td>
            <td>{len(company_events)}</td>
        </tr>
"""
        
        html += """    </table>
</body>
</html>"""
        
        with open(output_path, 'w') as f:
            f.write(html)
        
        print(f"✅ Exported HTML report to {output_path}")


# Test
if __name__ == '__main__':
    print("=" * 60)
    print("Data Export System Test")
    print("=" * 60)
    
    exporter = DataExporter()
    
    # Create test output directory
    output_dir = Path('exports')
    output_dir.mkdir(exist_ok=True)
    
    # Export in different formats
    print("\n📤 Exporting data...")
    
    try:
        exporter.export_json(output_dir / 'trackers.json')
        exporter.export_csv(output_dir / 'trackers.csv')
        exporter.export_xml(output_dir / 'trackers.xml')
        exporter.export_html_report(output_dir / 'report.html')
    except Exception as e:
        print(f"⚠️  Export failed (no events yet): {e}")
    
    print("\n" + "=" * 60)
    print("✅ Export system ready!")
    print("=" * 60)
