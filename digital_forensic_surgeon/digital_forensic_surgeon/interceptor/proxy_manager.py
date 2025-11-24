"""
mitmproxy Manager
Handles starting/stopping the proxy and filtering traffic
"""

import subprocess
import sys
import os
import signal
from pathlib import Path
from typing import Optional
import threading
import time

class ProxyManager:
    """Manages mitmproxy lifecycle"""
    
    def __init__(self, port: int = 8080):
        self.port = port
        self.process: Optional[subprocess.Popen] = None
        self.addon_script = Path(__file__).parent / "tracker_addon.py"
        
    def start(self):
        """Start mitmproxy with tracker addon"""
        
        if self.process and self.process.poll() is None:
            print("⚠️ Proxy already running")
            return
        
        print(f"🚀 Starting mitmproxy on port {self.port}...")
        
        # Run mitmproxy with our addon
        cmd = [
            "mitmdump",
            "-p", str(self.port),
            "-s", str(self.addon_script),
            "--set", "block_global=false",
            "--ssl-insecure"  # Allow inspecting HTTPS
        ]
        
        try:
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait a bit for startup
            time.sleep(2)
            
            if self.process.poll() is None:
                print(f"✅ Proxy started on http://localhost:{self.port}")
                print(f"📊 Intercepting traffic with addon: {self.addon_script}")
                
                # Start log reader thread
                threading.Thread(target=self._read_logs, daemon=True).start()
            else:
                stdout, stderr = self.process.communicate()
                print(f"❌ Failed to start proxy:")
                print(stderr)
                
        except FileNotFoundError:
            print("❌ mitmproxy not found! Install with: pip install mitmproxy")
        except Exception as e:
            print(f"❌ Error starting proxy: {e}")
    
    def stop(self):
        """Stop the proxy"""
        
        if not self.process or self.process.poll() is not None:
            print("⚠️ Proxy not running")
            return
        
        print("🛑 Stopping proxy...")
        
        try:
            self.process.terminate()
            self.process.wait(timeout=5)
            print("✅ Proxy stopped")
        except subprocess.TimeoutExpired:
            print("⚠️ Force killing proxy...")
            self.process.kill()
            print("✅ Proxy killed")
        
        self.process = None
    
    def is_running(self) -> bool:
        """Check if proxy is running"""
        return self.process is not None and self.process.poll() is None
    
    def _read_logs(self):
        """Read and display proxy logs"""
        if not self.process:
            return
            
        for line in self.process.stdout:
            if "TRACKER" in line:  # Only show tracker-related logs
                print(f"📡 {line.strip()}")
    
    def configure_system_proxy(self, enable: bool = True):
        """Configure Windows to use this proxy"""
        
        if sys.platform != "win32":
            print("⚠️ System proxy configuration only supported on Windows")
            return
        
        proxy_server = f"localhost:{self.port}" if enable else ""
        
        # Set Windows proxy via registry
        import winreg
        
        internet_settings = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
            0,
            winreg.KEY_WRITE
        )
        
        if enable:
            winreg.SetValueEx(internet_settings, "ProxyEnable", 0, winreg.REG_DWORD, 1)
            winreg.SetValueEx(internet_settings, "ProxyServer", 0, winreg.REG_SZ, proxy_server)
            print(f"✅ System proxy enabled: {proxy_server}")
        else:
            winreg.SetValueEx(internet_settings, "ProxyEnable", 0, winreg.REG_DWORD, 0)
            print("✅ System proxy disabled")
        
        winreg.CloseKey(internet_settings)


if __name__ == "__main__":
    # Test the proxy
    manager = ProxyManager()
    
    try:
        manager.start()
        manager.configure_system_proxy(enable=True)
        
        print("\n💡 Proxy running! Press Ctrl+C to stop...")
        
        while manager.is_running():
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n⚠️ Stopping...")
    finally:
        manager.configure_system_proxy(enable=False)
        manager.stop()
