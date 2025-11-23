"""
Reality Check - Easy Launcher with Visual Dashboard
Run this script to get the FULL visual experience with charts and timestamps!
"""

import subprocess
import time
import webbrowser
from pathlib import Path

print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║  🔥 REALITY CHECK - FULL VISUAL DASHBOARD                    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

This will launch:
1. The tracking proxy on localhost:8080
2. A FULL VISUAL DASHBOARD in your browser with:
   ✓ Live charts and graphs
   ✓ Timestamp for EVERY tracking event
   ✓ Company names and risk scores  
   ✓ Interactive network visualization
   ✓ Detailed violation timeline

""")

# Step 1: Configure browser proxy
print("═" * 60)
print("STEP 1: Configure Your Browser Proxy")
print("═" * 60)
print()
print("Open your browser settings and set:")
print("  • HTTP Proxy: localhost")
print("  • Port: 8080")
print("  • HTTPS Proxy: localhost") 
print("  • Port: 8080")
print()
print("Chrome/Edge: Settings → Search 'proxy' → Manual proxy setup")
print("Firefox: Settings → Network Settings → Manual proxy")
print()
input("Press ENTER when proxy is configured...")

# Step 2: Start the monitoring
print("\n" + "═" * 60)
print("STEP 2: Starting Reality Check Monitor...")
print("═" * 60)
print()

# Start in background without Streamlit integration
import sys
import threading
from digital_forensic_surgeon.scanners.reality_check_monitor import RealityCheckMonitor

# Create monitor
monitor = RealityCheckMonitor(proxy_port=8080)

# Start monitoring (5 minutes)
duration = 300
print(f"Duration: {duration} seconds ({duration//60} minutes)")
print()

monitor.start(duration_seconds=duration)

# Wait a bit for proxy to start
time.sleep(3)

# Step 3: Launch dashboard
print("\n" + "═" * 60)
print("STEP 3: Launching Visual Dashboard...")
print("═" * 60)
print()

dashboard_file = Path(__file__).parent / "digital_forensic_surgeon" / "dashboard" / "reality_check_dashboard.py"

print(f"Opening dashboard in browser...")
print(f"Dashboard will update every 2 seconds with live data!")
print()

# Launch streamlit dashboard
subprocess.Popen([
    sys.executable, "-m", "streamlit", "run",
    str(dashboard_file),
    "--server.headless", "false",
    "--server.port", "8501",
    "--",
    str(monitor)  # Pass monitor reference
])

print(f"✓ Dashboard launching at: http://localhost:8501")
print()
print("═" * 60)
print("READY! Now browse the web and watch the dashboard!")
print("═" * 60)
print()
print("Try visiting:")
print("  • Facebook.com")
print("  • Google.com")  
print("  • News websites")
print("  • YouTube")
print()
print("Watch the dashboard to see EVERY company tracking you in REAL-TIME!")
print()
print(f"Monitoring for {duration//60} minutes...")
print(f"Press Ctrl+C to stop early")
print()

# Wait for monitoring to complete
try:
    while monitor.is_monitoring:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n\nStopping...")
    monitor.stop()

print("\n" + "═" * 60)
print("Monitoring Complete!")
print("═" * 60)
print()
print("Check the dashboard for full results!")
print("The dashboard will stay open so you can review everything.")
print()
