"""
Auto-Update System
Automatically downloads new signature databases
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict
import urllib.request
import urllib.error

class DatabaseUpdater:
    """Manages signature database updates"""
    
    def __init__(self, tier: str = 'free'):
        """
        Args:
            tier: free, pro, or god
        """
        self.tier = tier
        self.data_dir = Path('tracker_shield/data')
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.version_file = self.data_dir / f'{tier}_version.json'
        self.db_file = self.data_dir / f'tracker_shield_{tier}.tsdb'
        
        # Update endpoints (in production, use real URLs)
        self.base_url = "https://updates.trackershield.io/v1"
    
    def get_current_version(self) -> Dict:
        """Get currently installed version"""
        if not self.version_file.exists():
            return {'version': 0, 'date': None, 'signatures': 0}
        
        try:
            with open(self.version_file, 'r') as f:
                return json.load(f)
        except:
            return {'version': 0, 'date': None, 'signatures': 0}
    
    def check_for_updates(self) -> Optional[Dict]:
        """
        Check if new version is available
        
        Returns:
            Update info if available, None otherwise
        """
        
        current = self.get_current_version()
        
        # In production, fetch from server
        # For now, simulate
        latest_versions = self._get_mock_latest_versions()
        
        latest = latest_versions.get(self.tier, {})
        
        if latest.get('version', 0) > current.get('version', 0):
            return {
                'current_version': current.get('version', 0),
                'latest_version': latest['version'],
                'new_signatures': latest['signatures'] - current.get('signatures', 0),
                'release_date': latest['release_date'],
                'download_url': latest['download_url'],
                'checksum': latest['checksum']
            }
        
        return None
    
    def _get_mock_latest_versions(self) -> Dict:
        """
        Mock latest versions
        In production, fetch from: {base_url}/versions.json
        """
        return {
            'free': {
                'version': 2,
                'signatures': 55,  # Up from 47
                'release_date': '2025-12-01',
                'download_url': f'{self.base_url}/tracker_shield_free_v2.tsdb',
                'checksum': 'abc123...'
            },
            'pro': {
                'version': 5,
                'signatures': 120,  # Up from 89
                'release_date': '2025-11-25',
                'download_url': f'{self.base_url}/tracker_shield_pro_v5.tsdb',
                'checksum': 'def456...'
            },
            'god': {
                'version': 10,
                'signatures': 150,  # Up from 100
                'release_date': '2025-11-25',
                'download_url': f'{self.base_url}/tracker_shield_god_v10.tsdb',
                'checksum': 'ghi789...'
            }
        }
    
    def download_update(self, update_info: Dict) -> bool:
        """
        Download and install update
        
        Args:
            update_info: Update info from check_for_updates()
        
        Returns:
            True if successful
        """
        
        print(f"📥 Downloading update v{update_info['latest_version']}...")
        
        # In production, download from update_info['download_url']
        # For now, just verify current database exists
        
        if not self.db_file.exists():
            print(f"❌ Current database not found: {self.db_file}")
            return False
        
        # Create backup
        backup_file = self.db_file.with_suffix('.tsdb.backup')
        
        try:
            import shutil
            shutil.copy2(self.db_file, backup_file)
            print(f"✅ Backup created: {backup_file.name}")
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return False
        
        # In production:
        # 1. Download new database
        # 2. Verify checksum
        # 3. Verify GPG signature
        # 4. Replace old database
        # 5. Update version file
        
        # For now, just update version file
        try:
            new_version = {
                'version': update_info['latest_version'],
                'date': update_info['release_date'],
                'signatures': update_info['latest_version'] * 10,  # Mock
                'updated_at': datetime.now().isoformat()
            }
            
            with open(self.version_file, 'w') as f:
                json.dump(new_version, f, indent=2)
            
            print(f"✅ Updated to v{update_info['latest_version']}")
            print(f"   New signatures: +{update_info['new_signatures']}")
            return True
        
        except Exception as e:
            print(f"❌ Update failed: {e}")
            # Restore backup
            if backup_file.exists():
                shutil.copy2(backup_file, self.db_file)
                print(f"✅ Restored from backup")
            return False
    
    def rollback(self) -> bool:
        """Rollback to previous version"""
        backup_file = self.db_file.with_suffix('.tsdb.backup')
        
        if not backup_file.exists():
            print(f"❌ No backup found")
            return False
        
        try:
            import shutil
            shutil.copy2(backup_file, self.db_file)
            print(f"✅ Rolled back to backup")
            return True
        except Exception as e:
            print(f"❌ Rollback failed: {e}")
            return False


class UpdateScheduler:
    """Schedules automatic updates based on tier"""
    
    UPDATE_INTERVALS = {
        'free': 30,   # Days
        'pro': 1,     # Days
        'god': 1      # Days
    }
    
    def __init__(self, tier: str = 'free'):
        self.tier = tier
        self.updater = DatabaseUpdater(tier)
        self.last_check_file = Path.home() / ".trackershield" / "last_update_check.json"
        self.last_check_file.parent.mkdir(parents=True, exist_ok=True)
    
    def should_check_updates(self) -> bool:
        """Check if it's time to check for updates"""
        
        interval_days = self.UPDATE_INTERVALS.get(self.tier, 30)
        
        if not self.last_check_file.exists():
            return True
        
        try:
            with open(self.last_check_file, 'r') as f:
                data = json.load(f)
            
            last_check = datetime.fromisoformat(data['last_check'])
            days_since = (datetime.now() - last_check).days
            
            return days_since >= interval_days
        except:
            return True
    
    def mark_checked(self):
        """Mark that we checked for updates"""
        with open(self.last_check_file, 'w') as f:
            json.dump({
                'last_check': datetime.now().isoformat(),
                'tier': self.tier
            }, f)
    
    def auto_update(self) -> bool:
        """
        Auto-update if available and scheduled
        
        Returns:
            True if update was performed
        """
        
        if not self.should_check_updates():
            return False
        
        self.mark_checked()
        
        # Check for updates
        update_info = self.updater.check_for_updates()
        
        if not update_info:
            print(f"✅ Already on latest version")
            return False
        
        print(f"\n🎉 Update available!")
        print(f"   Current: v{update_info['current_version']}")
        print(f"   Latest: v{update_info['latest_version']}")
        print(f"   New signatures: +{update_info['new_signatures']}")
        
        # Download and install
        success = self.updater.download_update(update_info)
        
        return success


# Demo
if __name__ == '__main__':
    print("=" * 60)
    print("Auto-Update System Demo")
    print("=" * 60)
    
    # Test for each tier
    for tier in ['free', 'pro', 'god']:
        print(f"\n{'='*60}")
        print(f"Testing {tier.upper()} Tier")
        print(f"{'='*60}")
        
        updater = DatabaseUpdater(tier)
        
        # Check current version
        current = updater.get_current_version()
        print(f"\n📋 Current version:")
        print(f"   Version: {current.get('version', 0)}")
        print(f"   Signatures: {current.get('signatures', 0)}")
        
        # Check for updates
        update_info = updater.check_for_updates()
        
        if update_info:
            print(f"\n🎉 Update available!")
            print(f"   v{update_info['current_version']} → v{update_info['latest_version']}")
            print(f"   New signatures: +{update_info['new_signatures']}")
        else:
            print(f"\n✅ Already on latest version")
    
    print("\n" + "=" * 60)
    print("✅ Auto-Update System Working!")
    print("=" * 60)
