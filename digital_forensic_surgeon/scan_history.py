"""
Historical Scanner - Rebuilt with Timestamp Fix
Scans browser history and preserves ORIGINAL timestamps
"""

from digital_forensic_surgeon.scanners.browser_history_scanner import BrowserHistoryScanner
from digital_forensic_surgeon.scanners.tracking_reconstructor import TrackingReconstructor
from digital_forensic_surgeon.database.tracking_schema import TrackingDatabase
from digital_forensic_surgeon.scanners.data_broker_database import DataBrokerDatabase
from pathlib import Path
from datetime import datetime

def scan_and_save():
    """Scan browser history and save with CORRECT timestamps"""
    
    print("=" * 70)
    print("  🔍 HISTORICAL BROWSER SCANNER")
    print("=" * 70)
    print()
    
    # Step 1: Scan browsers
    print("🔍 Scanning browser databases...")
    scanner = BrowserHistoryScanner()
    events = scanner.scan_all_browsers()
    
    if not events:
        print("❌ No browser data found!")
        return
    
    print(f"✅ Found {len(events):,} total events\n")
    
    # Step 2: Reconstruct tracking
    print("📊 Reconstructing tracking timeline...")
    reconstructor = TrackingReconstructor()
    timeline = reconstructor.reconstruct_timeline(events)
    
    # Step 3: Save to database with ORIGINAL timestamps
    print("\n💾 Saving to database with ORIGINAL timestamps...")
    
    db = TrackingDatabase()
    broker_db = DataBrokerDatabase()
    session_id = db.create_session()
    
    saved_count = 0
    skipped_count = 0
    
    for event in events:
        try:
            # Check if this is a tracker
            classification = broker_db.classify_url(event.url)
            
            if classification['is_tracker']:
                # Save with ORIGINAL timestamp from browser
                db.log_tracking_event(
                    session_id=session_id,
                    company_name=classification['entity_name'],
                    domain=event.domain,
                    url=event.url,
                    tracking_type=event.event_type,
                    category=classification['category'],
                    risk_score=classification['risk_score'],
                    browser=event.browser,
                    timestamp=event.timestamp.isoformat()  # ← ORIGINAL timestamp!
                )
                saved_count += 1
            else:
                skipped_count += 1
                
        except Exception as e:
            skipped_count += 1
    
    db.end_session(session_id)
    
    print(f"  ✅ Saved {saved_count:,} tracking events")
    print(f"  ⏭️ Skipped {skipped_count:,} non-tracker events")
    print(f"  💾 Database: {db.db_path}")
    
    # Show date range
    cursor = db.conn.cursor()
    cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM tracking_events")
    min_date, max_date = cursor.fetchone()
    
    if min_date and max_date:
        print(f"\n📅 Date range: {min_date[:10]} to {max_date[:10]}")
    
    print("\n✅ Scan complete!\n")
    print(f"💡 View dashboard: forensic-surgeon --reality-check")
    print()

if __name__ == "__main__":
    scan_and_save()
