"""
Database Cleanup Utility
Removes corrupted/invalid data
"""

import sqlite3
from pathlib import Path
from datetime import datetime

def clean_future_dates():
    """Remove tracking events with future timestamps"""
    
    db_path = Path.home() / "AppData" / "Local" / "DigitalForensicSurgeon" / "tracking_history.db"
    
    if not db_path.exists():
        print(f"❌ Database not found at: {db_path}")
        return
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Count future events
    cursor.execute("""
        SELECT COUNT(*) FROM tracking_events 
        WHERE timestamp > datetime('now')
    """)
    future_count = cursor.fetchone()[0]
    
    if future_count == 0:
        print("✅ No future dates found!")
        conn.close()
        return
    
    print(f"🔍 Found {future_count} events with future dates")
    
    # Delete them
    cursor.execute("""
        DELETE FROM tracking_events 
        WHERE timestamp > datetime('now')
    """)
    
    conn.commit()
    deleted = cursor.rowcount
    
    print(f"✅ Cleaned {deleted} corrupted events")
    print(f"💾 Database: {db_path}")
    
    # Show new date range
    cursor.execute("""
        SELECT MIN(timestamp), MAX(timestamp) 
        FROM tracking_events
    """)
    min_date, max_date = cursor.fetchone()
    
    if min_date and max_date:
        print(f"📅 New date range: {min_date} to {max_date}")
    
    conn.close()

if __name__ == '__main__':
    clean_future_dates()
