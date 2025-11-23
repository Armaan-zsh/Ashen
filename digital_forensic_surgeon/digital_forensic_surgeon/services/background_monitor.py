"""
24/7 Background Monitoring Service
Continuously monitors for new tracking events and logs to database
"""

import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

from ..scanners.browser_history_scanner import BrowserHistoryScanner
from ..database.tracking_schema import TrackingDatabase
from ..scanners.data_broker_database import DataBrokerDatabase


class BackgroundMonitor:
    """Background service that continuously monitors for tracking"""
    
    def __init__(self, scan_interval: int = 60):
        """
        Initialize monitor
        
        Args:
            scan_interval: Seconds between scans (default: 60)
        """
        self.scan_interval = scan_interval
        self.is_running = False
        self.monitor_thread = None
        
        self.db = TrackingDatabase()
        self.scanner = BrowserHistoryScanner()
        self.tracker_db = DataBrokerDatabase()
        
        self.session_id = None
        self.last_scan_time = None
        self.processed_urls = set()  # Track what we've already logged
    
    def start(self):
        """Start background monitoring"""
        if self.is_running:
            print("[Monitor] Already running")
            return
        
        print("\n" + "="*70)
        print("  🚀 STARTING 24/7 BACKGROUND MONITOR")
        print("="*70)
        print(f"  Scan interval: {self.scan_interval} seconds")
        print(f"  Database: {self.db.db_path}")
        print()
        
        # Create new session
        self.session_id = self.db.create_session()
        print(f"  ✓ Session created: #{self.session_id}")
        
        self.is_running = True
        # Start from far in the past to capture ALL events on first scan
        self.last_scan_time = datetime.now() - timedelta(days=365 * 10)  # 10 years ago
        
        # Start background thread
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        
        print(f"  ✓ Monitor started")
        print(f"  📊 Live tracking data being logged to database")
        print(f"  💡 Query anytime with --query command")
        print()
    
    def stop(self):
        """Stop background monitoring"""
        if not self.is_running:
            return
        
        print("\n[Monitor] Stopping...")
        
        self.is_running = False
        
        # End session
        if self.session_id:
            self.db.end_session(self.session_id)
        
        # Wait for thread
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
        
        print("[Monitor] ✓ Stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        print("[Monitor] 🔄 Monitoring loop started")
        
        while self.is_running:
            try:
                self._scan_and_log()
                time.sleep(self.scan_interval)
            except Exception as e:
                print(f"[Monitor] ⚠️ Error in monitoring loop: {e}")
                time.sleep(self.scan_interval)
    
    def _scan_and_log(self):
        """Scan browsers and log new tracking events"""
        
        # Scan all browsers
        events = self.scanner.scan_all_browsers()
        
        new_events_count = 0
        
        for event in events:
            # Only process events since last scan
            if event.timestamp < self.last_scan_time:
                continue
            
            # Create unique key to avoid duplicates
            event_key = f"{event.timestamp.isoformat()}_{event.url}_{event.event_type}"
            if event_key in self.processed_urls:
                continue
            
            # Check if this is a tracker
            classification = self.tracker_db.classify_url(event.url)
            
            if classification['is_tracker']:
                # Log to database
                self.db.log_tracking_event(
                    session_id=self.session_id,
                    company_name=classification['entity_name'],
                    domain=event.domain,
                    url=event.url,
                    tracking_type=event.event_type,
                    category=classification['category'],
                    risk_score=classification['risk_score'],
                    browser=event.browser
                )
                
                new_events_count += 1
                self.processed_urls.add(event_key)
        
        # Always log scan results
        print(f"[Monitor] {datetime.now().strftime('%H:%M:%S')} - Scanned {len(events)} total events, saved {new_events_count} new tracking events to database")
        
        self.last_scan_time = datetime.now()
    
    def get_status(self) -> dict:
        """Get current monitoring status"""
        return {
            'is_running': self.is_running,
            'session_id': self.session_id,
            'scan_interval': self.scan_interval,
            'last_scan': self.last_scan_time.isoformat() if self.last_scan_time else None,
            'database_path': str(self.db.db_path)
        }



class MonitorManager:
    """Manages the background monitor as a persistent service"""
    
    _instance = None
    _monitor = None
    
    @classmethod
    def get_monitor(cls) -> BackgroundMonitor:
        """Get or create the monitor instance (singleton)"""
        if cls._monitor is None:
            cls._monitor = BackgroundMonitor(scan_interval=60)
        return cls._monitor
    
    @classmethod
    def start_monitor(cls):
        """Start the monitor"""
        monitor = cls.get_monitor()
        monitor.start()
        return monitor
    
    @classmethod
    def stop_monitor(cls):
        """Stop the monitor"""
        if cls._monitor:
            cls._monitor.stop()
    
    @classmethod
    def is_running(cls) -> bool:
        """Check if monitor is running"""
        return cls._monitor is not None and cls._monitor.is_running
