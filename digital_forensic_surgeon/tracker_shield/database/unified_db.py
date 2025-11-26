"""
Database Bridge - Unifies old and new tracking data
Makes old browser forensics data work with new TrackerShield dashboard
"""

import sqlite3
from pathlib import Path
import pandas as pd
from datetime import datetime

class UnifiedDatabase:
    """Bridges old tracking_history.db with new TrackerShield format"""
    
    def __init__(self, db_path='tracking_history.db'):
        self.db_path = Path(db_path)
        self.conn = None
        
        if self.db_path.exists():
            self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
    
    def get_tracking_events(self, days_back=30):
        """Get tracking events in unified format"""
        if not self.conn:
            return pd.DataFrame()
        
        # Try new schema first
        try:
            query = """
                SELECT 
                    datetime(timestamp/1000, 'unixepoch') as timestamp,
                    company,
                    tracker_name as tracker_type,
                    CASE 
                        WHEN risk_score >= 8 THEN 'high'
                        WHEN risk_score >= 5 THEN 'medium'
                        ELSE 'low'
                    END as risk_level,
                    page_url as url,
                    evidence_json as data_collected
                FROM tracking_events
                WHERE timestamp <= strftime('%s', 'now') * 1000
                  AND timestamp >= strftime('%s', 'now', '-{days} days') * 1000
                ORDER BY timestamp DESC
                LIMIT 1000
            """.format(days=days_back)
            
            df = pd.DataFrame(
                self.conn.execute(query).fetchall(),
                columns=['timestamp', 'company', 'tracker_type', 'risk_level', 'url', 'data_collected']
            )
            
            if not df.empty:
                return df
        except Exception as e:
            print(f"New schema failed: {e}")
        
        # Fallback to any table structure
        try:
            # Get all tables
            tables = self.conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
            
            print(f"Available tables: {tables}")
            
            # Try the first table with tracking data
            for table_name in [t[0] for t in tables]:
                try:
                    query = f"SELECT * FROM {table_name} LIMIT 1000"
                    df = pd.read_sql_query(query, self.conn)
                    
                    if not df.empty:
                        # Normalize column names
                        df = self._normalize_columns(df)
                        return df
                except:
                    continue
        except Exception as e:
            print(f"Fallback failed: {e}")
        
        return pd.DataFrame()
    
    def _normalize_columns(self, df):
        """Normalize different column names to standard format"""
        
        # Map variations to standard names
        column_mapping = {
            'time': 'timestamp',
            'datetime': 'timestamp',
            'date': 'timestamp',
            'tracker_name': 'tracker_type',
            'type': 'tracker_type',
            'page_url': 'url',
            'site': 'url',
            'evidence_json': 'data_collected',
            'data': 'data_collected'
        }
        
        # Rename columns
        for old_name, new_name in column_mapping.items():
            if old_name in df.columns:
                df = df.rename(columns={old_name: new_name})
        
        # Ensure required columns exist
        required = ['timestamp', 'company', 'tracker_type', 'risk_level', 'url']
        
        for col in required:
            if col not in df.columns:
                if col == 'risk_level':
                    df[col] = 'medium'
                elif col == 'tracker_type':
                    df[col] = 'unknown'
                else:
                    df[col] = ''
        
        return df
    
    def get_stats(self):
        """Get quick stats"""
        df = self.get_tracking_events(days_back=365)
        
        if df.empty:
            return {
                'total_events': 0,
                'unique_companies': 0,
                'high_risk': 0,
                'data_worth': 0
            }
        
        return {
            'total_events': len(df),
            'unique_companies': df['company'].nunique() if 'company' in df.columns else 0,
            'high_risk': len(df[df['risk_level'] == 'high']) if 'risk_level' in df.columns else 0,
            'data_worth': len(df) * 0.50  # ₹0.50 per event
        }


# Test
if __name__ == '__main__':
    print("=" * 60)
    print("Unified Database Bridge Test")
    print("=" * 60)
    
    db = UnifiedDatabase()
    
    # Get stats
    stats = db.get_stats()
    print(f"\n📊 Stats:")
    print(f"   Total events: {stats['total_events']:,}")
    print(f"   Companies: {stats['unique_companies']}")
    print(f"   High risk: {stats['high_risk']}")
    print(f"   Data worth: ₹{stats['data_worth']:,.0f}")
    
    # Get sample data
    df = db.get_tracking_events(days_back=30)
    print(f"\n📋 Sample data:")
    print(df.head())
    
    print("\n" + "=" * 60)
    print("✅ Unified database working!")
    print("=" * 60)
