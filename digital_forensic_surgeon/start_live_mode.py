"""
One-Command Startup
Starts proxy + dashboard together
"""

import subprocess
import sys
import time
import threading
from pathlib import Path

def setup_certificate():
    """Generate and install mitmproxy certificate"""
    print("🔐 Setting up SSL certificate...")
    
    cert_dir = Path.home() / ".mitmproxy"
    cert_file = cert_dir / "mitmproxy-ca-cert.pem"
    
    if not cert_file.exists():
        print("📝 Generating certificate (first time only)...")
        # Run mitmdump briefly to generate cert
        proc = subprocess.Popen(
            ["mitmdump", "--version"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        proc.wait()
        time.sleep(1)
    
    if cert_file.exists():
        print(f"✅ Certificate ready: {cert_file}")
        
        # On Windows, try to install automatically
        if sys.platform == "win32":
            print("\n💡 To enable HTTPS interception:")
            print(f"   1. Double-click: {cert_file}")
            print("   2. Install → Local Machine → Trusted Root CA")
            print("   3. Restart browsers\n")
        
        return True
    else:
        print("❌ Certificate generation failed")
        return False

def start_proxy():
    """Start proxy in background"""
    print("🚀 Starting proxy on port 8080...")
    
    addon_script = Path(__file__).parent / "digital_forensic_surgeon" / "interceptor" / "tracker_addon.py"
    
    cmd = [
        "mitmdump",
        "-p", "8080",
        "-s", str(addon_script),
        "--set", "block_global=false",
        "--ssl-insecure"
    ]
    
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    time.sleep(2)
    
    if proc.poll() is None:
        print("✅ Proxy running on http://localhost:8080")
        return proc
    else:
        print("❌ Proxy failed to start")
        return None

def start_dashboard():
    """Start Streamlit dashboard"""
    print("🎨 Starting dashboard on port 8501...")
    
    cmd = [
        sys.executable,
        "-m", "streamlit", "run",
        "reality_check_dashboard.py",
        "--server.port=8501"
    ]
    
    proc = subprocess.Popen(cmd)
    
    print("✅ Dashboard starting at http://localhost:8501")
    return proc

def main():
    """Start everything"""
    
    print("=" * 70)
    print("  🔬 DIGITAL FORENSIC SURGEON - LIVE MODE")
    print("=" * 70)
    print()
    
    # Setup certificate
    if not setup_certificate():
        return
    
    # Start proxy
    proxy_proc = start_proxy()
    if not proxy_proc:
        return
    
    # Start dashboard
    dashboard_proc = start_dashboard()
    
    print()
    print("=" * 70)
    print("  ✅ READY!")
    print("=" * 70)
    print()
    print("  📊 Dashboard: http://localhost:8501")
    print("  🌐 Proxy: localhost:8080")
    print()
    print("  💡 Configure browser to use proxy:")
    print("     Settings → Proxy → Manual → localhost:8080")
    print()
    print("  Press Ctrl+C to stop everything...")
    print()
    
    try:
        # Wait for Ctrl+C
        dashboard_proc.wait()
    except KeyboardInterrupt:
        print("\n⚠️ Stopping...")
        proxy_proc.terminate()
        dashboard_proc.terminate()
        print("✅ Stopped")

if __name__ == "__main__":
    main()
