"""
Real-time Application Network Monitoring
Provides continuous monitoring of application network behavior and data flows
"""

import time
import threading
import json
import queue
from typing import Dict, List, Any, Optional, Generator, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import logging
import psutil

try:
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
class ApplicationActivity:
    """Represents real-time application network activity"""
    process_name: str
    pid: int
    timestamp: datetime
    connections: List[Dict[str, Any]]
    data_sent: int
    data_received: int
    destinations: List[str]
    protocols: List[str]
    risk_score: float

@dataclass
class NetworkEvent:
    """Represents a network event from an application"""
    timestamp: datetime
    process_name: str
    pid: int
    event_type: str
    source_ip: str
    dest_ip: str
    source_port: int
    dest_port: int
    protocol: str
    data_size: int
    content_preview: str
    risk_level: str

@dataclass
class ApplicationProfile:
    """Represents application network behavior profile"""
    process_name: str
    pid: int
    start_time: datetime
    total_connections: int
    unique_destinations: int
    data_volume: int
    risk_tier: str
    behavior_patterns: List[str]
    privacy_concerns: List[str]

class ApplicationNetworkMonitor(BaseScanner):
    """Real-time application network monitoring system"""
    
    def __init__(self, config: Optional[ForensicConfig] = None):
        super().__init__(ScannerType.APPLICATION_MONITOR, config)
        self.monitoring_active = False
        self.monitor_thread = None
        self.event_queue = queue.Queue()
        self.application_profiles = {}
        self.network_events = deque(maxlen=10000)  # Keep last 10,000 events
        self.suspicious_activities = []
        self.callbacks = []
        
        # Monitoring thresholds
        self.data_volume_threshold = 50 * 1024 * 1024  # 50MB
        self.connection_threshold = 100
        self.destination_threshold = 50
        self.suspicious_protocols = ['torrent', 'p2p', 'irc']

    def scan(self) -> Generator[EvidenceItem, None, None]:
        """Main scan method for application monitoring."""
        yield from self.start_monitoring()
        
    def start_monitoring(self, callback: Optional[Callable] = None) -> Generator[EvidenceItem, None, None]:
        """Start real-time network monitoring"""
        if not PSUTIL_AVAILABLE:
            yield EvidenceItem(
                id="monitoring_error",
                source="application_monitor",
                type="error",
                content="psutil not available for application monitoring",
                risk_level="medium",
                metadata={"error": "psutil_not_installed"}
            )
            return
        
        if self.monitoring_active:
            yield EvidenceItem(
                id="monitoring_warning",
                source="application_monitor",
                type="warning",
                content="Monitoring already active",
                risk_level="low",
                metadata={"status": "already_running"}
            )
            return
        
        try:
            self.monitoring_active = True
            if callback:
                self.callbacks.append(callback)
            
            # Start monitoring thread
            self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self.monitor_thread.start()
            
            yield EvidenceItem(
                id="monitoring_started",
                source="application_monitor",
                type="status",
                content="Application network monitoring started",
                risk_level="info",
                metadata={
                    "start_time": datetime.now().isoformat(),
                    "thresholds": {
                        "data_volume_mb": self.data_volume_threshold / (1024 * 1024),
                        "connections": self.connection_threshold,
                        "destinations": self.destination_threshold
                    }
                }
            )
            
            # Start event processing
            yield from self._process_events()
            
        except Exception as e:
            yield EvidenceItem(
                id="monitoring_error",
                source="application_monitor",
                type="error",
                content=f"Error starting monitoring: {str(e)}",
                risk_level="medium",
                metadata={"error": str(e)}
            )
    
    def stop_monitoring(self) -> EvidenceItem:
        """Stop real-time network monitoring"""
        self.monitoring_active = False
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=5)
        
        return EvidenceItem(
            id="monitoring_stopped",
            source="application_monitor",
            type="status",
            content="Application network monitoring stopped",
            risk_level="info",
            metadata={
                "stop_time": datetime.now().isoformat(),
                "total_events": len(self.network_events),
                "suspicious_activities": len(self.suspicious_activities)
            }
        )
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Get current network connections
                connections = self._get_network_connections()
                
                # Process each connection
                for conn in connections:
                    event = self._create_network_event(conn)
                    if event:
                        self.event_queue.put(event)
                
                # Check for suspicious activities
                self._check_suspicious_activities()
                
                # Update application profiles
                self._update_application_profiles()
                
                # Sleep for monitoring interval
                time.sleep(1)
                
            except Exception as e:
                logging.error(f"Error in monitoring loop: {str(e)}")
                time.sleep(5)
    
    def _get_network_connections(self) -> List[Dict[str, Any]]:
        """Get current network connections with process information"""
        if not PSUTIL_AVAILABLE:
            return []

        connections = []
        
        try:
            net_connections = psutil.net_connections(kind='inet')
            processes = {p.pid: p.info for p in psutil.process_iter(['pid', 'name', 'cmdline'])}
            
            for conn in net_connections:
                if conn.status == 'ESTABLISHED':
                    pid = conn.pid or 0
                    process_info = processes.get(pid, {'name': 'unknown', 'cmdline': []})
                    
                    # Get network I/O for this process
                    try:
                        process = psutil.Process(pid)
                        io_counters = process.io_counters()
                        net_io = process.net_io_counters()
                    except:
                        io_counters = None
                        net_io = None
                    
                    connection_data = {
                        'pid': pid,
                        'process_name': process_info.get('name', 'unknown'),
                        'cmdline': process_info.get('cmdline', []),
                        'local_addr': conn.laddr.ip if conn.laddr else 'unknown',
                        'local_port': conn.laddr.port if conn.laddr else 0,
                        'remote_addr': conn.raddr.ip if conn.raddr else 'unknown',
                        'remote_port': conn.raddr.port if conn.raddr else 0,
                        'status': conn.status,
                        'family': conn.family.name if conn.family else 'unknown',
                        'type': conn.type.name if conn.type else 'unknown',
                        'bytes_sent': net_io.bytes_sent if net_io else 0,
                        'bytes_recv': net_io.bytes_recv if net_io else 0,
                        'timestamp': datetime.now()
                    }
                    
                    connections.append(connection_data)
                    
        except Exception as e:
            logging.error(f"Error getting network connections: {str(e)}")
        
        return connections
    
    def _create_network_event(self, conn: Dict[str, Any]) -> Optional[NetworkEvent]:
        """Create network event from connection data"""
        try:
            # Determine event type
            event_type = self._classify_event_type(conn)
            
            # Determine risk level
            risk_level = self._assess_event_risk(conn)
            
            # Create content preview (placeholder - would need packet capture)
            content_preview = self._generate_content_preview(conn)
            
            event = NetworkEvent(
                timestamp=conn['timestamp'],
                process_name=conn['process_name'],
                pid=conn['pid'],
                event_type=event_type,
                source_ip=conn['local_addr'],
                dest_ip=conn['remote_addr'],
                source_port=conn['local_port'],
                dest_port=conn['remote_port'],
                protocol=conn['type'],
                data_size=conn['bytes_sent'] + conn['bytes_recv'],
                content_preview=content_preview,
                risk_level=risk_level
            )
            
            return event
            
        except Exception as e:
            logging.error(f"Error creating network event: {str(e)}")
            return None
    
    def _classify_event_type(self, conn: Dict[str, Any]) -> str:
        """Classify the type of network event"""
        remote_port = conn['remote_port']
        remote_addr = conn['remote_addr']
        process_name = conn['process_name'].lower()
        
        # Port-based classification
        if remote_port == 443:
            return 'https_traffic'
        elif remote_port == 80:
            return 'http_traffic'
        elif remote_port in [25, 587, 465]:
            return 'email_smtp'
        elif remote_port in [993, 995, 143, 110]:
            return 'email_imap_pop'
        elif remote_port == 53:
            return 'dns_query'
        elif remote_port in [21, 22, 23]:
            return 'file_transfer'
        elif remote_port in [6881, 6882, 6883, 6884, 6885, 6886, 6887, 6888, 6889]:
            return 'p2p_traffic'
        
        # Process-based classification
        if 'chrome' in process_name or 'firefox' in process_name or 'edge' in process_name:
            return 'browser_traffic'
        elif 'outlook' in process_name or 'thunderbird' in process_name:
            return 'email_client'
        elif 'steam' in process_name or 'epic' in process_name:
            return 'gaming_traffic'
        elif 'spotify' in process_name or 'itunes' in process_name:
            return 'streaming_traffic'
        
        return 'unknown_traffic'
    
    def _assess_event_risk(self, conn: Dict[str, Any]) -> str:
        """Assess risk level of network event"""
        risk_score = 0
        
        # Process-based risk
        risky_processes = ['torrent', 'utorrent', 'bittorrent', 'emule', 'limewire']
        process_name = conn['process_name'].lower()
        
        if any(risky in process_name for risky in risky_processes):
            risk_score += 3
        
        # Destination-based risk
        remote_addr = conn['remote_addr']
        if not self._is_private_ip(remote_addr):
            risk_score += 1
        
        # Port-based risk
        remote_port = conn['remote_port']
        if remote_port in [6881, 6882, 6883, 6884, 6885]:  # P2P ports
            risk_score += 2
        elif remote_port >= 1024:  # Non-standard ports
            risk_score += 0.5
        
        # Data volume risk
        data_size = conn['bytes_sent'] + conn['bytes_recv']
        if data_size > 10 * 1024 * 1024:  # 10MB
            risk_score += 2
        elif data_size > 1 * 1024 * 1024:  # 1MB
            risk_score += 1
        
        if risk_score >= 4:
            return 'high'
        elif risk_score >= 2:
            return 'medium'
        else:
            return 'low'
    
    def _generate_content_preview(self, conn: Dict[str, Any]) -> str:
        """Generate content preview for the event"""
        # This would typically involve packet capture and analysis
        # For now, return a descriptive preview
        
        event_type = self._classify_event_type(conn)
        remote_port = conn['remote_port']
        
        if event_type == 'https_traffic':
            return "Encrypted web traffic (HTTPS)"
        elif event_type == 'http_traffic':
            return "Unencrypted web traffic (HTTP)"
        elif event_type == 'email_smtp':
            return "Email transmission (SMTP)"
        elif event_type == 'dns_query':
            return "DNS query"
        elif event_type == 'p2p_traffic':
            return "Peer-to-peer traffic"
        else:
            return f"Network traffic on port {remote_port}"
    
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
    
    def _check_suspicious_activities(self):
        """Check for suspicious network activities"""
        current_time = datetime.now()
        
        # Check for high data volume
        recent_events = [e for e in self.network_events if current_time - e.timestamp < timedelta(minutes=5)]
        
        # Group by process
        process_data = defaultdict(lambda: {'data_volume': 0, 'connections': 0, 'destinations': set()})
        
        for event in recent_events:
            key = f"{event.process_name}_{event.pid}"
            process_data[key]['data_volume'] += event.data_size
            process_data[key]['connections'] += 1
            process_data[key]['destinations'].add(event.dest_ip)
        
        # Check thresholds
        for key, data in process_data.items():
            process_name, pid = key.split('_')
            
            # High data volume
            if data['data_volume'] > self.data_volume_threshold:
                suspicious = {
                    'type': 'high_data_volume',
                    'process': process_name,
                    'pid': int(pid),
                    'data_volume': data['data_volume'],
                    'timestamp': current_time,
                    'severity': 'high' if data['data_volume'] > self.data_volume_threshold * 2 else 'medium'
                }
                self.suspicious_activities.append(suspicious)
            
            # Many connections
            if data['connections'] > self.connection_threshold:
                suspicious = {
                    'type': 'many_connections',
                    'process': process_name,
                    'pid': int(pid),
                    'connection_count': data['connections'],
                    'timestamp': current_time,
                    'severity': 'medium'
                }
                self.suspicious_activities.append(suspicious)
            
            # Many destinations
            if len(data['destinations']) > self.destination_threshold:
                suspicious = {
                    'type': 'many_destinations',
                    'process': process_name,
                    'pid': int(pid),
                    'destination_count': len(data['destinations']),
                    'destinations': list(data['destinations'])[:10],  # Limit to 10
                    'timestamp': current_time,
                    'severity': 'high' if len(data['destinations']) > self.destination_threshold * 2 else 'medium'
                }
                self.suspicious_activities.append(suspicious)
    
    def _update_application_profiles(self):
        """Update application behavior profiles"""
        current_time = datetime.now()
        
        # Group events by application
        app_events = defaultdict(list)
        for event in self.network_events:
            key = f"{event.process_name}_{event.pid}"
            app_events[key].append(event)
        
        # Update profiles
        for key, events in app_events.items():
            process_name, pid = key.split('_')
            
            if key not in self.application_profiles:
                self.application_profiles[key] = ApplicationProfile(
                    process_name=process_name,
                    pid=int(pid),
                    start_time=current_time,
                    total_connections=0,
                    unique_destinations=0,
                    data_volume=0,
                    risk_tier='low',
                    behavior_patterns=[],
                    privacy_concerns=[]
                )
            
            profile = self.application_profiles[key]
            profile.total_connections = len(events)
            profile.unique_destinations = len(set(e.dest_ip for e in events))
            profile.data_volume = sum(e.data_size for e in events)
            
            # Determine risk tier
            profile.risk_tier = self._calculate_risk_tier(profile)
            
            # Identify behavior patterns
            profile.behavior_patterns = self._identify_behavior_patterns(events)
            
            # Identify privacy concerns
            profile.privacy_concerns = self._identify_privacy_concerns(events)
    
    def _calculate_risk_tier(self, profile: ApplicationProfile) -> str:
        """Calculate risk tier for application"""
        risk_score = 0
        
        # Data volume factor
        if profile.data_volume > 100 * 1024 * 1024:  # 100MB
            risk_score += 3
        elif profile.data_volume > 50 * 1024 * 1024:  # 50MB
            risk_score += 2
        elif profile.data_volume > 10 * 1024 * 1024:  # 10MB
            risk_score += 1
        
        # Connection factor
        if profile.total_connections > 200:
            risk_score += 3
        elif profile.total_connections > 100:
            risk_score += 2
        elif profile.total_connections > 50:
            risk_score += 1
        
        # Destination factor
        if profile.unique_destinations > 20:
            risk_score += 2
        elif profile.unique_destinations > 10:
            risk_score += 1
        
        # Process-based factor
        process_name = profile.process_name.lower()
        risky_processes = ['torrent', 'utorrent', 'bittorrent', 'emule']
        if any(risky in process_name for risky in risky_processes):
            risk_score += 3
        
        if risk_score >= 6:
            return 'critical'
        elif risk_score >= 4:
            return 'high'
        elif risk_score >= 2:
            return 'medium'
        else:
            return 'low'
    
    def _identify_behavior_patterns(self, events: List[NetworkEvent]) -> List[str]:
        """Identify behavior patterns from events"""
        patterns = []
        
        # Analyze event types
        event_types = [e.event_type for e in events]
        type_counts = defaultdict(int)
        for et in event_types:
            type_counts[et] += 1
        
        # Identify dominant patterns
        if type_counts['browser_traffic'] > len(events) * 0.8:
            patterns.append('heavy_browser_usage')
        
        if type_counts['p2p_traffic'] > 0:
            patterns.append('p2p_activity')
        
        if type_counts['streaming_traffic'] > len(events) * 0.5:
            patterns.append('streaming_activity')
        
        # Time-based patterns
        timestamps = [e.timestamp for e in events]
        if timestamps:
            time_span = max(timestamps) - min(timestamps)
            if time_span > timedelta(hours=4):
                patterns.append('extended_activity')
        
        # Destination patterns
        destinations = [e.dest_ip for e in events]
        unique_destinations = set(destinations)
        if len(unique_destinations) > len(destinations) * 0.8:
            patterns.append('diverse_destinations')
        
        return patterns
    
    def _identify_privacy_concerns(self, events: List[NetworkEvent]) -> List[str]:
        """Identify privacy concerns from events"""
        concerns = []
        
        # High-risk destinations
        for event in events:
            if event.risk_level == 'high':
                if 'high_risk_destination' not in concerns:
                    concerns.append('high_risk_destination')
        
        # Unencrypted traffic
        unencrypted_events = [e for e in events if e.event_type == 'http_traffic']
        if len(unencrypted_events) > len(events) * 0.3:
            concerns.append('unencrypted_traffic')
        
        # Frequent connections to tracking domains
        tracking_domains = ['google-analytics.com', 'facebook.com', 'doubleclick.net']
        tracking_events = [e for e in events if any(domain in e.dest_ip for domain in tracking_domains)]
        if len(tracking_events) > 10:
            concerns.append('extensive_tracking')
        
        # Large data transfers
        large_events = [e for e in events if e.data_size > 1024 * 1024]  # 1MB
        if len(large_events) > 5:
            concerns.append('large_data_transfers')
        
        return concerns
    
    def _process_events(self) -> Generator[EvidenceItem, None, None]:
        """Process events from the queue"""
        while self.monitoring_active:
            try:
                # Get event from queue
                event = self.event_queue.get(timeout=1)
                
                # Add to events list
                self.network_events.append(event)
                
                # Create evidence item
                evidence = EvidenceItem(
                    id=f"network_event_{event.process_name}_{event.pid}_{int(event.timestamp.timestamp())}",
                    source="application_monitor",
                    data_type="network_event",
                    description=f"Network Event: {event.process_name} -> {event.dest_ip}:{event.dest_port} ({event.event_type})",
                    severity=event.risk_level,
                    metadata=asdict(event)
                )
                
                yield evidence
                
                # Process callbacks
                for callback in self.callbacks:
                    try:
                        callback(evidence)
                    except Exception as e:
                        logging.error(f"Error in callback: {str(e)}")
                
            except queue.Empty:
                continue
            except Exception as e:
                logging.error(f"Error processing event: {str(e)}")
                yield EvidenceItem(
                    id="event_processing_error",
                    source="application_monitor",
                    data_type="error",
                    description=f"Error processing event: {str(e)}",
                    severity="medium",
                    metadata={"error": str(e)}
                )
    
    def get_monitoring_summary(self) -> Dict[str, Any]:
        """Get current monitoring summary"""
        current_time = datetime.now()
        
        # Recent events (last hour)
        recent_events = [e for e in self.network_events if current_time - e.timestamp < timedelta(hours=1)]
        
        # Active applications
        active_apps = set()
        for event in recent_events:
            active_apps.add(f"{event.process_name}_{event.pid}")
        
        # Risk distribution
        risk_distribution = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        for event in recent_events:
            risk_distribution[event.risk_level] += 1
        
        # Top applications by data volume
        app_data_volume = defaultdict(int)
        for event in recent_events:
            key = f"{event.process_name}_{event.pid}"
            app_data_volume[key] += event.data_size
        
        top_apps = sorted(app_data_volume.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            'monitoring_active': self.monitoring_active,
            'current_time': current_time.isoformat(),
            'recent_events': {
                'total': len(recent_events),
                'risk_distribution': risk_distribution,
                'unique_applications': len(active_apps)
            },
            'top_applications': [
                {
                    'application': app.split('_')[0],
                    'pid': int(app.split('_')[1]),
                    'data_volume_mb': volume / (1024 * 1024)
                }
                for app, volume in top_apps
            ],
            'suspicious_activities': len(self.suspicious_activities),
            'application_profiles': len(self.application_profiles),
            'total_events_processed': len(self.network_events)
        }
    
    def generate_monitoring_report(self) -> Dict[str, Any]:
        """Generate comprehensive monitoring report"""
        summary = self.get_monitoring_summary()
        
        # Application profiles summary
        profile_summary = {
            'total_profiles': len(self.application_profiles),
            'risk_tiers': {'critical': 0, 'high': 0, 'medium': 0, 'low': 0},
            'common_patterns': defaultdict(int),
            'privacy_concerns': defaultdict(int)
        }
        
        for profile in self.application_profiles.values():
            profile_summary['risk_tiers'][profile.risk_tier] += 1
            
            for pattern in profile.behavior_patterns:
                profile_summary['common_patterns'][pattern] += 1
            
            for concern in profile.privacy_concerns:
                profile_summary['privacy_concerns'][concern] += 1
        
        # Suspicious activities analysis
        suspicious_analysis = {
            'total_activities': len(self.suspicious_activities),
            'by_type': defaultdict(int),
            'by_severity': {'critical': 0, 'high': 0, 'medium': 0, 'low': 0},
            'recent_activities': []
        }
        
        current_time = datetime.now()
        recent_suspicious = [
            activity for activity in self.suspicious_activities
            if current_time - activity['timestamp'] < timedelta(hours=24)
        ]
        
        for activity in recent_suspicious:
            suspicious_analysis['by_type'][activity['type']] += 1
            suspicious_analysis['by_severity'][activity['severity']] += 1
        
        suspicious_analysis['recent_activities'] = recent_suspicious[-10:]  # Last 10
        
        return {
            'summary': summary,
            'application_profiles': profile_summary,
            'suspicious_activities': suspicious_analysis,
            'recommendations': self._generate_monitoring_recommendations(),
            'report_timestamp': datetime.now().isoformat()
        }
    
    def _generate_monitoring_recommendations(self) -> List[str]:
        """Generate recommendations based on monitoring data"""
        recommendations = []
        
        summary = self.get_monitoring_summary()
        
        # High-risk applications
        high_risk_apps = [
            profile for profile in self.application_profiles.values()
            if profile.risk_tier in ['critical', 'high']
        ]
        
        if len(high_risk_apps) > 3:
            recommendations.append(f"Multiple high-risk applications detected ({len(high_risk_apps)}). Review application usage.")
        
        # Suspicious activities
        if summary['suspicious_activities'] > 10:
            recommendations.append(f"High number of suspicious activities ({summary['suspicious_activities']}). Investigate potential security issues.")
        
        # Data volume
        recent_events = [e for e in self.network_events if datetime.now() - e.timestamp < timedelta(hours=1)]
        total_data_volume = sum(e.data_size for e in recent_events)
        
        if total_data_volume > 500 * 1024 * 1024:  # 500MB per hour
            recommendations.append("High data volume detected. Monitor for potential data exfiltration.")
        
        # Privacy concerns
        privacy_concern_count = sum(len(profile.privacy_concerns) for profile in self.application_profiles.values())
        if privacy_concern_count > 5:
            recommendations.append("Multiple privacy concerns identified. Review application privacy settings.")
        
        if not recommendations:
            recommendations.append("Network monitoring shows normal activity. Continue monitoring.")
        
        return recommendations

def scan_application_monitoring(duration: int = 60, config: Optional[ForensicConfig] = None) -> Dict[str, Any]:
    """Perform application network monitoring for specified duration"""
    monitor = ApplicationNetworkMonitor(config)
    
    results = {
        'events': [],
        'profiles': [],
        'suspicious_activities': [],
        'report': {}
    }
    
    # Start monitoring
    evidence_generator = monitor.start_monitoring()
    
    # Collect events for specified duration
    start_time = time.time()
    while time.time() - start_time < duration:
        try:
            evidence = next(evidence_generator)
            if evidence.data_type == 'network_event':
                results['events'].append(asdict(evidence))
        except StopIteration:
            break
        except Exception as e:
            logging.error(f"Error in monitoring: {str(e)}")
            time.sleep(1)
    
    # Stop monitoring
    monitor.stop_monitoring()
    
    # Collect profiles and suspicious activities
    results['profiles'] = [asdict(p) for p in monitor.application_profiles.values()]
    results['suspicious_activities'] = monitor.suspicious_activities
    
    # Generate report
    results['report'] = monitor.generate_monitoring_report()
    
    return results
