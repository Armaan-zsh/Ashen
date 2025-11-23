"""
Browser History Scanner
Extracts browsing history, cookies, and tracking data from browser SQLite databases
"""

import sqlite3
import shutil
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass
import tempfile


@dataclass
class HistoricalEvent:
    """Represents a historical browser event"""
    timestamp: datetime
    event_type: str  # 'visit', 'cookie', 'download', 'search'
    url: str
    domain: str
    browser: str
    title: Optional[str] = None
    visit_count: Optional[int] = None
    cookie_name: Optional[str] = None
    cookie_value: Optional[str] = None
    search_term: Optional[str] = None


class BrowserHistoryScanner:
    """Scans browser databases to extract historical data"""
    
    def __init__(self):
        self.events: List[HistoricalEvent] = []
        self.user_home = Path.home()
    
    def scan_all_browsers(self) -> List[HistoricalEvent]:
        """Scan all installed browsers"""
        print("🔍 Scanning browser databases...")
        
        # Chrome/Edge (Chromium-based)
        chrome_events = self.scan_chrome()
        edge_events = self.scan_edge()
        
        # Firefox
        firefox_events = self.scan_firefox()
        
        # Combine all
        all_events = chrome_events + edge_events + firefox_events
        
        # Sort by timestamp
        all_events.sort(key=lambda x: x.timestamp, reverse=True)
        
        print(f"✓ Total events found: {len(all_events):,}")
        return all_events
    
    def scan_chrome(self) -> List[HistoricalEvent]:
        """Scan Chrome browser data"""
        events = []
        
        # Chrome paths (Windows)
        chrome_base = self.user_home / "AppData" / "Local" / "Google" / "Chrome" / "User Data" / "Default"
        
        if not chrome_base.exists():
            print("  ⚠️ Chrome not found")
            return events
        
        # Scan history
        history_path = chrome_base / "History"
        if history_path.exists():
            history_events = self._scan_chromium_history(history_path, "Chrome")
            events.extend(history_events)
            print(f"  ✓ Chrome history: {len(history_events):,} visits")
        
        # Scan cookies
        cookies_path = chrome_base / "Cookies" if (chrome_base / "Cookies").exists() else chrome_base / "Network" / "Cookies"
        if cookies_path.exists():
            cookie_events = self._scan_chromium_cookies(cookies_path, "Chrome")
            events.extend(cookie_events)
            print(f"  ✓ Chrome cookies: {len(cookie_events):,} cookies")
        
        return events
    
    def scan_edge(self) -> List[HistoricalEvent]:
        """Scan Edge browser data"""
        events = []
        
        # Edge paths (Windows)
        edge_base = self.user_home / "AppData" / "Local" / "Microsoft" / "Edge" / "User Data" / "Default"
        
        if not edge_base.exists():
            print("  ⚠️ Edge not found")
            return events
        
        # Scan history
        history_path = edge_base / "History"
        if history_path.exists():
            history_events = self._scan_chromium_history(history_path, "Edge")
            events.extend(history_events)
            print(f"  ✓ Edge history: {len(history_events):,} visits")
        
        # Scan cookies
        cookies_path = edge_base / "Cookies" if (edge_base / "Cookies").exists() else edge_base / "Network" / "Cookies"
        if cookies_path.exists():
            cookie_events = self._scan_chromium_cookies(cookies_path, "Edge")
            events.extend(cookie_events)
            print(f"  ✓ Edge cookies: {len(cookie_events):,} cookies")
        
        return events
    
    def scan_firefox(self) -> List[HistoricalEvent]:
        """Scan Firefox browser data"""
        events = []
        
        # Firefox profiles directory
        firefox_base = self.user_home / "AppData" / "Roaming" / "Mozilla" / "Firefox" / "Profiles"
        
        if not firefox_base.exists():
            print("  ⚠️ Firefox not found")
            return events
        
        # Find default profile (usually ends with .default or .default-release)
        profiles = [p for p in firefox_base.iterdir() if p.is_dir() and 'default' in p.name.lower()]
        
        if not profiles:
            print("  ⚠️ No Firefox profile found")
            return events
        
        profile = profiles[0]  # Use first default profile
        
        # Scan history
        history_path = profile / "places.sqlite"
        if history_path.exists():
            history_events = self._scan_firefox_history(history_path)
            events.extend(history_events)
            print(f"  ✓ Firefox history: {len(history_events):,} visits")
        
        # Scan cookies
        cookies_path = profile / "cookies.sqlite"
        if cookies_path.exists():
            cookie_events = self._scan_firefox_cookies(cookies_path)
            events.extend(cookie_events)
            print(f"  ✓ Firefox cookies: {len(cookie_events):,} cookies")
        
        return events
    
    def _scan_chromium_history(self, db_path: Path, browser: str) -> List[HistoricalEvent]:
        """Scan Chromium-based browser history database"""
        events = []
        
        # Copy database to temp (avoid locking issues)
        temp_db = self._copy_to_temp(db_path)
        if not temp_db:
            return events
        
        try:
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            
            # Query visits
            query = """
                SELECT urls.url, urls.title, urls.visit_count, 
                       visits.visit_time, urls.last_visit_time
                FROM urls
                LEFT JOIN visits ON urls.id = visits.url
                WHERE urls.url IS NOT NULL
                ORDER BY visits.visit_time DESC
                LIMIT 10000
            """
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            for row in rows:
                url, title, visit_count, visit_time, last_visit = row
                
                if visit_time:
                    # Chrome timestamps are microseconds since 1601-01-01
                    timestamp = self._chrome_timestamp_to_datetime(visit_time)
                elif last_visit:
                    timestamp = self._chrome_timestamp_to_datetime(last_visit)
                else:
                    continue
                
                # Extract domain
                domain = self._extract_domain(url)
                
                event = HistoricalEvent(
                    timestamp=timestamp,
                    event_type='visit',
                    url=url,
                    domain=domain,
                    browser=browser,
                    title=title,
                    visit_count=visit_count
                )
                events.append(event)
            
            conn.close()
            
        except Exception as e:
            print(f"  ⚠️ Error scanning {browser} history: {e}")
        
        finally:
            # Clean up temp file
            try:
                os.unlink(temp_db)
            except:
                pass
        
        return events
    
    def _scan_chromium_cookies(self, db_path: Path, browser: str) -> List[HistoricalEvent]:
        """Scan Chromium-based browser cookies database"""
        events = []
        
        # Copy database to temp
        temp_db = self._copy_to_temp(db_path)
        if not temp_db:
            return events
        
        try:
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            
            # Query cookies
            query = """
                SELECT host_key, name, value, creation_utc, last_access_utc
                FROM cookies
                ORDER BY last_access_utc DESC
                LIMIT 5000
            """
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            for row in rows:
                domain, name, value, created, accessed = row
                
                # Use last access time
                timestamp = self._chrome_timestamp_to_datetime(accessed) if accessed else self._chrome_timestamp_to_datetime(created)
                
                event = HistoricalEvent(
                    timestamp=timestamp,
                    event_type='cookie',
                    url=f"https://{domain}",
                    domain=domain,
                    browser=browser,
                    cookie_name=name,
                    cookie_value=value[:50] if value else ""  # Truncate value
                )
                events.append(event)
            
            conn.close()
            
        except Exception as e:
            print(f"  ⚠️ Error scanning {browser} cookies: {e}")
        
        finally:
            try:
                os.unlink(temp_db)
            except:
                pass
        
        return events
    
    def _scan_firefox_history(self, db_path: Path) -> List[HistoricalEvent]:
        """Scan Firefox history database"""
        events = []
        
        temp_db = self._copy_to_temp(db_path)
        if not temp_db:
            return events
        
        try:
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            
            # Query visits
            query = """
                SELECT moz_places.url, moz_places.title, moz_places.visit_count,
                       moz_historyvisits.visit_date
                FROM moz_places
                LEFT JOIN moz_historyvisits ON moz_places.id = moz_historyvisits.place_id
                WHERE moz_places.url IS NOT NULL
                ORDER BY moz_historyvisits.visit_date DESC
                LIMIT 10000
            """
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            for row in rows:
                url, title, visit_count, visit_date = row
                
                if not visit_date:
                    continue
                
                # Firefox timestamps are microseconds since Unix epoch
                timestamp = datetime.fromtimestamp(visit_date / 1000000)
                
                domain = self._extract_domain(url)
                
                event = HistoricalEvent(
                    timestamp=timestamp,
                    event_type='visit',
                    url=url,
                    domain=domain,
                    browser='Firefox',
                    title=title,
                    visit_count=visit_count
                )
                events.append(event)
            
            conn.close()
            
        except Exception as e:
            print(f"  ⚠️ Error scanning Firefox history: {e}")
        
        finally:
            try:
                os.unlink(temp_db)
            except:
                pass
        
        return events
    
    def _scan_firefox_cookies(self, db_path: Path) -> List[HistoricalEvent]:
        """Scan Firefox cookies database"""
        events = []
        
        temp_db = self._copy_to_temp(db_path)
        if not temp_db:
            return events
        
        try:
            conn = sqlite3.connect(temp_db)
            cursor = conn.cursor()
            
            # Query cookies
            query = """
                SELECT host, name, value, creationTime, lastAccessed
                FROM moz_cookies
                ORDER BY lastAccessed DESC
                LIMIT 5000
            """
            
            cursor.execute(query)
            rows = cursor.fetchall()
            
            for row in rows:
                domain, name, value, created, accessed = row
                
                # Firefox timestamps are microseconds since Unix epoch
                timestamp = datetime.fromtimestamp(accessed / 1000000) if accessed else datetime.fromtimestamp(created / 1000000)
                
                event = HistoricalEvent(
                    timestamp=timestamp,
                    event_type='cookie',
                    url=f"https://{domain}",
                    domain=domain,
                    browser='Firefox',
                    cookie_name=name,
                    cookie_value=value[:50] if value else ""
                )
                events.append(event)
            
            conn.close()
            
        except Exception as e:
            print(f"  ⚠️ Error scanning Firefox cookies: {e}")
        
        finally:
            try:
                os.unlink(temp_db)
            except:
                pass
        
        return events
    
    def _copy_to_temp(self, source: Path) -> Optional[str]:
        """Copy database to temp location to avoid locking"""
        try:
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, f"forensic_temp_{source.name}")
            shutil.copy2(source, temp_path)
            return temp_path
        except Exception as e:
            print(f"  ⚠️ Could not copy {source.name}: {e}")
            return None
    
    def _chrome_timestamp_to_datetime(self, timestamp: int) -> datetime:
        """Convert Chrome timestamp to datetime"""
        # Chrome uses microseconds since 1601-01-01
        # Convert to Unix timestamp
        unix_timestamp = (timestamp / 1000000) - 11644473600
        return datetime.fromtimestamp(unix_timestamp)
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        from urllib.parse import urlparse
        try:
            parsed = urlparse(url)
            return parsed.netloc or url
        except:
            return url
