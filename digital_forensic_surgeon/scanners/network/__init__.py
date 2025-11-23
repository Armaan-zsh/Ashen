"""Network scanner for Digital Forensic Surgeon."""

from __future__ import annotations

import socket
import ssl
import requests
from typing import Dict, List, Any, Optional, Generator
from datetime import datetime

from digital_forensic_surgeon.core.models import EvidenceItem, ForensicResult
from digital_forensic_surgeon.core.exceptions import ScannerError


class NetworkScanner:
    """Scanner for network activity and connections."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.timeout = 5.0
    
    def scan_active_connections(self) -> Generator[EvidenceItem, None, None]:
        """Scan for active network connections."""
        try:
            # This would typically use netstat or similar
            # For demonstration, we'll simulate some connections
            
            connections = [
                {"local": "192.168.1.100:12345", "remote": "142.250.191.14:443", "state": "ESTABLISHED"},
                {"local": "192.168.1.100:54321", "remote": "151.101.129.69:80", "state": "TIME_WAIT"},
                {"local": "192.168.1.100:34567", "remote": "13.107.4.50:443", "state": "ESTABLISHED"},
            ]
            
            for conn in connections:
                yield EvidenceItem(
                    type="network_connection",
                    source="network",
                    path=f"{conn['local']} -> {conn['remote']}",
                    content=f"Connection state: {conn['state']}",
                    metadata=conn,
                    is_sensitive=False,
                    confidence=0.9
                )
                
        except Exception as e:
            yield EvidenceItem(
                type="network_scan_error",
                source="network",
                path="active_connections",
                content=f"Failed to scan connections: {e}",
                is_sensitive=False,
                confidence=0.1
            )
    
    def scan_dns_queries(self) -> Generator[EvidenceItem, None, None]:
        """Scan DNS query history (if available)."""
        # This would typically parse DNS log files
        yield EvidenceItem(
            type="dns_query",
            source="network", 
            path="dns_cache",
            content="DNS query history",
            metadata={"queries": ["google.com", "facebook.com", "amazon.com"]},
            is_sensitive=False,
            confidence=0.7
        )
    
    def check_external_ips(self) -> Generator[EvidenceItem, None, None]:
        """Check external IP addresses and geolocation."""
        try:
            # Get public IP
            response = requests.get("https://api.ipify.org?format=json", timeout=10)
            if response.status_code == 200:
                ip_data = response.json()
                public_ip = ip_data.get('ip')
                
                yield EvidenceItem(
                    type="public_ip",
                    source="network",
                    path="public_ip",
                    content=f"Public IP: {public_ip}",
                    metadata=ip_data,
                    is_sensitive=True,
                    confidence=0.9
                )
                
                # Get geolocation
                try:
                    geo_response = requests.get(f"http://ip-api.com/json/{public_ip}", timeout=10)
                    if geo_response.status_code == 200:
                        geo_data = geo_response.json()
                        
                        yield EvidenceItem(
                            type="geolocation",
                            source="network",
                            path="geolocation",
                            content=f"Location: {geo_data.get('city', 'Unknown')}, {geo_data.get('country', 'Unknown')}",
                            metadata=geo_data,
                            is_sensitive=True,
                            confidence=0.8
                        )
                except Exception:
                    pass
                    
        except Exception as e:
            yield EvidenceItem(
                type="ip_check_error",
                source="network",
                path="external_ip_check",
                content=f"Failed to check external IP: {e}",
                is_sensitive=False,
                confidence=0.1
            )
    
    def scan_network_interfaces(self) -> Generator[EvidenceItem, None, None]:
        """Scan network interfaces."""
        import psutil
        
        try:
            interfaces = psutil.net_if_addrs()
            
            for interface_name, addresses in interfaces.items():
                for addr in addresses:
                    if addr.family == socket.AF_INET:  # IPv4
                        yield EvidenceItem(
                            type="network_interface",
                            source="network",
                            path=f"interface_{interface_name}",
                            content=f"IPv4: {addr.address}",
                            metadata={
                                "interface": interface_name,
                                "address": addr.address,
                                "netmask": addr.netmask,
                                "broadcast": addr.broadcast
                            },
                            is_sensitive=False,
                            confidence=0.9
                        )
                    elif addr.family == socket.AF_INET6:  # IPv6
                        yield EvidenceItem(
                            type="network_interface",
                            source="network",
                            path=f"interface_{interface_name}_ipv6",
                            content=f"IPv6: {addr.address}",
                            metadata={
                                "interface": interface_name,
                                "address": addr.address,
                                "netmask": addr.netmask,
                                "broadcast": addr.broadcast
                            },
                            is_sensitive=False,
                            confidence=0.9
                        )
                        
        except ImportError:
            yield EvidenceItem(
                type="missing_dependency",
                source="network",
                path="network_interfaces",
                content="psutil library required for network interface scanning",
                is_sensitive=False,
                confidence=0.0
            )
        except Exception as e:
            yield EvidenceItem(
                type="network_scan_error",
                source="network", 
                path="network_interfaces",
                content=f"Failed to scan network interfaces: {e}",
                is_sensitive=False,
                confidence=0.1
            )


def scan_network_forensic() -> ForensicResult:
    """Perform network forensic scan."""
    scanner = NetworkScanner()
    result = ForensicResult(scan_type="network")
    
    start_time = datetime.now()
    
    try:
        # Scan various network components
        yield_count = 0
        
        for evidence in scanner.scan_active_connections():
            result.add_evidence(evidence)
            yield_count += 1
        
        for evidence in scanner.scan_dns_queries():
            result.add_evidence(evidence)
            yield_count += 1
            
        for evidence in scanner.check_external_ips():
            result.add_evidence(evidence)
            yield_count += 1
            
        for evidence in scanner.scan_network_interfaces():
            result.add_evidence(evidence)
            yield_count += 1
        
        result.finalize()
        
    except Exception as e:
        result.add_error(f"Network scan failed: {e}")
        result.finalize()
    
    return result
