"""
TrackerShield Master Launcher
ONE command to start EVERYTHING together
"""

import subprocess
import sys
import time
from pathlib import Path
import webbrowser

def check_dependencies():
    """Check if all dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    required = ['streamlit', 'mitmproxy', 'PyQt6']
    missing = []
    
    for package in required:
        try:
            __import__(package.lower().replace('pyqt6', 'PyQt6'))
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - MISSING")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing packages: {', '.join(missing)}")
        print(f"\nInstall with:")
        print(f"   pip install {' '.join(missing)}")
        return False
    
    return True

def start_trackershield():
    """Start complete TrackerShield system"""
    
    print("=" * 70)
    print("🛡️  TRACKERSHIELD UNIFIED LAUNCHER")
    print("=" * 70)
    
    if not check_dependencies():
        print("\n❌ Missing dependencies. Install them first.")
        return
    
    print("\n🚀 Starting TrackerShield components...\n")
    
    processes = []
    
    # 1. Start Integration Manager (in background)
    print("1️⃣  Starting Integration Manager...")
    try:
        from tracker_shield.integration.manager import IntegrationManager
        manager = IntegrationManager()
        manager.start()
        print("   ✅ Integration Manager running")
    except Exception as e:
        print(f"   ⚠️  Integration Manager: {e}")
    
    time.sleep(1)
    
    # 2. Start Dashboard
    print("\n2️⃣  Starting Dashboard...")
    try:
        dashboard_process = subprocess.Popen(
            [sys.executable, '-m', 'streamlit', 'run', 'enhanced_dashboard.py',
             '--server.headless', 'true'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        processes.append(('Dashboard', dashboard_process))
        print("   ✅ Dashboard starting on http://localhost:8501")
        time.sleep(3)
    except Exception as e:
        print(f"   ❌ Dashboard failed: {e}")
    
    # 3. Start System Tray (if PyQt6 available)
    print("\n3️⃣  Starting System Tray...")
    try:
        tray_process = subprocess.Popen(
            [sys.executable, 'tracker_shield_tray.py'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        processes.append(('System Tray', tray_process))
        print("   ✅ System Tray icon active")
    except Exception as e:
        print(f"   ⚠️  System Tray: {e}")
    
    time.sleep(2)
    
    # 4. Open Dashboard in browser
    print("\n4️⃣  Opening Dashboard...")
    try:
        webbrowser.open('http://localhost:8501')
        print("   ✅ Browser opened")
    except Exception as e:
        print(f"   ⚠️  Browser: {e}")
    
    # Summary
    print("\n" + "=" * 70)
    print("✅ TRACKERSHIELD IS NOW RUNNING!")
    print("=" * 70)
    print("\n📊 Components:")
    print("   • Integration Manager: Running")
    print("   • Dashboard: http://localhost:8501")
    print("   • System Tray: Check your taskbar")
    print("   • Event Bus: Connected")
    
    print("\n💡 Usage:")
    print("   • Click system tray icon for quick menu")
    print("   • Use dashboard for detailed stats")
    print("   • All components are connected via event bus")
    
    print("\n🛑 To stop: Press Ctrl+C or exit from system tray")
    print("=" * 70)
    
    # Keep running
    try:
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            for name, process in processes:
                if process.poll() is not None:
                    print(f"\n⚠️  {name} stopped unexpectedly")
    
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down TrackerShield...")
        
        for name, process in processes:
            try:
                process.terminate()
                print(f"   ✅ Stopped {name}")
            except:
                pass
        
        print("\n✅ TrackerShield stopped.\n")

if __name__ == '__main__':
    start_trackershield()
