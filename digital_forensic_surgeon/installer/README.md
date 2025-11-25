# Building TrackerShield Installer

## Prerequisites

1. **Python 3.9+** installed
2. **PyInstaller**: `pip install pyinstaller`
3. **NSIS**: Download from https://nsis.sourceforge.io/Download
4. **PyQt6**: `pip install PyQt6`

## Build Steps

### Option 1: Automated (Windows)

```cmd
build_installer.bat
```

### Option 2: Manual

1. **Build executable:**
   ```cmd
   pyinstaller --name=tracker_shield_tray ^
       --noconsole ^
       --onefile ^
       --add-data "tracker_shield;tracker_shield" ^
       tracker_shield_tray.py
   ```

2. **Build installer:**
   ```cmd
   "C:\Program Files (x86)\NSIS\makensis.exe" installer\trackershield.nsi
   ```

3. **Output:**
   - Executable: `dist/tracker_shield_tray.exe`
   - Installer: `TrackerShield_Setup.exe`

## Distribution

The installer includes:
- System tray application
- All signature databases
- Auto-update system
- Uninstaller

Users can:
- Install with one click
- Auto-launch on Windows startup
- Access quick menu from tray
- Receive update notifications
