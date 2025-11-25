@echo off
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
