"""
Windows Installer Script Generator
Creates NSIS installer script for TrackerShield
"""

from pathlib import Path

def generate_nsis_script():
    """Generate NSIS installer script"""
    
    script = r'''
; TrackerShield Installer Script
; Generated for NSIS (Nullsoft Scriptable Install System)

!define APP_NAME "TrackerShield"
!define APP_VERSION "1.0.0"
!define APP_PUBLISHER "TrackerShield"
!define APP_URL "https://trackershield.io"
!define APP_EXE "tracker_shield_tray.exe"

; Installer settings
Name "${APP_NAME}"
OutFile "TrackerShield_Setup.exe"
InstallDir "$PROGRAMFILES64\${APP_NAME}"
InstallDirRegKey HKLM "Software\${APP_NAME}" "Install_Dir"
RequestExecutionLevel admin

; Modern UI
!include "MUI2.nsh"

; Interface Settings
!define MUI_ABORTWARNING
!define MUI_ICON "icon.ico"
!define MUI_UNICON "icon.ico"

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Languages
!insertmacro MUI_LANGUAGE "English"

; Installer Sections
Section "TrackerShield (required)"
  
  SectionIn RO
  
  ; Set output path
  SetOutPath $INSTDIR
  
  ; Copy files
  File /r "dist\tracker_shield\*.*"
  
  ; Write uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  
  ; Registry keys
  WriteRegStr HKLM "Software\${APP_NAME}" "Install_Dir" "$INSTDIR"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayName" "${APP_NAME}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "UninstallString" '"$INSTDIR\Uninstall.exe"'
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayIcon" '"$INSTDIR\${APP_EXE}"'
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "DisplayVersion" "${APP_VERSION}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "Publisher" "${APP_PUBLISHER}"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "URLInfoAbout" "${APP_URL}"
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}" "NoRepair" 1
  
  ; Create shortcuts
  CreateDirectory "$SMPROGRAMS\${APP_NAME}"
  CreateShortcut "$SMPROGRAMS\${APP_NAME}\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}"
  CreateShortcut "$SMPROGRAMS\${APP_NAME}\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
  CreateShortcut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\${APP_EXE}"
  
SectionEnd

; Auto-start section (optional)
Section "Start with Windows"
  
  WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Run" "${APP_NAME}" '"$INSTDIR\${APP_EXE}"'
  
SectionEnd

; Uninstaller
Section "Uninstall"
  
  ; Remove registry keys
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_NAME}"
  DeleteRegKey HKLM "Software\${APP_NAME}"
  DeleteRegValue HKCU "Software\Microsoft\Windows\CurrentVersion\Run" "${APP_NAME}"
  
  ; Remove files
  RMDir /r "$INSTDIR"
  
  ; Remove shortcuts
  Delete "$SMPROGRAMS\${APP_NAME}\*.*"
  RMDir "$SMPROGRAMS\${APP_NAME}"
  Delete "$DESKTOP\${APP_NAME}.lnk"
  
SectionEnd
'''
    
    # Save script
    script_file = Path('installer/trackershield.nsi')
    script_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(script_file, 'w') as f:
        f.write(script)
    
    print(f"✅ Generated NSIS installer script: {script_file}")
    
    # Create build script
    build_script = r'''@echo off
echo Building TrackerShield Installer...

REM 1. Build executable with PyInstaller
echo.
echo [1/3] Building executable...
pyinstaller --name=tracker_shield_tray ^
    --noconsole ^
    --onefile ^
    --add-data "tracker_shield;tracker_shield" ^
    --add-data "landing_page.html;." ^
    --icon=icon.ico ^
    tracker_shield_tray.py

REM 2. Build installer with NSIS
echo.
echo [2/3] Building installer...
"C:\Program Files (x86)\NSIS\makensis.exe" installer\trackershield.nsi

REM 3. Done
echo.
echo [3/3] Done!
echo.
echo Installer created: TrackerShield_Setup.exe
pause
'''
    
    build_file = Path('build_installer.bat')
    with open(build_file, 'w') as f:
        f.write(build_script)
    
    print(f"✅ Generated build script: {build_file}")
    
    # Create README
    readme = '''# Building TrackerShield Installer

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
   "C:\\Program Files (x86)\\NSIS\\makensis.exe" installer\\trackershield.nsi
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
'''
    
    readme_file = Path('installer/README.md')
    with open(readme_file, 'w') as f:
        f.write(readme)
    
    print(f"✅ Generated README: {readme_file}")
    
    print("\n" + "=" * 60)
    print("✅ Installer scripts generated!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Install NSIS from: https://nsis.sourceforge.io/Download")
    print("2. Install PyInstaller: pip install pyinstaller PyQt6")
    print("3. Run: build_installer.bat")


if __name__ == '__main__':
    generate_nsis_script()
