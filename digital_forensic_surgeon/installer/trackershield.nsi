
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
