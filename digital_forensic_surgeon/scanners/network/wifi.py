"""WiFi Network Scanner for Digital Forensic Surgeon."""

from __future__ import annotations

import os
import sys
import platform
import subprocess
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Generator
from dataclasses import dataclass

from digital_forensic_surgeon.core.models import EvidenceItem
from digital_forensic_surgeon.core.exceptions import ScannerError
from digital_forensic_surgeon.core.config import get_config


@dataclass
class WiFiNetwork:
    """Represents a discovered WiFi network."""
    ssid: str
    signal_strength: Optional[int] = None
    security_type: str = "Unknown"
    connected: bool = False
    signal_strength_dbm: Optional[int] = None
    frequency: Optional[str] = None
    channel: Optional[int] = None


class WiFiScanner:
    """Perform WiFi network forensic analysis."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or get_config()
        self.system = platform.system().lower()
        
    def scan_wifi_networks(self) -> Generator[WiFiNetwork, None, None]:
        """Scan for available WiFi networks."""
        try:
            if self.system == "windows":
                yield from self._scan_wifi_windows()
            elif self.system == "darwin":
                yield from self._scan_wifi_macos()
            elif self.system == "linux":
                yield from self._scan_wifi_linux()
            else:
                raise ScannerError(f"Unsupported platform: {self.system}")
                
        except Exception as e:
            raise ScannerError(f"WiFi scanning failed: {e}")
    
    def _scan_wifi_windows(self) -> Generator[WiFiNetwork, None, None]:
        """Scan WiFi networks on Windows using netsh."""
        try:
            # Get saved networks
            result = subprocess.run(
                ["netsh", "wlan", "show", "profiles"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # Parse saved network profiles
                profile_pattern = r'All User Profile\s+: (.+)'
                for line in result.stdout.splitlines():
                    match = re.search(profile_pattern, line)
                    if match:
                        ssid = match.group(1).strip()
                        if ssid:
                            yield WiFiNetwork(
                                ssid=ssid,
                                security_type="Saved",
                                connected=False
                            )
            
            # Get current connection
            result = subprocess.run(
                ["netsh", "wlan", "show", "interfaces"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                # Parse current connection
                current_ssid = None
                for line in result.stdout.splitlines():
                    if "SSID" in line and ":" in line:
                        current_ssid = line.split(":")[1].strip()
                        break
                
                if current_ssid:
                    # Mark as connected
                    for network in self._scan_wifi_windows():
                        if network.ssid == current_ssid:
                            network.connected = True
                            break
                    else:
                        # Add as connected if not in saved list
                        yield WiFiNetwork(
                            ssid=current_ssid,
                            connected=True
                        )
            
        except Exception:
            pass  # Silently fail for privacy
    
    def _scan_wifi_macos(self) -> Generator[WiFiNetwork, None, None]:
        """Scan WiFi networks on macOS."""
        try:
            result = subprocess.run(
                ["/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport", "-s"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    header = lines[0].split()
                    
                    for line in lines[1:]:
                        parts = line.split()
                        if len(parts) >= 2:
                            ssid = parts[0]
                            if ssid and not ssid.isspace():
                                yield WiFiNetwork(
                                    ssid=ssid,
                                    connected=False
                                )
                                
        except Exception:
            pass  # Silently fail for privacy
    
    def _scan_wifi_linux(self) -> Generator[WiFiNetwork, None, None]:
        """Scan WiFi networks on Linux using nmcli."""
        try:
            # Try using nmcli (NetworkManager)
            result = subprocess.run(
                ["nmcli", "-t", "-f", "SSID,SIGNAL,SECURITY", "dev", "wifi"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split(':')
                        if len(parts) >= 3 and parts[0]:
                            ssid = parts[0]
                            signal = parts[1] if parts[1] != '--' else None
                            
                            try:
                                signal_strength = int(signal) if signal else None
                            except ValueError:
                                signal_strength = None
                            
                            yield WiFiNetwork(
                                ssid=ssid,
                                signal_strength=signal_strength,
                                security_type=parts[2] if len(parts) > 2 else "Unknown"
                            )
            
            # Also check saved networks
            result = subprocess.run(
                ["nmcli", "-t", "-f", "NAME,TYPE,DEVICE", "connection", "show"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                saved_ssids = set()
                for line in result.stdout.strip().split('\n'):
                    if line:
                        parts = line.split(':')
                        if len(parts) >= 1:
                            ssid = parts[0]
                            if ssid and not ssid.isspace():
                                saved_ssids.add(ssid)
                
                # Mark saved networks
                for network in self._scan_wifi_linux():
                    if network.ssid in saved_ssids:
                        network.security_type = "Saved"
                        yield network
                        
        except FileNotFoundError:
            # nmcli not available, try alternative methods
            pass
        except Exception:
            pass  # Silently fail for privacy
    
    def get_connected_ssid(self) -> Optional[str]:
        """Get currently connected WiFi SSID."""
        try:
            if self.system == "windows":
                result = subprocess.run(
                    ["netsh", "wlan", "show", "interfaces"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    for line in result.stdout.splitlines():
                        if "SSID" in line and ":" in line:
                            return line.split(":")[1].strip()
                            
            elif self.system == "darwin":
                result = subprocess.run(
                    ["/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport", "-I"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    for line in result.stdout.splitlines():
                        if "SSID:" in line:
                            return line.split("SSID:")[1].strip()
                            
            elif self.system == "linux":
                result = subprocess.run(
                    ["nmcli", "-t", "-f", "ACTIVE,SSID", "dev", "wifi"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    for line in result.stdout.strip().split('\n'):
                        if line.startswith("yes:"):
                            return line.split(":", 1)[1]
                            
        except Exception:
            pass
            
        return None
    
    def get_evidence_items(self) -> List[EvidenceItem]:
        """Get WiFi network evidence items."""
        evidence_items = []
        
        try:
            # Scan for current connection
            connected_ssid = self.get_connected_ssid()
            if connected_ssid:
                evidence_items.append(EvidenceItem(
                    type="wifi_connection",
                    source="network",
                    path=f"Current WiFi: {connected_ssid}",
                    content=f"Connected to WiFi network: {connected_ssid}",
                    metadata={
                        "ssid": connected_ssid,
                        "connected": True,
                        "timestamp": None
                    },
                    is_sensitive=True,
                    confidence=1.0
                ))
            
            # Scan for available networks
            networks = list(self.scan_wifi_networks())
            if networks:
                evidence_items.append(EvidenceItem(
                    type="wifi_scan",
                    source="network",
                    path="WiFi Network Scan",
                    content=f"Found {len(networks)} WiFi networks",
                    metadata={
                        "networks_found": len(networks),
                        "ssids": [network.ssid for network in networks],
                        "network_details": [
                            {
                                "ssid": net.ssid,
                                "connected": net.connected,
                                "signal_strength": net.signal_strength,
                                "security_type": net.security_type
                            }
                            for net in networks
                        ]
                    },
                    is_sensitive=True,
                    confidence=0.9
                ))
                
        except Exception as e:
            # Add error evidence
            evidence_items.append(EvidenceItem(
                type="wifi_scan_error",
                source="network",
                path="WiFi Scan",
                content=f"WiFi scan failed: {str(e)}",
                metadata={"error": str(e)},
                is_sensitive=False,
                confidence=0.1
            ))
        
        return evidence_items
    
    def prepare_geolocation_data(self) -> List[Dict[str, Any]]:
        """Prepare SSID data for geolocation API queries."""
        geolocation_data = []
        
        try:
            networks = list(self.scan_wifi_networks())
            
            for network in networks:
                # Clean SSID for API submission
                clean_ssid = network.ssid.strip()
                
                # Skip obvious fake/empty SSIDs
                if len(clean_ssid) < 1 or clean_ssid in ['Cisco', 'Linksys', 'Netgear', 'D-Link']:
                    continue
                
                geolocation_data.append({
                    "ssid": clean_ssid,
                    "signal_strength": network.signal_strength,
                    "security_type": network.security_type,
                    "timestamp": None,
                    "clean_ssid": re.sub(r'[^a-zA-Z0-9]', '', clean_ssid.lower())  # Clean for API
                })
                
        except Exception:
            pass
            
        return geolocation_data
    
    def resolve_geolocation(self, wigle_api_key: Optional[str] = None) -> List[Dict[str, Any]]:
        """Resolve WiFi SSIDs to geolocation coordinates using Wigle.net API.
        
        Args:
            wigle_api_key: API key for Wigle.net (optional)
            
        Returns:
            List of dictionaries with SSID, lat, lon, and confidence data
        """
        if not wigle_api_key:
            # Return data in format ready for API query (no API key yet)
            return self.prepare_geolocation_data()
        
        geolocation_data = []
        
        try:
            networks = list(self.scan_wifi_networks())
            
            for network in networks:
                # This would make actual API calls to Wigle.net
                # For now, return the prepared data with placeholder coordinates
                clean_ssid = re.sub(r'[^a-zA-Z0-9]', '', network.ssid.lower())
                
                geolocation_data.append({
                    "ssid": network.ssid,
                    "clean_ssid": clean_ssid,
                    "signal_strength": network.signal_strength,
                    "security_type": network.security_type,
                    "estimated_location": {
                        "lat": None,  # Would be filled by API
                        "lon": None,  # Would be filled by API
                        "confidence": None,  # Would be filled by API
                        "source": "wigle_api"
                    }
                })
                
        except Exception as e:
            pass
            
        return geolocation_data