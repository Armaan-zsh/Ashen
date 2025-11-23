"""
MITMProxy Manager for Reality Check
Manages mitmproxy instance for HTTPS traffic inspection and tracking detection
"""

import os
import sys
import subprocess
import threading
import time
import queue
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from urllib.parse import urlparse
import json

from mitmproxy import http, options
from mitmproxy.tools import cmdline
from mitmproxy.tools.dump import DumpMaster

from .data_broker_database import DataBrokerDatabase


class TrackingEvent:
    """Represents a tracking/privacy violation event"""
    def __init__(self, timestamp: datetime, url: str, method: str,
                 entity_name: str, category: str, risk_score: float,
                 request_headers: Dict[str, str], cookies: List[str],
                 tracking_type: str, data_sent: Dict[str, Any] = None):
        self.timestamp = timestamp
        self.url = url
        self.method = method
        self.entity_name = entity_name
        self.category = category
        self.risk_score = risk_score
        self.request_headers = request_headers
        self.cookies = cookies
        self.tracking_type = tracking_type
        self.data_sent = data_sent or {}
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "url": self.url,
            "method": self.method,
            "entity_name": self.entity_name,
            "category": self.category,
            "risk_score": self.risk_score,
            "request_headers": self.request_headers,
            "cookies": self.cookies,
            "tracking_type": self.tracking_type,
            "data_sent": self.data_sent
        }


class TrackingAddon:
    """mitmproxy addon for tracking detection"""
    
    def __init__(self, event_queue: queue.Queue, broker_db: DataBrokerDatabase):
        self.event_queue = event_queue
        self.broker_db = broker_db
        self.request_count = 0
        self.tracker_count = 0
    
    def request(self, flow: http.HTTPFlow) -> None:
        """Process each HTTP request"""
        self.request_count += 1
        
        url = flow.request.pretty_url
        parsed = urlparse(url)
        domain = parsed.netloc
        
        # Check if this is a tracker
        classification = self.broker_db.classify_url(url)
        
        if classification["is_tracker"]:
            self.tracker_count += 1
            
            # Extract cookies
            cookies = []
            if "cookie" in flow.request.headers:
                cookie_header = flow.request.headers["cookie"]
                cookies = [c.strip() for c in cookie_header.split(";")]
            
            # Determine tracking type
            tracking_type = self._determine_tracking_type(flow, classification)
            
            # Extract potentially sensitive data
            data_sent = self._extract_sensitive_data(flow)
            
            # Create tracking event
            event = TrackingEvent(
                timestamp=datetime.now(),
                url=url,
                method=flow.request.method,
                entity_name=classification["entity_name"],
                category=classification["category"],
                risk_score=classification["risk_score"],
                request_headers=dict(flow.request.headers),
                cookies=cookies,
                tracking_type=tracking_type,
                data_sent=data_sent
            )
            
            # Queue the event
            try:
                self.event_queue.put_nowait(event)
            except queue.Full:
                # Queue full, remove oldest and try again
                try:
                    self.event_queue.get_nowait()
                    self.event_queue.put_nowait(event)
                except:
                    pass
    
    def _determine_tracking_type(self, flow: http.HTTPFlow, classification: Dict[str, Any]) -> str:
        """Determine the type of tracking"""
        url = flow.request.pretty_url.lower()
        category = classification["category"]
        
        # Tracking pixel
        if ("/tr" in url or "/pixel" in url or "/beacon" in url or
            "1x1" in url or flow.request.path.endswith((".gif", ".png")) and "tracking" in url):
            return "Tracking Pixel"
        
        # Analytics
        if category == "Analytics" or "analytics" in url or "stats" in url:
            return "Analytics"
        
        # Ad Network
        if category == "Ad Network" or "ad" in url or "doubleclick" in url:
            return "Ad Tracking"
        
        # Social tracking
        if category == "Social Tracking":
            return "Social Media Tracking"
        
        # Fingerprinting
        if category == "Fingerprinting" or "fingerprint" in url:
            return "Device Fingerprinting"
        
        # Third-party cookie
        if flow.request.headers.get("cookie"):
            return "Third-Party Cookie"
        
        return "Unknown Tracker"
    
    def _extract_sensitive_data(self, flow: http.HTTPFlow) -> Dict[str, Any]:
        """Extract potentially sensitive data from request"""
        data = {
            "has_cookies": bool(flow.request.headers.get("cookie")),
            "has_referrer": bool(flow.request.headers.get("referer")),
            "user_agent": flow.request.headers.get("user-agent", ""),
            "content_length": flow.request.headers.get("content-length", 0)
        }
        
        # Check for form data or JSON payload
        if flow.request.content:
            try:
                content_type = flow.request.headers.get("content-type", "")
                if "json" in content_type.lower():
                    try:
                        payload = json.loads(flow.request.content.decode('utf-8', errors='ignore'))
                        data["json_keys"] = list(payload.keys()) if isinstance(payload, dict) else []
                    except:
                        pass
                elif "form" in content_type.lower():
                    data["has_form_data"] = True
            except:
                pass
        
        return data


class MITMProxyManager:
    """Manages mitmproxy for traffic inspection"""
    
    def __init__(self, port: int = 8080):
        self.port = port
        self.proxy_thread = None
        self.master = None
        self.is_running = False
        self.event_queue = queue.Queue(maxsize=10000)
        self.broker_db = DataBrokerDatabase()
        self.addon = None
        self.stats = {
            "start_time": None,
            "total_requests": 0,
            "total_trackers": 0,
            "unique_trackers": set()
        }
    
    def start(self):
        """Start the mitmproxy in background"""
        if self.is_running:
            print("[Reality Check] Proxy already running")
            return
        
        print(f"[Reality Check] Starting mitmproxy on port {self.port}...")
        
        self.is_running = True
        self.stats["start_time"] = datetime.now()
        
        # Start proxy in background thread
        self.proxy_thread = threading.Thread(target=self._run_proxy, daemon=True)
        self.proxy_thread.start()
        
        # Wait for startup
        time.sleep(2)
        
        print(f"[Reality Check] ✓ Proxy started on http://localhost:{self.port}")
        print(f"[Reality Check] Configure your browser to use proxy: localhost:{self.port}")
    
    def _run_proxy(self):
        """Run mitmproxy in this thread"""
        try:
            # Configure mitmproxy options
            opts = options.Options(listen_host='127.0.0.1', listen_port=self.port)
            opts.update(
                ssl_insecure=True,  # Don't verify upstream certs (for testing)
            )
            
            # Create addon
            self.addon = TrackingAddon(self.event_queue, self.broker_db)
            
            # Create and run master
            self.master = DumpMaster(opts)
            self.master.addons.add(self.addon)
            
            # Run the proxy
            self.master.run()
            
        except Exception as e:
            print(f"[Reality Check] Proxy error: {e}")
            self.is_running = False
    
    def stop(self):
        """Stop the mitmproxy"""
        if not self.is_running:
            return
        
        print("[Reality Check] Stopping proxy...")
        
        self.is_running = False
        
        if self.master:
            self.master.shutdown()
        
        if self.proxy_thread and self.proxy_thread.is_alive():
            self.proxy_thread.join(timeout=5)
        
        print("[Reality Check] ✓ Proxy stopped")
    
    def get_events(self, max_events: int = 100) -> List[TrackingEvent]:
        """Get tracking events from the queue"""
        events = []
        
        try:
            while len(events) < max_events:
                event = self.event_queue.get_nowait()
                events.append(event)
                
                # Update stats
                self.stats["total_trackers"] += 1
                self.stats["unique_trackers"].add(event.entity_name)
                
        except queue.Empty:
            pass
        
        return events
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current statistics"""
        runtime = (datetime.now() - self.stats["start_time"]).total_seconds() if self.stats["start_time"] else 0
        
        return {
            "is_running": self.is_running,
            "runtime_seconds": runtime,
            "total_requests": self.addon.request_count if self.addon else 0,
            "total_trackers": self.addon.tracker_count if self.addon else 0,
            "unique_trackers": len(self.stats["unique_trackers"]),
            "trackers_per_minute": (self.addon.tracker_count / (runtime / 60)) if runtime > 0 and self.addon else 0,
            "tracker_names": list(self.stats["unique_trackers"])
        }
    
    def install_certificate(self):
        """Install mitmproxy root certificate"""
        print("\n" + "="*60)
        print("  REALITY CHECK - Certificate Installation")
        print("="*60)
        print()
        print("To inspect HTTPS traffic, you need to install mitmproxy's")
        print("root certificate. This is a ONE-TIME setup.")
        print()
        print("Steps:")
        print("  1. Start the proxy (it will be started automatically)")
        print("  2. Open your browser and visit: http://mitm.it")
        print("  3. Click on your OS (Windows/Mac/Linux)")
        print("  4. Download and install the certificate")
        print("  5. Trust the certificate when prompted")
        print()
        print("This is the SAME process used by professional tools like")
        print("GlassWire, Charles Proxy, and Fiddler.")
        print()
        print("="*60)
        
        # Check if cert already exists
        cert_path = Path.home() / ".mitmproxy" / "mitmproxy-ca-cert.pem"
        
        if cert_path.exists():
            print(f"\n✓ Certificate found at: {cert_path}")
            print("  If you've already installed it in your browser, you're all set!")
        else:
            print("\n⚠ Certificate not generated yet.")
            print("  It will be created when you start the proxy for the first time.")
        
        print("\nPress ENTER to continue...")
        input()
    
    def configure_system_proxy(self, enable: bool = True):
        """Configure system-wide proxy settings (Windows)"""
        if sys.platform != "win32":
            print("[Reality Check] System proxy configuration only supported on Windows")
            return
        
        try:
            import winreg
            
            internet_settings = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r'Software\Microsoft\Windows\CurrentVersion\Internet Settings',
                0, winreg.KEY_ALL_ACCESS
            )
            
            if enable:
                # Enable proxy
                winreg.SetValueEx(internet_settings, 'ProxyEnable', 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(internet_settings, 'ProxyServer', 0, winreg.REG_SZ, f'http://127.0.0.1:{self.port}')
                print(f"[Reality Check] ✓ System proxy enabled: localhost:{self.port}")
            else:
                # Disable proxy
                winreg.SetValueEx(internet_settings, 'ProxyEnable', 0, winreg.REG_DWORD, 0)
                print("[Reality Check] ✓ System proxy disabled")
            
            winreg.CloseKey(internet_settings)
            
            # Refresh settings
            import ctypes
            internet_set_option = ctypes.windll.Wininet.InternetSetOptionW
            internet_set_option(0, 39, 0, 0)  # INTERNET_OPTION_SETTINGS_CHANGED
            internet_set_option(0, 37, 0, 0)  # INTERNET_OPTION_REFRESH
            
        except Exception as e:
            print(f"[Reality Check] Failed to configure system proxy: {e}")
            print("               Manual configuration required")
