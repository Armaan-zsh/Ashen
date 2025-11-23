"""Browser scanner for Digital Forensic Surgeon - Phase 2: Shadow Self."""

from __future__ import annotations

import os
import sys
import platform
import sqlite3
import shutil
import tempfile
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Generator, Tuple
from datetime import datetime
import json
from dataclasses import dataclass

from digital_forensic_surgeon.core.models import EvidenceItem, ForensicResult, Account
from digital_forensic_surgeon.core.exceptions import ScannerError
from digital_forensic_surgeon.utils.helpers import create_temp_directory


@dataclass
class BrowserProfile:
    """Represents a browser profile with paths."""
    browser: str
    profile_path: Path
    user_data_dir: Path
    is_default: bool = False


@dataclass
class AutofillData:
    """Represents browser autofill data."""
    name: str
    value: str
    value_type: str
    count: int
    date_last_used: Optional[datetime]


@dataclass
class DownloadRecord:
    """Represents a browser download record."""
    target_path: str
    url: str
    start_time: datetime
    file_size: int
    mime_type: str


class BrowserScanner:
    """Scanner for browser data and artifacts - extracts real data from SQLite databases."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.system = platform.system().lower()
        self.temp_dir = create_temp_directory("browser_extract")
        self.browser_paths = self._get_browser_paths()
    
    def scan_browser_data(self, browser: Optional[str] = None) -> Generator[EvidenceItem, None, None]:
        """Scan browser data for forensic artifacts."""
        browsers = [browser] if browser else ["chrome", "firefox", "edge"]
        
        for browser_name in browsers:
            try:
                yield from self._scan_browser_specific(browser_name)
            except Exception as e:
                yield EvidenceItem(
                    type="browser_scan_error",
                    source="browser",
                    path=f"browser_{browser_name}",
                    content=f"Failed to scan {browser_name}: {e}",
                    is_sensitive=True,
                    confidence=0.1
                )
    
    def _scan_browser_specific(self, browser: str) -> Generator[EvidenceItem, None, None]:
        """Scan specific browser data using real SQLite extraction."""
        profiles = self._get_browser_profiles(browser)
        
        if not profiles:
            yield EvidenceItem(
                type="browser_profile",
                source="browser",
                path=f"{browser}_profile",
                content=f"No {browser} profiles found",
                metadata={"browser": browser, "profiles_found": 0},
                is_sensitive=False,
                confidence=0.5
            )
            return
        
        for profile in profiles:
            try:
                yield from self._scan_profile(profile)
            except Exception as e:
                yield EvidenceItem(
                    type="browser_scan_error",
                    source="browser",
                    path=str(profile.profile_path),
                    content=f"Failed to scan profile {profile.profile_path}: {e}",
                    is_sensitive=True,
                    confidence=0.1
                )
    
    def _get_browser_paths(self) -> Dict[str, Dict[str, Any]]:
        """Get standard browser profile paths for different platforms."""
        paths = {
            "chrome": {
                "windows": "~\\AppData\\Local\\Google\\Chrome\\User Data",
                "darwin": "~/Library/Application Support/Google/Chrome",
                "linux": "~/.config/google-chrome"
            },
            "firefox": {
                "windows": "~\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles",
                "darwin": "~/Library/Application Support/Firefox/Profiles",
                "linux": "~/.mozilla/firefox"
            },
            "edge": {
                "windows": "~\\AppData\\Local\\Microsoft\\Edge\\User Data",
                "darwin": "~/Library/Application Support/Microsoft Edge",
                "linux": "~/.config/microsoft-edge"
            }
        }
        
        # Expand home directory paths
        for browser in paths:
            for platform_name in paths[browser]:
                try:
                    paths[browser][platform_name] = Path(paths[browser][platform_name]).expanduser()
                except RuntimeError:
                    # In cloud environments, use placeholder paths
                    paths[browser][platform_name] = Path(paths[browser][platform_name])
        
        return paths
    
    def _get_browser_profiles(self, browser: str) -> List[BrowserProfile]:
        """Identify browser profiles for a specific browser."""
        profiles = []
        
        if browser not in self.browser_paths:
            return profiles
        
        platform_paths = self.browser_paths[browser]
        if self.system not in platform_paths:
            return profiles
        
        user_data_dir = platform_paths[self.system]
        
        if not user_data_dir.exists():
            return profiles
        
        try:
            if browser == "firefox":
                # Firefox uses profile directories with random names
                for profile_dir in user_data_dir.glob("*.default*"):
                    profiles.append(BrowserProfile(
                        browser=browser,
                        profile_path=profile_dir,
                        user_data_dir=user_data_dir,
                        is_default="default" in profile_dir.name
                    ))
            else:
                # Chrome/Edge use a "Default" profile
                default_profile = user_data_dir / "Default"
                if default_profile.exists():
                    profiles.append(BrowserProfile(
                        browser=browser,
                        profile_path=default_profile,
                        user_data_dir=user_data_dir,
                        is_default=True
                    ))
        
        except Exception:
            pass
        
        return profiles
    
    def _scan_profile(self, profile: BrowserProfile) -> Generator[EvidenceItem, None, None]:
        """Scan a specific browser profile for data."""
        # Extract autofill data
        yield from self._extract_autofill_data(profile)
        
        # Extract download history
        yield from self._extract_download_history(profile)
        
        # Generate profile summary
        yield EvidenceItem(
            type="browser_profile",
            source="browser",
            path=str(profile.profile_path),
            content=f"Scanned {profile.browser} profile at {profile.profile_path}",
            metadata={
                "browser": profile.browser,
                "profile_path": str(profile.profile_path),
                "is_default": profile.is_default,
                "scanned_at": datetime.now().isoformat()
            },
            is_sensitive=True,
            confidence=0.9
        )
    
    def _safe_copy_db(self, db_path: Path) -> Optional[Path]:
        """Copy a database to a temporary location to handle locked files."""
        if not db_path.exists():
            return None
        
        try:
            temp_db = self.temp_dir / f"{db_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.sqlite"
            shutil.copy2(db_path, temp_db)
            return temp_db
        except Exception:
            return None
    
    def _extract_autofill_data(self, profile: BrowserProfile) -> Generator[EvidenceItem, None, None]:
        """Extract autofill data from browser Web Data SQLite database."""
        try:
            # Different database names for different browsers
            db_names = ["Web Data", "Form Data", "formhistory.sqlite"]
            
            for db_name in db_names:
                db_path = profile.profile_path / db_name
                
                if db_path.exists():
                    temp_db = self._safe_copy_db(db_path)
                    if not temp_db:
                        continue
                    
                    try:
                        with sqlite3.connect(temp_db) as conn:
                            cursor = conn.cursor()
                            
                            # Try different table schemas
                            tables_to_try = [
                                "autofill", "autofill_profiles", "credit_cards", 
                                "moz_formhistory", "formhistory"
                            ]
                            
                            for table in tables_to_try:
                                try:
                                    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                                    if cursor.fetchone():
                                        yield from self._query_autofill_table(conn, table, profile.browser)
                                        break
                                except sqlite3.Error:
                                    continue
                    
                    finally:
                        if temp_db.exists():
                            temp_db.unlink()
        
        except Exception as e:
            yield EvidenceItem(
                type="browser_autofill_error",
                source="browser",
                path=str(profile.profile_path),
                content=f"Failed to extract autofill data: {e}",
                is_sensitive=True,
                confidence=0.1
            )
    
    def _query_autofill_table(self, conn, table: str, browser: str) -> Generator[EvidenceItem, None, None]:
        """Query autofill table and yield structured data."""
        try:
            cursor = conn.cursor()
            
            # Different column schemas for different browsers
            column_sets = [
                ("name", "value", "value_type", "count", "date_last_used"),
                ("name", "value", "value_type", "usage_count", "date_last_used"),
                ("fieldname", "value", "times_used", "first_used", "last_used")
            ]
            
            for columns in column_sets:
                try:
                    query = f"SELECT {', '.join(columns)} FROM {table} LIMIT 100"
                    cursor.execute(query)
                    rows = cursor.fetchall()
                    
                    if not rows:
                        continue
                    
                    # Process the data
                    autofill_items = []
                    for row in rows:
                        try:
                            if len(row) >= 2 and row[0] and row[1]:  # Ensure we have name and value
                                item = {
                                    "name": str(row[0]).strip(),
                                    "value": str(row[1]).strip(),
                                    "value_type": str(row[2]) if len(row) > 2 else "unknown",
                                    "count": int(row[3]) if len(row) > 3 and row[3] else 1,
                                    "browser": browser
                                }
                                
                                # Add to evidence if it looks like personal data
                                if self._is_personal_data(item["name"], item["value"]):
                                    autofill_items.append(item)
                        except (ValueError, IndexError):
                            continue
                    
                    if autofill_items:
                        yield EvidenceItem(
                            type="browser_autofill",
                            source="browser",
                            path=f"{browser}_autofill",
                            content=f"Found {len(autofill_items)} autofill entries",
                            metadata={
                                "browser": browser,
                                "table": table,
                                "autofill_data": autofill_items,
                                "personal_data_count": len(autofill_items)
                            },
                            is_sensitive=True,
                            confidence=0.9
                        )
                        break
                        
                except sqlite3.Error:
                    continue
        
        except Exception:
            pass
    
    def _is_personal_data(self, field_name: str, value: str) -> bool:
        """Check if field contains potentially sensitive personal data."""
        field_lower = field_name.lower()
        value_lower = value.lower()
        
        personal_indicators = [
            "name", "email", "phone", "address", "street", "city", "zip", 
            "firstname", "lastname", "fullname", "credit", "card", "cc-number"
        ]
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        phone_pattern = r'^\+?[\d\s\-\(\)]{10,}$'
        
        return (
            any(indicator in field_lower for indicator in personal_indicators) or
            bool(re.match(email_pattern, value)) or
            bool(re.match(phone_pattern, value))
        )
    
    def _extract_download_history(self, profile: BrowserProfile) -> Generator[EvidenceItem, None, None]:
        """Extract download history from browser History SQLite database."""
        try:
            history_path = profile.profile_path / "History"
            
            if not history_path.exists():
                return
            
            temp_db = self._safe_copy_db(history_path)
            if not temp_db:
                return
            
            try:
                with sqlite3.connect(temp_db) as conn:
                    cursor = conn.cursor()
                    
                    # Query downloads with URL correlation
                    download_queries = [
                        """
                        SELECT d.target_path, du.url, d.start_time, d.total_bytes, d.mime_type
                        FROM downloads d 
                        JOIN downloads_url_chains du ON d.id = du.id
                        LIMIT 100
                        """,
                        """
                        SELECT current_path, url, start_time, 0, mime_type
                        FROM downloads
                        LIMIT 100
                        """,
                        """
                        SELECT target_path, source, dateAdded, totalBytes, mimeType
                        FROM moz_downloads
                        LIMIT 100
                        """
                    ]
                    
                    for query in download_queries:
                        try:
                            cursor.execute(query)
                            rows = cursor.fetchall()
                            
                            if rows:
                                download_items = []
                                for row in rows:
                                    try:
                                        if len(row) >= 2:
                                            item = {
                                                "target_path": str(row[0]),
                                                "url": str(row[1]) if len(row) > 1 else "",
                                                "start_time": datetime.fromtimestamp(row[2]) if row[2] else None,
                                                "file_size": int(row[3]) if len(row) > 3 and row[3] else 0,
                                                "mime_type": str(row[4]) if len(row) > 4 else "unknown",
                                                "browser": profile.browser
                                            }
                                            download_items.append(item)
                                    except (ValueError, IndexError):
                                        continue
                                
                                if download_items:
                                    yield EvidenceItem(
                                        type="browser_download",
                                        source="browser",
                                        path=f"{profile.browser}_downloads",
                                        content=f"Found {len(download_items)} download records",
                                        metadata={
                                            "browser": profile.browser,
                                            "download_data": download_items,
                                            "total_downloads": len(download_items)
                                        },
                                        is_sensitive=True,
                                        confidence=0.8
                                    )
                                    break
                                    
                        except sqlite3.Error:
                            continue
            
            finally:
                if temp_db.exists():
                    temp_db.unlink()
        
        except Exception:
            pass
    
    def extract_credentials(self, profile: BrowserProfile) -> Generator[EvidenceItem, None, None]:
        """Extract saved passwords (NOT IMPLEMENTED - requires decryption)."""
        # This would require password decryption which is complex and browser-specific
        # For security reasons, we'll skip this and focus on the safer autofill data
        pass
    
    def get_browser_summary(self, evidence_items: List[EvidenceItem]) -> Dict[str, Any]:
        """Generate summary of browser scan results."""
        summary = {
            "total_items": len(evidence_items),
            "autofill_items": 0,
            "download_items": 0,
            "browsers_found": set(),
            "personal_data_fields": set(),
            "download_urls": []
        }
        
        for item in evidence_items:
            if item.type == "browser_autofill":
                summary["autofill_items"] += 1
                if "autofill_data" in item.metadata:
                    for data in item.metadata["autofill_data"]:
                        summary["personal_data_fields"].add(data.get("name", ""))
            
            elif item.type == "browser_download":
                summary["download_items"] += 1
                if "download_data" in item.metadata:
                    for data in item.metadata["download_data"]:
                        summary["download_urls"].append(data.get("url", ""))
            
            elif "browser" in item.metadata:
                summary["browsers_found"].add(item.metadata["browser"])
        
        summary["browsers_found"] = list(summary["browsers_found"])
        summary["personal_data_fields"] = list(summary["personal_data_fields"])
        
        return summary