"""
Browser Cleaner for Digital Forensic Surgeon
Provides capabilities to remove browser data for specific sites.
"""

from __future__ import annotations

import os
import shutil
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional

from digital_forensic_surgeon.core.exceptions import BrowserAutomationError

class BrowserCleaner:
    """A class to surgically remove browser data for a specific domain."""

    def __init__(self, browser: str = "chrome"):
        self.browser = browser.lower()
        self.profile_path = self._get_profile_path()

    def _get_profile_path(self) -> Path:
        """
        Gets the path to the browser profile.
        NOTE: This is a simplified example. A real implementation would need to be
              much more robust to handle different OSes and browser versions.
        """
        if self.browser == "chrome":
            if os.name == 'nt':  # Windows
                return Path(os.environ['LOCALAPPDATA']) / 'Google' / 'Chrome' / 'User Data' / 'Default'
            elif os.name == 'posix':  # macOS / Linux
                if 'darwin' in os.sys.platform: # macOS
                    return Path.home() / 'Library' / 'Application Support' / 'Google' / 'Chrome' / 'Default'
                else: # Linux
                    return Path.home() / '.config' / 'google-chrome' / 'Default'
        elif self.browser == "firefox":
            # Firefox profile paths are more complex to locate.
            # This is a placeholder for a more robust implementation.
            if os.name == 'nt':
                app_data = Path(os.environ['APPDATA'])
                ff_path = app_data / 'Mozilla' / 'Firefox' / 'Profiles'
            else:
                ff_path = Path.home() / '.mozilla' / 'firefox'
            
            profiles = list(ff_path.glob('*.default-release'))
            if profiles:
                return profiles[0]

        raise BrowserAutomationError(f"Unsupported browser or OS: {self.browser}/{os.name}")

    def nuke_site_data(self, domain: str) -> Dict[str, Any]:
        """
        Removes all data associated with a given domain.
        This includes cookies, local storage, and session storage.
        """
        if not self.profile_path or not self.profile_path.exists():
            raise BrowserAutomationError(f"Browser profile path not found for {self.browser}")

        bytes_cleared = 0
        files_deleted = 0
        
        # 1. Clear Cookies
        cookies_db = self.profile_path / 'Cookies'
        if cookies_db.exists():
            try:
                conn = sqlite3.connect(str(cookies_db))
                cursor = conn.cursor()
                
                # Get size before
                size_before = cookies_db.stat().st_size

                # Delete cookies for the domain
                cursor.execute("DELETE FROM cookies WHERE host_key LIKE ?", (f'%{domain}%',))
                conn.commit()
                
                # Get size after
                conn.execute("VACUUM")
                conn.close()
                size_after = cookies_db.stat().st_size
                
                bytes_cleared += (size_before - size_after)
            except sqlite3.Error as e:
                raise BrowserAutomationError(f"Error clearing cookies for {domain}: {e}")

        # 2. Clear Local Storage & Session Storage
        # These are stored in LevelDB format, which is harder to manipulate directly.
        # The safest approach is to delete the files associated with the domain.
        storage_path = self.profile_path / 'Local Storage' / 'leveldb'
        if storage_path.exists():
            for f in storage_path.glob('*.log'):
                # This is a simplified approach. A real implementation would need to
                # parse the LevelDB logs to identify the correct entries.
                # For now, we'll just log that we can't do this yet.
                pass # Not implemented

        return {
            "status": "Partial success (cookie cleaning only)",
            "domain": domain,
            "bytes_cleared": bytes_cleared,
            "files_deleted": files_deleted,
            "notes": "Local/Session storage cleaning is not fully implemented in this version."
        }
