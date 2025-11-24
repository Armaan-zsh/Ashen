"""
Tracking Database Schema
SQLite database for storing all tracking events
"""

import sqlite3
from pathlib import Path
from typing import Optional
from datetime import datetime


class TrackingDatabase:
    """Manages the tracking events database"""
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            # Default location in user's AppData
            app_data = Path.home() / "AppData" / "Local" / "DigitalForensicSurgeon"
            app_data.mkdir(parents=True, exist_ok=True)
            db_path = str(app_data / "tracking_history.db")
        
        self.db_path = db_path
        self.conn = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Create database and tables if they don't exist"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = self.conn.cursor()
        
        # Tracking events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tracking_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                session_id INTEGER,
                company_name TEXT NOT NULL,
                domain TEXT NOT NULL,
                url TEXT,
                tracking_type TEXT,
                category TEXT,
                risk_score REAL,
                data_sent TEXT,
                browser TEXT,
                FOREIGN KEY (session_id) REFERENCES sessions(id)
            )
        """)
        
        # Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time TEXT NOT NULL,
                end_time TEXT,
                total_requests INTEGER DEFAULT 0,
                total_trackers INTEGER DEFAULT 0,
                status TEXT DEFAULT 'active'
            )
        """)
        
        # Companies table (aggregated stats)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                name TEXT PRIMARY KEY,
                category TEXT,
                risk_score REAL,
                total_requests INTEGER DEFAULT 0,
                first_seen TEXT,
                last_seen TEXT
            )
        """)
        
        self.conn.commit()
        
        # Add indexes for performance (Week 2 optimization)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_timestamp ON tracking_events(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_company ON tracking_events(company_name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_category ON tracking_events(category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_session ON tracking_events(session_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_date ON tracking_events(DATE(timestamp))")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_companies_name ON companies(name)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_events_domain ON tracking_events(domain)")
        
        self.conn.commit()
    
    def create_session(self) -> int:
        """Create a new monitoring session"""
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO sessions (start_time, status)
            VALUES (?, 'active')
        """, (datetime.now().isoformat(),))
        self.conn.commit()
        return cursor.lastrowid
    
    def log_tracking_event(self, session_id: int, company_name: str, domain: str,
                          url: str, tracking_type: str, category: str, 
                          risk_score: float, data_sent: str = None, browser: str = None,
                          timestamp: str = None):
        """Log a tracking event"""
        cursor = self.conn.cursor()
        
        # Use provided timestamp or current time
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        # Insert event
        cursor.execute("""
            INSERT INTO tracking_events 
            (timestamp, session_id, company_name, domain, url, tracking_type, 
             category, risk_score, data_sent, browser)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (timestamp, session_id, company_name, domain, url, tracking_type,
              category, risk_score, data_sent, browser))
        
        # Update company stats
        cursor.execute("""
            INSERT INTO companies (name, category, risk_score, total_requests, first_seen, last_seen)
            VALUES (?, ?, ?, 1, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                total_requests = total_requests + 1,
                last_seen = excluded.last_seen
        """, (company_name, category, risk_score, timestamp, timestamp))
        
        # Update session stats
        cursor.execute("""
            UPDATE sessions 
            SET total_requests = total_requests + 1,
                total_trackers = total_trackers + 1
            WHERE id = ?
        """, (session_id,))
        
        self.conn.commit()
    
    def end_session(self, session_id: int):
        """End a monitoring session"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE sessions 
            SET end_time = ?, status = 'completed'
            WHERE id = ?
        """, (datetime.now().isoformat(), session_id))
        self.conn.commit()
    
    def query_events_by_date(self, start_date: str, end_date: str = None):
        """Query events by date range"""
        cursor = self.conn.cursor()
        
        if end_date:
            cursor.execute("""
                SELECT timestamp, company_name, domain, url, tracking_type, 
                       category, risk_score, browser
                FROM tracking_events
                WHERE timestamp >= ? AND timestamp <= ?
                ORDER BY timestamp DESC
            """, (start_date, end_date))
        else:
            cursor.execute("""
                SELECT timestamp, company_name, domain, url, tracking_type, 
                       category, risk_score, browser
                FROM tracking_events
                WHERE timestamp LIKE ?
                ORDER BY timestamp DESC
            """, (f"{start_date}%",))
        
        return cursor.fetchall()
    
    def query_events_by_company(self, company_name: str):
        """Query events by company"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT timestamp, domain, url, tracking_type, risk_score
            FROM tracking_events
            WHERE company_name = ?
            ORDER BY timestamp DESC
        """, (company_name,))
        return cursor.fetchall()
    
    def get_company_stats(self):
        """Get statistics for all companies"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT name, category, risk_score, total_requests, first_seen, last_seen
            FROM companies
            ORDER BY total_requests DESC
        """)
        return cursor.fetchall()
    
    def get_recent_events(self, limit: int = 100):
        """Get most recent events"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT timestamp, company_name, domain, tracking_type, risk_score
            FROM tracking_events
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        return cursor.fetchall()
    
    def get_stats_summary(self):
        """Get overall tracking statistics (with caching)"""
        from digital_forensic_surgeon.database.query_cache import query_cache
        
        # Try cache first
        cached = query_cache.get("stats_summary", ())
        if cached:
            return cached
        
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_events,
                COUNT(DISTINCT company_name) as unique_companies,
                COUNT(DISTINCT session_id) as sessions,
                MIN(timestamp) as first_seen,
                MAX(timestamp) as last_seen
            FROM tracking_events
        """)
        
        row = cursor.fetchone()
        
        result = {
            'total_events': row[0] or 0,
            'unique_companies': row[1] or 0,
            'sessions': row[2] or 0,
            'first_seen': row[3],
            'last_seen': row[4]
        }
        
        # Cache for 60 seconds
        query_cache.set("stats_summary", (), result)
        
        return result
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
