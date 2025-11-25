"""
Test TrackerShield with mitmproxy
Run this to test the new signature-based addon
"""

import subprocess
import time
from pathlib import Path

def test_tracker_shield_proxy():
    """Test TrackerShield addon with mitmproxy"""
    
    print("=" * 70)
    print("TrackerShield mitmproxy Integration Test")
    print("=" * 70)
    
    # Check if addon exists
    addon_path = Path('tracker_shield_addon.py')
    if not addon_path.exists():
        print(f"❌ Addon not found: {addon_path}")
        return
    
    print(f"\n✅ Addon found: {addon_path}")
    print(f"\n🚀 Starting mitmproxy with TrackerShield...")
    print(f"\nInstructions:")
    print(f"1. Configure your browser to use proxy: localhost:8080")
    print(f"2. Visit tracking-heavy sites (Facebook, Google, etc.)")
    print(f"3. Watch console for signature matches")
    print(f"4. Press Ctrl+C to stop")
    print(f"\n" + "=" * 70 + "\n")
    
    try:
        # Start mitmproxy with TrackerShield addon
        subprocess.run([
            'mitmdump',
            '--listen-port', '8080',
            '--ssl-insecure',
            '-s', str(addon_path),
            '--set', 'trackershield_license='  # Empty = free tier
        ])
    except KeyboardInterrupt:
        print(f"\n\n✅ Stopped TrackerShield")
    except FileNotFoundError:
        print(f"\n❌ mitmproxy not installed. Install with: pip install mitmproxy")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == '__main__':
    test_tracker_shield_proxy()
