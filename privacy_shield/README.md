# PrivacyShield OS - Network Filter

System-level network traffic interceptor and tracker blocker.

## Requirements

### Python Packages:
```bash
pip install pydivert scapy psutil colorama
```

### System Requirements:
- Windows 10/11
- Administrator privileges
- WinDivert driver (auto-installed)

## Project Structure:
```
privacy_shield/
├── network_filter/
│   ├── packet_interceptor.py  # Core packet interception
│   ├── tracker_db.py           # Tracker domain database
│   └── blocker.py              # Blocking logic
├── requirements.txt
└── run.py                      # Main entry point
```

## How It Works:

1. **WinDivert** captures ALL network packets at kernel level
2. **Packet Inspector** checks if destination is a tracker
3. **Blocker** drops packets to trackers, forwards rest
4. **Logger** shows what was blocked in real-time

## Usage:

```bash
# Run as Administrator
python run.py
```

You'll see live blocking:
```
🚫 Blocked: chrome.exe → google-analytics.com
🚫 Blocked: spotify.exe → ads.spotify.com
✅ Allowed: chrome.exe → github.com
```
