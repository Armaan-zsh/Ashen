"""
TrackerShield System Tray
Runs in background with quick access menu
"""

import sys
from pathlib import Path
import json
from datetime import datetime

try:
    from PyQt6.QtWidgets import (QApplication, QSystemTrayIcon, QMenu, 
                                  QMessageBox, QDialog, QVBoxLayout, QLabel, 
                                  QLineEdit, QPushButton, QCheckBox)
    from PyQt6.QtGui import QIcon, QAction
    from PyQt6.QtCore import Qt, QTimer
except ImportError:
    print("PyQt6 not installed. Install with: pip install PyQt6")
    sys.exit(1)


class SettingsDialog(QDialog):
    """Settings dialog"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("TrackerShield Settings")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # License key
        layout.addWidget(QLabel("License Key:"))
        self.license_input = QLineEdit()
        self.license_input.setPlaceholderText("TSGD-XXXX-XXXX or leave empty for Free tier")
        layout.addWidget(self.license_input)
        
        # Auto-launch
        self.autolaunch_checkbox = QCheckBox("Launch on Windows startup")
        layout.addWidget(self.autolaunch_checkbox)
        
        # Auto-update
        self.autoupdate_checkbox = QCheckBox("Automatically check for updates")
        self.autoupdate_checkbox.setChecked(True)
        layout.addWidget(self.autoupdate_checkbox)
        
        # Save button
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.accept)
        layout.addWidget(save_btn)
        
        self.setLayout(layout)
    
    def get_settings(self):
        """Get current settings"""
        return {
            'license_key': self.license_input.text(),
            'auto_launch': self.autolaunch_checkbox.isChecked(),
            'auto_update': self.autoupdate_checkbox.isChecked()
        }
    
    def set_settings(self, settings):
        """Load settings"""
        self.license_input.setText(settings.get('license_key', ''))
        self.autolaunch_checkbox.setChecked(settings.get('auto_launch', False))
        self.autoupdate_checkbox.setChecked(settings.get('auto_update', True))


class TrackerShieldTray(QSystemTrayIcon):
    """System tray application"""
    
    def __init__(self, icon, parent=None):
        super().__init__(icon, parent)
        
        self.settings_file = Path.home() / ".trackershield" / "settings.json"
        self.settings_file.parent.mkdir(parents=True, exist_ok=True)
        
        self.settings = self.load_settings()
        
        # Create menu
        menu = QMenu()
        
        # Show Dashboard
        show_action = QAction("Show Dashboard", self)
        show_action.triggered.connect(self.show_dashboard)
        menu.addAction(show_action)
        
        menu.addSeparator()
        
        # Status
        self.status_action = QAction("Status: Running", self)
        self.status_action.setEnabled(False)
        menu.addAction(self.status_action)
        
        # Stats
        self.stats_action = QAction("Blocked: 0 trackers", self)
        self.stats_action.setEnabled(False)
        menu.addAction(self.stats_action)
        
        menu.addSeparator()
        
        # Settings
        settings_action = QAction("Settings...", self)
        settings_action.triggered.connect(self.show_settings)
        menu.addAction(settings_action)
        
        # Check for updates
        update_action = QAction("Check for Updates", self)
        update_action.triggered.connect(self.check_updates)
        menu.addAction(update_action)
        
        menu.addSeparator()
        
        # Exit
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.exit_app)
        menu.addAction(exit_action)
        
        self.setContextMenu(menu)
        self.setToolTip("TrackerShield - Privacy Protection Active")
        
        # Show notification on startup
        self.showMessage(
            "TrackerShield Active",
            "Protecting your privacy in the background",
            QSystemTrayIcon.MessageIcon.Information,
            3000
        )
        
        # Update stats timer
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self.update_stats)
        self.stats_timer.start(5000)  # Every 5 seconds
        
        self.blocked_count = 0
    
    def load_settings(self):
        """Load settings from file"""
        if not self.settings_file.exists():
            return {
                'license_key': '',
                'auto_launch': False,
                'auto_update': True
            }
        
        try:
            with open(self.settings_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def save_settings(self):
        """Save settings to file"""
        with open(self.settings_file, 'w') as f:
            json.dump(self.settings, f, indent=2)
    
    def show_dashboard(self):
        """Open dashboard in browser"""
        import webbrowser
        webbrowser.open("http://localhost:8501")
        
        self.showMessage(
            "Dashboard Opening",
            "Opening TrackerShield dashboard in your browser",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )
    
    def show_settings(self):
        """Show settings dialog"""
        dialog = SettingsDialog()
        dialog.set_settings(self.settings)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.settings = dialog.get_settings()
            self.save_settings()
            
            self.showMessage(
                "Settings Saved",
                "Your settings have been updated",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
    
    def check_updates(self):
        """Check for signature updates"""
        from tracker_shield.updater.auto_update import DatabaseUpdater
        
        tier = 'free'  # Get from license
        if self.settings.get('license_key'):
            if self.settings['license_key'].startswith('TSGD'):
                tier = 'god'
            elif self.settings['license_key'].startswith('TSPR'):
                tier = 'pro'
        
        updater = DatabaseUpdater(tier)
        update_info = updater.check_for_updates()
        
        if update_info:
            self.showMessage(
                "Update Available!",
                f"New version {update_info['latest_version']} with +{update_info['new_signatures']} signatures",
                QSystemTrayIcon.MessageIcon.Information,
                5000
            )
        else:
            self.showMessage(
                "Up to Date",
                "You have the latest signature database",
                QSystemTrayIcon.MessageIcon.Information,
                2000
            )
    
    def update_stats(self):
        """Update statistics"""
        # In production, get real stats from addon
        self.blocked_count += 1  # Mock
        self.stats_action.setText(f"Blocked: {self.blocked_count} trackers")
    
    def exit_app(self):
        """Exit application"""
        reply = QMessageBox.question(
            None,
            "Exit TrackerShield",
            "Are you sure you want to exit? You will no longer be protected.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            QApplication.quit()


def main():
    """Run system tray app"""
    app = QApplication(sys.argv)
    
    # Don't quit when last window closes
    app.setQuitOnLastWindowClosed(False)
    
    # Create icon (use a simple colored square for now)
    # In production, use actual icon file
    from PyQt6.QtGui import QPixmap, QPainter, QColor
    pixmap = QPixmap(64, 64)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setBrush(QColor(255, 59, 59))  # Red
    painter.drawEllipse(8, 8, 48, 48)
    painter.end()
    icon = QIcon(pixmap)
    
    # Create tray
    tray = TrackerShieldTray(icon)
    tray.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
