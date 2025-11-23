"""
Deep Packet Inspection and Network Traffic Analysis
Provides detailed analysis of network data flows, content classification, and destination intelligence
"""

import re
import json
import time
import socket
import struct
import subprocess
from typing import Dict, List, Any, Optional, Tuple, Generator
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

try:
    import scapy.all as scapy
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False

from ..core.models import EvidenceItem, ScannerType
from ..core.config import ForensicConfig
from .base import BaseScanner

@dataclass
class NetworkConnection:
    """Represents a network connection with detailed metadata"""
    protocol: str
    local_addr: str
    local_port: int
    remote_addr: str
    remote_port: int
    status: str
    pid: int
    process_name: str
    timestamp: datetime
    data_sent: int = 0
    data_received: int = 0

@dataclass
class DataPacket:
    """Represents a captured data packet with content analysis"""
    timestamp: datetime
    source_ip: str
    dest_ip: str
    source_port: int
    dest_port: int
    protocol: str
    size: int
    payload: bytes
    content_type: str
    risk_level: str
    pii_detected: List[str]
    destinations: List[str]

@dataclass
class DataFlow:
    """Represents a complete data flow between source and destination"""
    source_app: str
    destination_domain: str
    destination_ip: str
    protocol: str
    total_bytes: int
    packet_count: int
    duration: float
    content_types: List[str]
    risk_score: float
    data_categories: List[str]
    first_seen: datetime
    last_seen: datetime

class PacketDataAnalyzer(BaseScanner):
    """Advanced packet analysis for deep network inspection."""
    
    def __init__(self, config: Optional[ForensicConfig] = None):
        super().__init__(ScannerType.PACKET_ANALYZER, config)
        self.connections: Dict[str, NetworkConnection] = {}
        self.data_flows: Dict[str, DataFlow] = {}
        self.captured_packets: List[DataPacket] = []
        self.pii_patterns = self._init_pii_patterns()
        self.risky_domains = self._init_risky_domains()
        
    def scan(self) -> Generator[EvidenceItem, None, None]:
        """Main scan method for packet analysis."""
        yield from self.scan_active_connections()
        yield from self.analyze_traffic_patterns()
    
    def _init_pii_patterns(self) -> Dict[str, re.Pattern]:
        """Initialize regex patterns for PII detection"""
        return {
            'email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'phone': re.compile(r'\b\d{3}-\d{3}-\d{4}\b|\b\(\d{3}\)\s*\d{3}-\d{4}\b'),
            'ssn': re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
            'credit_card': re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'),
            'ip_address': re.compile(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'),
            'name': re.compile(r'\b[A-Z][a-z]+\s[A-Z][a-z]+\b'),
            'address': re.compile(r'\b\d+\s+[A-Z][a-z]+\s+(Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln)\b'),
            'license_plate': re.compile(r'\b[A-Z]{2,3}\s*\d{3,4}\b'),
            'passport': re.compile(r'\b[A-Z]{1,2}\d{7,9}\b'),
            'bank_account': re.compile(r'\b\d{8,17}\b'),
        }
    
    def _init_risky_domains(self) -> Dict[str, str]:
        """Initialize known risky domains and their risk categories"""
        return {
            'facebook.com': 'social_tracking',
            'google-analytics.com': 'analytics_tracking',
            'googleads.g.doubleclick.net': 'ad_tracking',
            'doubleclick.net': 'ad_tracking',
            'googlesyndication.com': 'ad_tracking',
            'googleadservices.com': 'ad_tracking',
            'facebook.tr': 'social_tracking',
            'connect.facebook.net': 'social_tracking',
            'analytics.twitter.com': 'analytics_tracking',
            'google.com': 'data_collection',
            'amazonaws.com': 'cloud_storage',
            'cloudflare.com': 'cdn_security',
            'fastly.net': 'cdn_performance',
            'segment.io': 'analytics_tracking',
            'mixpanel.com': 'analytics_tracking',
            'hotjar.com': 'user_tracking',
            'fullstory.com': 'user_tracking',
            'optimizely.com': 'a_b_testing',
            'chartbeat.com': 'analytics_tracking',
            'quantserve.com': 'analytics_tracking',
            'scorecardresearch.com': 'analytics_tracking',
            'taboola.com': 'ad_tracking',
            'outbrain.com': 'ad_tracking',
            'rubiconproject.com': 'ad_tracking',
            'pubmatic.com': 'ad_tracking',
            'indexww.com': 'ad_tracking',
            'criteo.com': 'ad_tracking',
            'adnxs.com': 'ad_tracking',
            'adsystem.com': 'ad_tracking',
        }
    
    def scan_active_connections(self) -> Generator[EvidenceItem, None, None]:
        """Scan for active network connections with detailed analysis"""
        if not PSUTIL_AVAILABLE:
            yield EvidenceItem(
                id="conn_scan_error",
                source="network_scanner",
                type="error",
                content="psutil not available for connection scanning",
                metadata={"error": "psutil_not_installed"}
            )
            return
        
        try:
            connections = psutil.net_connections(kind='inet')
            processes = {p.pid: p.info for p in psutil.process_iter(['pid', 'name'])}
            
            for conn in connections:
                if conn.status == 'ESTABLISHED':
                    pid = conn.pid or 0
                    process_info = processes.get(pid, {'name': 'unknown'})
                    
                    network_conn = NetworkConnection(
                        protocol=conn.type.name if conn.type else 'unknown',
                        local_addr=conn.laddr.ip if conn.laddr else 'unknown',
                        local_port=conn.laddr.port if conn.laddr else 0,
                        remote_addr=conn.raddr.ip if conn.raddr else 'unknown',
                        remote_port=conn.raddr.port if conn.raddr else 0,
                        status=conn.status,
                        pid=pid,
                        process_name=process_info.get('name', 'unknown'),
                        timestamp=datetime.now()
                    )
                    
                    conn_key = f"{network_conn.local_addr}:{network_conn.local_port}-{network_conn.remote_addr}:{network_conn.remote_port}"
                    self.connections[conn_key] = network_conn
                    
                    risk_level = self._assess_connection_risk(network_conn)
                    
                    yield EvidenceItem(
                        id=f"network_connection_{conn_key}",
                        source="network_scanner",
                        type="network_connection",
                        content=f"Active connection: {network_conn.process_name} -> {network_conn.remote_addr}:{network_conn.remote_port}",
                        path=f"{network_conn.local_addr}:{network_conn.local_port}",
                        metadata=asdict(network_conn)
                    )
                    
        except Exception as e:
            yield EvidenceItem(
                id="conn_scan_error",
                source="network_scanner",
                type="error",
                content=f"Error scanning connections: {str(e)}",
                metadata={"error": str(e)}
            )
    
    def analyze_traffic_patterns(self) -> Generator[EvidenceItem, None, None]:
        """Analyze network traffic patterns and data flows"""
        if not SCAPY_AVAILABLE:
            yield EvidenceItem(
                id="traffic_analysis_error",
                source="network_scanner",
                type="error",
                content="scapy not available for traffic analysis",
                metadata={"error": "scapy_not_installed"}
            )
            return
        
        try:
            # Get network interfaces
            interfaces = scapy.get_if_list()
            
            for interface in interfaces[:3]:  # Limit to first 3 interfaces
                try:
                    # Capture packets for 10 seconds
                    packets = scapy.sniff(iface=interface, timeout=10, count=100)
                    
                    for packet in packets:
                        analysis = self._analyze_packet(packet)
                        if analysis:
                            yield analysis
                            
                except Exception as e:
                    yield EvidenceItem(
                        id=f"interface_error_{interface}",
                        source="network_scanner",
                        type="error",
                        content=f"Error capturing on {interface}: {str(e)}",
                        metadata={"interface": interface, "error": str(e)}
                    )
                    
        except Exception as e:
            yield EvidenceItem(
                id="traffic_analysis_error",
                source="network_scanner",
                type="error",
                content=f"Error in traffic analysis: {str(e)}",
                metadata={"error": str(e)}
            )
    
    def _analyze_packet(self, packet) -> Optional[EvidenceItem]:
        """Analyze individual packet for content and destinations"""
        try:
            if packet.haslayer(scapy.IP):
                ip_layer = packet[scapy.IP]
                src_ip = ip_layer.src
                dst_ip = ip_layer.dst
                
                # Determine protocol
                protocol = "unknown"
                payload = b""
                
                if packet.haslayer(scapy.TCP):
                    protocol = "TCP"
                    payload = bytes(packet[scapy.TCP].payload)
                elif packet.haslayer(scapy.UDP):
                    protocol = "UDP"
                    payload = bytes(packet[scapy.UDP].payload)
                
                # Analyze payload for PII
                pii_detected = []
                payload_str = payload.decode('utf-8', errors='ignore')
                
                for pii_type, pattern in self.pii_patterns.items():
                    matches = pattern.findall(payload_str)
                    if matches:
                        pii_detected.extend(matches)
                
                # Determine content type
                content_type = self._classify_content(payload_str)
                
                # Assess risk level
                risk_level = self._assess_packet_risk(src_ip, dst_ip, payload_str, pii_detected)
                
                # Extract destinations
                destinations = self._extract_destinations(payload_str)
                
                packet_data = DataPacket(
                    timestamp=datetime.now(),
                    source_ip=src_ip,
                    dest_ip=dst_ip,
                    source_port=packet[scapy.TCP].sport if packet.haslayer(scapy.TCP) else packet[scapy.UDP].sport if packet.haslayer(scapy.UDP) else 0,
                    dest_port=packet[scapy.TCP].dport if packet.haslayer(scapy.TCP) else packet[scapy.UDP].dport if packet.haslayer(scapy.UDP) else 0,
                    protocol=protocol,
                    size=len(payload),
                    payload=payload,
                    content_type=content_type,
                    risk_level=risk_level,
                    pii_detected=pii_detected,
                    destinations=destinations
                )
                
                self.captured_packets.append(packet_data)
                
                return EvidenceItem(
                    id=f"packet_{src_ip}_{dst_ip}_{int(time.time())}",
                    source="packet_analyzer",
                    type="network_packet",
                    content=f"Packet: {src_ip} -> {dst_ip} ({protocol}, {len(payload)} bytes)",
                    metadata=asdict(packet_data)
                )
                
        except Exception as e:
            return EvidenceItem(
                id="packet_analysis_error",
                source="packet_analyzer",
                type="error",
                content=f"Error analyzing packet: {str(e)}",
                metadata={"error": str(e)}
            )
        
        return None
    
    def _classify_content(self, payload_str: str) -> str:
        """Classify the content type of packet payload"""
        content_types = []
        
        # Check for HTTP requests
        if payload_str.startswith(('GET ', 'POST ', 'PUT ', 'DELETE ', 'HEAD ')):
            content_types.append('http_request')
        
        # Check for JSON
        if payload_str.strip().startswith('{') and payload_str.strip().endswith('}'):
            content_types.append('json')
        
        # Check for form data
        if '=' in payload_str and '&' in payload_str:
            content_types.append('form_data')
        
        # Check for HTML
        if '<html' in payload_str.lower() or '<!doctype' in payload_str.lower():
            content_types.append('html')
        
        # Check for JavaScript
        if 'javascript' in payload_str.lower() or 'function' in payload_str:
            content_types.append('javascript')
        
        # Check for PII
        for pii_type, pattern in self.pii_patterns.items():
            if pattern.search(payload_str):
                content_types.append(f'pii_{pii_type}')
        
        return ','.join(content_types) if content_types else 'unknown'
    
    def _assess_packet_risk(self, src_ip: str, dst_ip: str, payload: str, pii_detected: List[str]) -> str:
        """Assess risk level of a packet"""
        risk_score = 0
        
        # Check for PII
        if pii_detected:
            risk_score += len(pii_detected) * 2
        
        # Check destination
        dst_domain = self._ip_to_domain(dst_ip)
        if dst_domain in self.risky_domains:
            risk_score += 3
        
        # Check for suspicious content
        suspicious_keywords = ['password', 'credit_card', 'ssn', 'social_security', 'bank_account']
        for keyword in suspicious_keywords:
            if keyword in payload.lower():
                risk_score += 2
        
        # Check for external destinations
        if not self._is_private_ip(dst_ip):
            risk_score += 1
        
        if risk_score >= 5:
            return 'high'
        elif risk_score >= 3:
            return 'medium'
        else:
            return 'low'
    
    def _assess_connection_risk(self, conn: NetworkConnection) -> str:
        """Assess risk level of a network connection"""
        risk_score = 0
        
        # Check process
        risky_processes = ['chrome.exe', 'firefox.exe', 'iexplore.exe', 'edge.exe']
        if conn.process_name.lower() in risky_processes:
            risk_score += 1
        
        # Check destination
        if not self._is_private_ip(conn.remote_addr):
            risk_score += 1
        
        # Check port
        if conn.remote_port in [80, 443, 8080, 8443]:
            risk_score += 1
        elif conn.remote_port >= 1024:
            risk_score += 0.5
        
        if risk_score >= 2.5:
            return 'high'
        elif risk_score >= 1.5:
            return 'medium'
        else:
            return 'low'
    
    def _extract_destinations(self, payload: str) -> List[str]:
        """Extract destination domains from payload"""
        destinations = []
        
        # Extract URLs
        url_pattern = re.compile(r'https?://[^\s<>"{}|\\^`\[\]]+')
        urls = url_pattern.findall(payload)
        
        for url in urls:
            parsed = urlparse(url)
            if parsed.netloc:
                destinations.append(parsed.netloc)
        
        # Extract domain references
        domain_pattern = re.compile(r'\b[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b')
        domains = domain_pattern.findall(payload)
        
        for domain in domains:
            if '.' in domain and len(domain) > 5:
                destinations.append(domain)
        
        return list(set(destinations))  # Remove duplicates
    
    def _ip_to_domain(self, ip: str) -> str:
        """Convert IP to domain name if possible"""
        try:
            return socket.gethostbyaddr(ip)[0]
        except:
            return ip
    
    def _is_private_ip(self, ip: str) -> bool:
        """Check if IP is private/local"""
        try:
            parts = ip.split('.')
            if len(parts) != 4:
                return False
            
            first = int(parts[0])
            second = int(parts[1])
            
            # 10.0.0.0/8
            if first == 10:
                return True
            # 172.16.0.0/12
            if first == 172 and 16 <= second <= 31:
                return True
            # 192.168.0.0/16
            if first == 192 and second == 168:
                return True
            # 127.0.0.0/8
            if first == 127:
                return True
            
            return False
        except:
            return False
    
    def profile_app_behavior(self) -> Generator[EvidenceItem, None, None]:
        """Profile application network behavior patterns"""
        if not PSUTIL_AVAILABLE:
            yield EvidenceItem(
                id="app_profiling_error",
                source="network_scanner",
                type="error",
                description="psutil not available for app profiling",
                severity="medium",
                metadata={"error": "psutil_not_installed"}
            )
            return
        
        try:
            # Group connections by process
            process_connections = {}
            for conn in self.connections.values():
                if conn.process_name not in process_connections:
                    process_connections[conn.process_name] = []
                process_connections[conn.process_name].append(conn)
            
            for process_name, conns in process_connections.items():
                if len(conns) > 0:
                    # Calculate statistics
                    total_connections = len(conns)
                    external_connections = sum(1 for c in conns if not self._is_private_ip(c.remote_addr))
                    unique_destinations = len(set(c.remote_addr for c in conns))
                    
                    # Risk assessment
                    risk_score = 0
                    if external_connections > 5:
                        risk_score += 2
                    if unique_destinations > 10:
                        risk_score += 2
                    if total_connections > 20:
                        risk_score += 1
                    
                    risk_level = 'high' if risk_score >= 4 else 'medium' if risk_score >= 2 else 'low'
                    
                    profile_data = {
                        'process_name': process_name,
                        'total_connections': total_connections,
                        'external_connections': external_connections,
                        'unique_destinations': unique_destinations,
                        'risk_score': risk_score,
                        'connections': [asdict(c) for c in conns[:10]]  # Limit to 10 connections
                    }
                    
                    yield EvidenceItem(
                        id=f"app_profile_{process_name}",
                        source="network_scanner",
                        type="application_profile",
                        description=f"Network profile: {process_name} ({total_connections} connections)",
                        severity=risk_level,
                        metadata=profile_data
                    )
                    
        except Exception as e:
            yield EvidenceItem(
                id="app_profiling_error",
                source="network_scanner",
                type="error",
                description=f"Error profiling applications: {str(e)}",
                severity="medium",
                metadata={"error": str(e)}
            )
    
    def generate_data_flow_report(self) -> Dict[str, Any]:
        """Generate comprehensive data flow analysis report"""
        report = {
            'summary': {
                'total_connections': len(self.connections),
                'total_packets': len(self.captured_packets),
                'unique_destinations': len(set(c.remote_addr for c in self.connections.values())),
                'high_risk_connections': sum(1 for c in self.connections.values() if self._assess_connection_risk(c) == 'high'),
                'pii_detections': sum(len(p.pii_detected) for p in self.captured_packets)
            },
            'top_destinations': self._get_top_destinations(),
            'risk_analysis': self._analyze_risks(),
            'data_categories': self._categorize_data(),
            'recommendations': self._generate_recommendations()
        }
        
        return report
    
    def _get_top_destinations(self) -> List[Dict[str, Any]]:
        """Get top network destinations by traffic"""
        destination_stats = {}
        
        for conn in self.connections.values():
            dest = conn.remote_addr
            if dest not in destination_stats:
                destination_stats[dest] = {
                    'domain': self._ip_to_domain(dest),
                    'connection_count': 0,
                    'processes': set(),
                    'risk_level': 'low'
                }
            
            destination_stats[dest]['connection_count'] += 1
            destination_stats[dest]['processes'].add(conn.process_name)
            
            # Update risk level
            if self._assess_connection_risk(conn) == 'high':
                destination_stats[dest]['risk_level'] = 'high'
            elif destination_stats[dest]['risk_level'] == 'low' and self._assess_connection_risk(conn) == 'medium':
                destination_stats[dest]['risk_level'] = 'medium'
        
        # Convert to list and sort
        result = []
        for dest, stats in destination_stats.items():
            stats['processes'] = list(stats['processes'])
            stats['ip_address'] = dest
            result.append(stats)
        
        return sorted(result, key=lambda x: x['connection_count'], reverse=True)[:20]
    
    def _analyze_risks(self) -> Dict[str, Any]:
        """Analyze network security risks"""
        risks = {
            'high_risk_destinations': [],
            'data_leakage_indicators': [],
            'suspicious_patterns': [],
            'privacy_concerns': []
        }
        
        # High risk destinations
        for conn in self.connections.values():
            if self._assess_connection_risk(conn) == 'high':
                risks['high_risk_destinations'].append({
                    'destination': conn.remote_addr,
                    'process': conn.process_name,
                    'port': conn.remote_port,
                    'reason': 'High_risk_connection'
                })
        
        # Data leakage indicators
        for packet in self.captured_packets:
            if packet.pii_detected:
                risks['data_leakage_indicators'].append({
                    'timestamp': packet.timestamp.isoformat(),
                    'source': packet.source_ip,
                    'destination': packet.dest_ip,
                    'pii_types': list(set(self._classify_pii(pii) for pii in packet.pii_detected)),
                    'size': packet.size
                })
        
        # Privacy concerns
        for conn in self.connections.values():
            domain = self._ip_to_domain(conn.remote_addr)
            if domain in self.risky_domains:
                risks['privacy_concerns'].append({
                    'domain': domain,
                    'category': self.risky_domains[domain],
                    'process': conn.process_name,
                    'connections': sum(1 for c in self.connections.values() if self._ip_to_domain(c.remote_addr) == domain)
                })
        
        return risks
    
    def _classify_pii(self, pii_data: str) -> str:
        """Classify type of PII data"""
        for pii_type, pattern in self.pii_patterns.items():
            if pattern.match(pii_data):
                return pii_type
        return 'unknown'
    
    def _categorize_data(self) -> Dict[str, int]:
        """Categorize types of data being transmitted"""
        categories = {
            'personal_data': 0,
            'behavioral_data': 0,
            'telemetry_data': 0,
            'analytics_data': 0,
            'advertising_data': 0,
            'unknown_data': 0
        }
        
        for packet in self.captured_packets:
            if packet.pii_detected:
                categories['personal_data'] += 1
            elif 'analytics' in packet.content_type or 'tracking' in packet.content_type:
                categories['analytics_data'] += 1
            elif 'telemetry' in packet.content_type:
                categories['telemetry_data'] += 1
            elif 'ad' in packet.content_type:
                categories['advertising_data'] += 1
            elif 'behavior' in packet.content_type or 'user' in packet.content_type:
                categories['behavioral_data'] += 1
            else:
                categories['unknown_data'] += 1
        
        return categories
    
    def _generate_recommendations(self) -> List[str]:
        """Generate security recommendations based on analysis"""
        recommendations = []
        
        high_risk_count = sum(1 for c in self.connections.values() if self._assess_connection_risk(c) == 'high')
        pii_count = sum(len(p.pii_detected) for p in self.captured_packets)
        
        if high_risk_count > 5:
            recommendations.append("High number of risky connections detected. Consider using a firewall or VPN.")
        
        if pii_count > 0:
            recommendations.append("PII data detected in network traffic. Review applications sending personal information.")
        
        external_connections = sum(1 for c in self.connections.values() if not self._is_private_ip(c.remote_addr))
        if external_connections > 20:
            recommendations.append("High number of external connections. Monitor for potential data exfiltration.")
        
        # Check for risky domains
        risky_domains_found = set()
        for conn in self.connections.values():
            domain = self._ip_to_domain(conn.remote_addr)
            if domain in self.risky_domains:
                risky_domains_found.add(domain)
        
        if risky_domains_found:
            recommendations.append(f"Connections to tracking/advertising domains detected: {', '.join(list(risky_domains_found)[:3])}")
        
        if not recommendations:
            recommendations.append("Network activity appears normal. Continue monitoring for changes.")
        
        return recommendations

def scan_packet_analysis(paths: List[str] = None, config: Optional[ForensicConfig] = None) -> Dict[str, Any]:
    """Perform comprehensive packet and network analysis"""
    analyzer = PacketDataAnalyzer(config)
    
    results = {
        'connections': [],
        'packets': [],
        'profiles': [],
        'report': {}
    }
    
    # Scan active connections
    for evidence in analyzer.scan_active_connections():
        results['connections'].append(asdict(evidence))
    
    # Analyze traffic patterns
    for evidence in analyzer.analyze_traffic_patterns():
        results['packets'].append(asdict(evidence))
    
    # Profile application behavior
    for evidence in analyzer.profile_app_behavior():
        results['profiles'].append(asdict(evidence))
    
    # Generate comprehensive report
    results['report'] = analyzer.generate_data_flow_report()
    
    return results
