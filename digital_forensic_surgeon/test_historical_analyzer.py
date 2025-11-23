"""
Test script for Historical Browser Analyzer
Run this to scan your browser history and generate reports!
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from digital_forensic_surgeon.scanners.browser_history_scanner import BrowserHistoryScanner
from digital_forensic_surgeon.scanners.tracking_reconstructor import TrackingReconstructor
from digital_forensic_surgeon.reporting.historical_report import HistoricalReportGenerator


def main():
    print("="*70)
    print("  🔍 HISTORICAL BROWSER ANALYZER")
    print("="*70)
    print()
    print("This will scan your browser databases and find all tracking history!")
    print()
    
    # Step 1: Scan browsers
    scanner = BrowserHistoryScanner()
    events = scanner.scan_all_browsers()
    
    if not events:
        print("\n⚠️ No browser data found!")
        return
    
    # Step 2: Reconstruct tracking
    reconstructor = TrackingReconstructor()
    timeline = reconstructor.reconstruct_timeline(events)
    
    # Step 3: Save to database
    print("\n💾 Saving to database...")
    from digital_forensic_surgeon.database.tracking_schema import TrackingDatabase
    from digital_forensic_surgeon.scanners.data_broker_database import DataBrokerDatabase
    
    db = TrackingDatabase()
    broker_db = DataBrokerDatabase()
    session_id = db.create_session()
    
    saved_count = 0
    # Iterate over RAW events and filter for trackers
    for event in events:
        try:
            # Check if this is a tracker
            classification = broker_db.classify_url(event.url)
            
            if classification['is_tracker']:
                db.log_tracking_event(
                    session_id=session_id,
                    company_name=classification['entity_name'],
                    domain=event.domain,
                    url=event.url,
                    tracking_type=event.event_type,
                    category=classification['category'],
                    risk_score=classification['risk_score'],
                    browser=event.browser
                )
                saved_count += 1
        except Exception as e:
            pass  # Skip duplicates/errors
    
    db.end_session(session_id)
    print(f"  ✓ Saved {saved_count} events to database")
    print(f"  ✓ Database: {db.db_path}")
    
    # Step 4: Generate reports
    output_dir = Path("./tracking_history_reports")
    output_dir.mkdir(exist_ok=True)
    
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    csv_path = output_dir / f"tracking_timeline_{timestamp}.csv"
    html_path = output_dir / f"tracking_report_{timestamp}.html"
    
    generator = HistoricalReportGenerator(timeline, events)
    generator.print_summary()
    generator.generate_csv_report(str(csv_path))
    generator.generate_html_report(str(html_path))
    
    print(f"\n✅ Reports generated successfully!")
    print(f"  📄 CSV: {csv_path}")
    print(f"  🌐 HTML: {html_path}")
    print(f"\n💡 Open the HTML file in your browser to see the full report!")
    print()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Scan cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
