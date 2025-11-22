"""
Enhanced Reporting Module with Detailed Data Flow Analysis
Generates comprehensive forensic reports with data flow visualization and analysis
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter
import logging

try:
    import graphviz
    GRAPHVIZ_AVAILABLE = True
except ImportError:
    GRAPHVIZ_AVAILABLE = False

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    import seaborn as sns
    PLOTTING_AVAILABLE = True
except ImportError:
    PLOTTING_AVAILABLE = False

from ..core.models import EvidenceItem, ForensicResult, Account, Credential
from ..core.config import ForensicConfig
from ..scanners.packet_analyzer import PacketDataAnalyzer
from ..scanners.content_classifier import DataContentClassifier
from ..scanners.destination_intelligence import DestinationIntelligence
from ..scanners.application_monitor import ApplicationNetworkMonitor
from ..scanners.security_auditor import AccountSecurityAuditor
from ..scanners.behavioral_intelligence import BehavioralIntelligenceEngine
from ..utils.helpers import extract_domain
from ..db.services import ServicesDB
from ..db.manager import DatabaseManager
from ..db.schema import update_privacy_ledger, get_daily_health_summary
from ..core.intelligence import EntityResolver
from pathlib import Path


class PrivacyHealthAnalyzer:
    def calculate_digital_health(self, evidence_items, services_db, db_manager: DatabaseManager, entity_resolver: EntityResolver):
        for item in evidence_items:
            if item.type == 'browser_history':
                date = item.timestamp.date().isoformat()
                domain = extract_domain(item.metadata['url'])
                company_name = entity_resolver.resolve(domain)
                
                service_info = services_db.get_service_by_domain(domain)
                
                if service_info:
                    category = service_info.get('category', 'Uncategorized')
                    try:
                        risk_score = float(service_info.get('privacy_rating', 1.0))
                    except (ValueError, TypeError):
                        risk_score = 1.0
                else:
                    category = 'Uncategorized'
                    risk_score = 1.0
                
                update_privacy_ledger(db_manager.get_connection(), date, company_name, category, 1, risk_score)


@dataclass
class DataFlowNode:
    """Represents a node in the data flow graph"""
    node_id: str
    node_type: str  # application, service, destination, user
    name: str
    metadata: Dict[str, Any]
    risk_score: float
    data_volume: int
    connection_count: int

@dataclass
class DataFlowEdge:
    """Represents an edge in the data flow graph"""
    edge_id: str
    source_id: str
    destination_id: str
    data_type: str
    volume: int
    protocol: str
    risk_level: str
    timestamp: datetime
    metadata: Dict[str, Any]

@dataclass
class DataFlowPath:
    """Represents a complete data flow path"""
    path_id: str
    path_type: str
    nodes: List[DataFlowNode]
    edges: List[DataFlowEdge]
    total_volume: int
    risk_score: float
    duration: timedelta
    description: str

@dataclass
class FlowAnalysis:
    """Represents analysis of data flow patterns"""
    analysis_id: str
    flow_patterns: List[str]
    anomalies: List[str]
    risk_assessment: Dict[str, Any]
    recommendations: List[str]
    summary_statistics: Dict[str, Any]

class EnhancedReportingEngine:
    """Enhanced reporting with detailed data flow analysis"""
    
    def __init__(self, config: Optional[ForensicConfig] = None):
        self.config = config or ForensicConfig()
        self.scanners = self._init_scanners()
        self.data_flows = []
        self.flow_graph = defaultdict(list)
        self.analysis_cache = {}
        
        # Determine the root directory of the project
        project_root = Path(__file__).parent.parent.parent
        services_csv_path = project_root / "data" / "services.csv"
        self.services_db = ServicesDB(services_csv_path)
        self.db_manager = DatabaseManager(self.config.db_path)
        self.entity_resolver = EntityResolver()
        
    def _init_scanners(self) -> Dict[str, Any]:
        """Initialize all scanners"""
        return {
            'packet_analyzer': PacketDataAnalyzer(self.config),
            'content_classifier': DataContentClassifier(self.config),
            'destination_intelligence': DestinationIntelligence(self.config),
            'application_monitor': ApplicationNetworkMonitor(self.config),
            'security_auditor': AccountSecurityAuditor(self.config),
            'behavioral_engine': BehavioralIntelligenceEngine(self.config)
        }
    
    def generate_comprehensive_report(self, 
                                     evidence_items: List[EvidenceItem],
                                     accounts: Optional[List[Account]] = None,
                                     credentials: Optional[List[Credential]] = None,
                                     include_visualizations: bool = True) -> Dict[str, Any]:
        """Generate comprehensive forensic report with data flow analysis"""
        
        # Initialize PrivacyHealthAnalyzer and calculate digital health
        privacy_analyzer = PrivacyHealthAnalyzer()
        privacy_analyzer.calculate_digital_health(evidence_items, self.services_db, self.db_manager, self.entity_resolver)

        executive_summary = self._generate_executive_summary(evidence_items)
        executive_summary['digital_health_scores'] = get_daily_health_summary(self.db_manager.get_connection())

        report = {
            'report_metadata': self._generate_report_metadata(),
            'executive_summary': executive_summary,
            'evidence_analysis': self._analyze_evidence(evidence_items),
            'data_flow_analysis': self._analyze_data_flows(evidence_items),
            'security_analysis': self._analyze_security(evidence_items, accounts, credentials),
            'behavioral_analysis': self._analyze_behavioral_patterns(evidence_items),
            'risk_assessment': self._assess_overall_risk(evidence_items),
            'recommendations': self._generate_recommendations(evidence_items),
            'detailed_findings': self._generate_detailed_findings(evidence_items),
            'appendices': {}
        }
        
        # Add visualizations if requested and available
        if include_visualizations:
            report['visualizations'] = self._generate_visualizations(evidence_items)
        
        # Add data flow diagrams
        if GRAPHVIZ_AVAILABLE:
            report['data_flow_diagrams'] = self._generate_data_flow_diagrams(evidence_items)
        
        return report
    
    def _generate_report_metadata(self) -> Dict[str, Any]:
        """Generate report metadata"""
        return {
            'report_title': 'Comprehensive Digital Forensic Analysis Report',
            'report_version': '2.0',
            'generated_at': datetime.now().isoformat(),
            'generated_by': 'Digital Forensic Surgeon - Enhanced Reporting Engine',
            'analysis_period': {
                'start': (datetime.now() - timedelta(days=1)).isoformat(),
                'end': datetime.now().isoformat()
            },
            'scope': 'Full system forensic analysis with data flow mapping',
            'methodology': [
                'Packet-level network inspection',
                'Deep content classification',
                'Destination intelligence analysis',
                'Application network monitoring',
                'Security vulnerability assessment',
                'Behavioral pattern analysis',
                'Data flow reconstruction'
            ]
        }
    
    def _generate_executive_summary(self, evidence_items: List[EvidenceItem]) -> Dict[str, Any]:
        """Generate executive summary"""
        if not evidence_items:
            return {
                'overview': 'No evidence items found during analysis.',
                'key_findings': [],
                'risk_level': 'low',
                'recommendations': ['No immediate action required.']
            }
        
        # Analyze evidence distribution
        severity_counts = Counter(item.severity for item in evidence_items)
        source_counts = Counter(item.source for item in evidence_items)
        type_counts = Counter(item.data_type for item in evidence_items)
        
        # Calculate risk metrics
        high_risk_count = severity_counts.get('critical', 0) + severity_counts.get('high', 0)
        total_risk_score = sum([
            10 if item.severity == 'critical' else
            7 if item.severity == 'high' else
            4 if item.severity == 'medium' else
            1 for item in evidence_items
        ])
        
        # Determine overall risk level
        if high_risk_count > 10 or total_risk_score > 100:
            risk_level = 'critical'
        elif high_risk_count > 5 or total_risk_score > 50:
            risk_level = 'high'
        elif high_risk_count > 0 or total_risk_score > 20:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        # Identify key findings
        key_findings = []
        
        if severity_counts.get('critical', 0) > 0:
            key_findings.append(f"{severity_counts['critical']} critical security issues identified")
        
        if severity_counts.get('high', 0) > 0:
            key_findings.append(f"{severity_counts['high']} high-risk items detected")
        
        # Check for data exfiltration patterns
        data_exfil_items = [item for item in evidence_items if 'exfil' in item.description.lower()]
        if data_exfil_items:
            key_findings.append(f"Potential data exfiltration activity detected ({len(data_exfil_items)} items)")
        
        # Check for unauthorized access
        unauthorized_items = [item for item in evidence_items if 'unauthorized' in item.description.lower()]
        if unauthorized_items:
            key_findings.append(f"Unauthorized access patterns identified ({len(unauthorized_items)} items)")
        
        return {
            'overview': f"Analysis of {len(evidence_items)} evidence items revealed {risk_level} risk level with {high_risk_count} high-priority issues requiring immediate attention.",
            'key_findings': key_findings,
            'risk_level': risk_level,
            'statistics': {
                'total_evidence': len(evidence_items),
                'critical_items': severity_counts.get('critical', 0),
                'high_risk_items': severity_counts.get('high', 0),
                'medium_risk_items': severity_counts.get('medium', 0),
                'low_risk_items': severity_counts.get('low', 0),
                'total_risk_score': total_risk_score,
                'primary_sources': dict(source_counts.most_common(5)),
                'primary_types': dict(type_counts.most_common(5))
            },
            'recommendations': self._generate_executive_recommendations(risk_level, high_risk_count)
        }
    
    def _generate_executive_recommendations(self, risk_level: str, high_risk_count: int) -> List[str]:
        """Generate executive-level recommendations"""
        recommendations = []
        
        if risk_level == 'critical':
            recommendations.extend([
                "IMMEDIATE ACTION REQUIRED: Isolate affected systems to prevent further damage",
                "Conduct emergency incident response procedures",
                "Engage cybersecurity team for comprehensive investigation",
                "Review and enhance security controls immediately"
            ])
        elif risk_level == 'high':
            recommendations.extend([
                "Address high-priority security issues within 24 hours",
                "Implement additional monitoring and logging",
                "Review access controls and permissions",
                "Schedule comprehensive security audit"
            ])
        elif risk_level == 'medium':
            recommendations.extend([
                "Address identified issues within 7 days",
                "Enhance monitoring and alerting",
                "Review security policies and procedures",
                "Conduct user security awareness training"
            ])
        else:
            recommendations.extend([
                "Continue regular security monitoring",
                "Maintain current security posture",
                "Schedule periodic security assessments",
                "Update security documentation"
            ])
        
        return recommendations
    
    def _analyze_evidence(self, evidence_items: List[EvidenceItem]) -> Dict[str, Any]:
        """Perform detailed evidence analysis"""
        if not evidence_items:
            return {'summary': 'No evidence items to analyze.'}
        
        # Evidence by source
        source_analysis = {}
        for source in set(item.source for item in evidence_items):
            source_items = [item for item in evidence_items if item.source == source]
            source_analysis[source] = {
                'count': len(source_items),
                'severity_distribution': dict(Counter(item.severity for item in source_items)),
                'risk_score': sum([
                    10 if item.severity == 'critical' else
                    7 if item.severity == 'high' else
                    4 if item.severity == 'medium' else
                    1 for item in source_items
                ]),
                'top_findings': [
                    {
                        'description': item.description,
                        'severity': item.severity,
                        'timestamp': item.timestamp.isoformat()
                    }
                    for item in sorted(source_items, key=lambda x: self._severity_weight(x.severity), reverse=True)[:5]
                ]
            }
        
        # Evidence by type
        type_analysis = {}
        for data_type in set(item.data_type for item in evidence_items):
            type_items = [item for item in evidence_items if item.data_type == data_type]
            type_analysis[data_type] = {
                'count': len(type_items),
                'risk_distribution': dict(Counter(item.severity for item in type_items)),
                'patterns': self._identify_type_patterns(type_items)
            }
        
        # Temporal analysis
        temporal_analysis = self._analyze_temporal_patterns(evidence_items)
        
        # Geographic analysis (if available)
        geographic_analysis = self._analyze_geographic_patterns(evidence_items)
        
        return {
            'summary': f"Analyzed {len(evidence_items)} evidence items across {len(source_analysis)} sources and {len(type_analysis)} types.",
            'source_analysis': source_analysis,
            'type_analysis': type_analysis,
            'temporal_analysis': temporal_analysis,
            'geographic_analysis': geographic_analysis,
            'correlation_analysis': self._analyze_evidence_correlations(evidence_items)
        }
    
    def _severity_weight(self, severity: str) -> int:
        """Get numerical weight for severity"""
        weights = {'critical': 10, 'high': 7, 'medium': 4, 'low': 1}
        return weights.get(severity, 0)
    
    def _identify_type_patterns(self, items: List[EvidenceItem]) -> List[str]:
        """Identify patterns within evidence type"""
        patterns = []
        
        # Common keywords in descriptions
        descriptions = [item.description.lower() for item in items]
        word_counts = Counter(' '.join(descriptions).split())
        common_words = [word for word, count in word_counts.most_common(10) if len(word) > 3]
        
        if common_words:
            patterns.append(f"Common themes: {', '.join(common_words[:5])}")
        
        # Time patterns
        if len(items) > 1:
            timestamps = [item.timestamp for item in items]
            time_span = max(timestamps) - min(timestamps)
            if time_span.total_seconds() < 3600:  # Less than 1 hour
                patterns.append("Concentrated activity within short time period")
        
        return patterns
    
    def _analyze_temporal_patterns(self, evidence_items: List[EvidenceItem]) -> Dict[str, Any]:
        """Analyze temporal patterns in evidence"""
        if not evidence_items:
            return {}
        
        timestamps = [item.timestamp for item in evidence_items]
        hours = [ts.hour for ts in timestamps]
        days = [ts.weekday() for ts in timestamps]  # 0 = Monday, 6 = Sunday
        
        return {
            'time_span': {
                'start': min(timestamps).isoformat(),
                'end': max(timestamps).isoformat(),
                'duration_hours': (max(timestamps) - min(timestamps)).total_seconds() / 3600
            },
            'activity_patterns': {
                'peak_hour': max(set(hours), key=hours.count) if hours else None,
                'hour_distribution': dict(Counter(hours)),
                'peak_day': max(set(days), key=days.count) if days else None,
                'day_distribution': dict(Counter(days)),
                'business_hours_activity': sum(1 for h in hours if 8 <= h <= 18),
                'off_hours_activity': sum(1 for h in hours if h < 8 or h > 18)
            },
            'frequency_analysis': {
                'items_per_hour': len(evidence_items) / max(1, (max(timestamps) - min(timestamps)).total_seconds() / 3600),
                'burst_periods': self._identify_activity_bursts(timestamps)
            }
        }
    
    def _identify_activity_bursts(self, timestamps: List[datetime]) -> List[Dict[str, Any]]:
        """Identify periods of high activity"""
        if len(timestamps) < 5:
            return []
        
        # Sort timestamps
        sorted_times = sorted(timestamps)
        
        # Find periods with high concentration of activity
        bursts = []
        window_size = timedelta(minutes=30)
        
        for i, start_time in enumerate(sorted_times):
            end_time = start_time + window_size
            window_items = [ts for ts in sorted_times[i:] if ts <= end_time]
            
            if len(window_items) >= 5:  # Threshold for burst
                bursts.append({
                    'start_time': start_time.isoformat(),
                    'end_time': end_time.isoformat(),
                    'item_count': len(window_items),
                    'burst_score': len(window_items) / 5.0
                })
        
        return bursts[:5]  # Return top 5 bursts
    
    def _analyze_geographic_patterns(self, evidence_items: List[EvidenceItem]) -> Dict[str, Any]:
        """Analyze geographic patterns (if location data available)"""
        locations = []
        
        for item in evidence_items:
            if item.metadata and 'location' in item.metadata:
                locations.append(item.metadata['location'])
            elif item.metadata and 'country' in item.metadata:
                locations.append(item.metadata['country'])
        
        if not locations:
            return {'message': 'No geographic data available in evidence'}
        
        return {
            'unique_locations': len(set(locations)),
            'location_distribution': dict(Counter(locations)),
            'international_activity': len([loc for loc in locations if loc not in ['US', 'USA', 'United States']]),
            'suspicious_locations': [loc for loc, count in Counter(locations).items() if count > 10]
        }
    
    def _analyze_evidence_correlations(self, evidence_items: List[EvidenceItem]) -> Dict[str, Any]:
        """Analyze correlations between evidence items"""
        correlations = {
            'source_correlations': {},
            'temporal_correlations': {},
            'severity_correlations': {}
        }
        
        # Source correlations
        sources = [item.source for item in evidence_items]
        for source in set(sources):
            source_items = [item for item in evidence_items if item.source == source]
            other_sources = [item.source for item in evidence_items if item.source != source]
            
            # Check for co-occurrence patterns
            co_occurrence = {}
            for other_source in set(other_sources):
                other_items = [item for item in evidence_items if item.source == other_source]
                
                # Check temporal overlap
                source_times = [item.timestamp for item in source_items]
                other_times = [item.timestamp for item in other_items]
                
                overlaps = 0
                for st in source_times:
                    for ot in other_times:
                        if abs((st - ot).total_seconds()) < 300:  # 5 minute window
                            overlaps += 1
                
                if overlaps > 0:
                    co_occurrence[other_source] = overlaps
            
            if co_occurrence:
                correlations['source_correlations'][source] = co_occurrence
        
        # Severity correlations
        severity_patterns = defaultdict(list)
        for item in evidence_items:
            severity_patterns[item.severity].append(item)
        
        for severity, items in severity_patterns.items():
            if len(items) > 1:
                # Check for common patterns within same severity
                common_sources = Counter(item.source for item in items)
                common_types = Counter(item.data_type for item in items)
                
                correlations['severity_correlations'][severity] = {
                    'common_sources': dict(common_sources.most_common(3)),
                    'common_types': dict(common_types.most_common(3))
                }
        
        return correlations
    
    def _analyze_data_flows(self, evidence_items: List[EvidenceItem]) -> Dict[str, Any]:
        """Analyze data flow patterns"""
        # Extract data flow information from evidence
        flow_nodes = {}
        flow_edges = []
        
        for item in evidence_items:
            # Create nodes from evidence
            if item.metadata:
                # Source node
                if 'source_entity' in item.metadata:
                    source_id = item.metadata['source_entity']
                    if source_id not in flow_nodes:
                        flow_nodes[source_id] = DataFlowNode(
                            node_id=source_id,
                            node_type=item.metadata.get('source_type', 'unknown'),
                            name=item.metadata.get('source_name', source_id),
                            metadata=item.metadata,
                            risk_score=self._severity_weight(item.severity),
                            data_volume=item.metadata.get('data_volume', 0),
                            connection_count=0
                        )
                    flow_nodes[source_id].connection_count += 1
                
                # Destination node
                if 'destination_entity' in item.metadata:
                    dest_id = item.metadata['destination_entity']
                    if dest_id not in flow_nodes:
                        flow_nodes[dest_id] = DataFlowNode(
                            node_id=dest_id,
                            node_type=item.metadata.get('destination_type', 'unknown'),
                            name=item.metadata.get('destination_name', dest_id),
                            metadata=item.metadata,
                            risk_score=self._severity_weight(item.severity),
                            data_volume=item.metadata.get('data_volume', 0),
                            connection_count=0
                        )
                    flow_nodes[dest_id].connection_count += 1
                
                # Create edge
                if 'source_entity' in item.metadata and 'destination_entity' in item.metadata:
                    edge = DataFlowEdge(
                        edge_id=f"{item.metadata['source_entity']}_to_{item.metadata['destination_entity']}_{int(item.timestamp.timestamp())}",
                        source_id=item.metadata['source_entity'],
                        destination_id=item.metadata['destination_entity'],
                        data_type=item.data_type,
                        volume=item.metadata.get('data_volume', 0),
                        protocol=item.metadata.get('protocol', 'unknown'),
                        risk_level=item.severity,
                        timestamp=item.timestamp,
                        metadata=item.metadata
                    )
                    flow_edges.append(edge)
        
        # Analyze flow patterns
        flow_analysis = self._analyze_flow_patterns(flow_nodes, flow_edges)
        
        # Identify suspicious flows
        suspicious_flows = self._identify_suspicious_flows(flow_nodes, flow_edges)
        
        # Generate flow paths
        flow_paths = self._generate_flow_paths(flow_nodes, flow_edges)
        
        return {
            'summary': f"Analyzed {len(flow_nodes)} nodes and {len(flow_edges)} data flows",
            'flow_statistics': {
                'total_nodes': len(flow_nodes),
                'total_edges': len(flow_edges),
                'high_risk_nodes': len([n for n in flow_nodes.values() if n.risk_score >= 7]),
                'high_risk_flows': len([e for e in flow_edges if e.risk_level in ['critical', 'high']]),
                'total_data_volume': sum(e.volume for e in flow_edges),
                'protocols': dict(Counter(e.protocol for e in flow_edges))
            },
            'flow_analysis': flow_analysis,
            'suspicious_flows': suspicious_flows,
            'flow_paths': [asdict(path) for path in flow_paths],
            'node_analysis': {
                node_id: asdict(node) for node_id, node in flow_nodes.items()
            }
        }
    
    def _analyze_flow_patterns(self, nodes: Dict[str, DataFlowNode], edges: List[DataFlowEdge]) -> Dict[str, Any]:
        """Analyze patterns in data flows"""
        if not edges:
            return {'message': 'No data flows to analyze'}
        
        # Identify communication patterns
        communication_patterns = {}
        
        # Hub analysis (nodes with many connections)
        hub_nodes = sorted(nodes.values(), key=lambda x: x.connection_count, reverse=True)[:5]
        
        # Protocol analysis
        protocol_usage = Counter(edge.protocol for edge in edges)
        
        # Volume analysis
        volume_by_node = defaultdict(int)
        for edge in edges:
            volume_by_node[edge.source_id] += edge.volume
            volume_by_node[edge.destination_id] += edge.volume
        
        # Risk analysis
        risk_by_protocol = defaultdict(list)
        for edge in edges:
            risk_by_protocol[edge.protocol].append(self._severity_weight(edge.risk_level))
        
        return {
            'hub_nodes': [
                {
                    'node_id': node.node_id,
                    'name': node.name,
                    'connection_count': node.connection_count,
                    'risk_score': node.risk_score
                }
                for node in hub_nodes
            ],
            'protocol_analysis': {
                'usage_distribution': dict(protocol_usage),
                'risk_by_protocol': {
                    protocol: {
                        'avg_risk': sum(risks) / len(risks),
                        'max_risk': max(risks),
                        'flow_count': len(risks)
                    }
                    for protocol, risks in risk_by_protocol.items()
                }
            },
            'volume_analysis': {
                'total_volume': sum(edge.volume for edge in edges),
                'volume_by_node': dict(sorted(volume_by_node.items(), key=lambda x: x[1], reverse=True)[:10]),
                'high_volume_flows': [
                    {
                        'source': edge.source_id,
                        'destination': edge.destination_id,
                        'volume': edge.volume,
                        'protocol': edge.protocol
                    }
                    for edge in sorted(edges, key=lambda x: x.volume, reverse=True)[:5]
                ]
            }
        }
    
    def _identify_suspicious_flows(self, nodes: Dict[str, DataFlowNode], edges: List[DataFlowEdge]) -> List[Dict[str, Any]]:
        """Identify suspicious data flows"""
        suspicious = []
        
        for edge in edges:
            suspicion_score = 0
            reasons = []
            
            # High volume transfers
            if edge.volume > 100 * 1024 * 1024:  # 100MB
                suspicion_score += 3
                reasons.append("High volume data transfer")
            
            # High risk protocol
            if edge.protocol in ['unknown', 'custom']:
                suspicion_score += 2
                reasons.append("Unusual protocol usage")
            
            # High risk destination
            dest_node = nodes.get(edge.destination_id)
            if dest_node and dest_node.risk_score >= 7:
                suspicion_score += 2
                reasons.append("High-risk destination")
            
            # Off-hours activity
            if edge.timestamp.hour < 6 or edge.timestamp.hour > 22:
                suspicion_score += 1
                reasons.append("Off-hours activity")
            
            if suspicion_score >= 3:
                suspicious.append({
                    'edge_id': edge.edge_id,
                    'source': edge.source_id,
                    'destination': edge.destination_id,
                    'suspicion_score': suspicion_score,
                    'reasons': reasons,
                    'volume': edge.volume,
                    'protocol': edge.protocol,
                    'timestamp': edge.timestamp.isoformat()
                })
        
        return sorted(suspicious, key=lambda x: x['suspicion_score'], reverse=True)
    
    def _generate_flow_paths(self, nodes: Dict[str, DataFlowNode], edges: List[DataFlowEdge]) -> List[DataFlowPath]:
        """Generate complete data flow paths"""
        paths = []
        
        # Build adjacency list
        adjacency = defaultdict(list)
        for edge in edges:
            adjacency[edge.source_id].append((edge.destination_id, edge))
        
        # Find paths from sources to destinations
        visited = set()
        
        def find_path(current_node: str, current_path: List[DataFlowEdge], visited_nodes: set):
            if len(current_path) > 5:  # Limit path length
                return
            
            if current_node in visited_nodes:
                return
            
            visited_nodes.add(current_node)
            
            for next_node, edge in adjacency[current_node]:
                new_path = current_path + [edge]
                
                # Check if this is a complete path (ends at a destination)
                if next_node in nodes and nodes[next_node].node_type in ['destination', 'external']:
                    path_nodes = []
                    all_nodes = set()
                    
                    for e in new_path:
                        all_nodes.add(e.source_id)
                        all_nodes.add(e.destination_id)
                    
                    for node_id in all_nodes:
                        if node_id in nodes:
                            path_nodes.append(nodes[node_id])
                    
                    path = DataFlowPath(
                        path_id=f"path_{len(paths)}_{int(time.time())}",
                        path_type="data_transfer",
                        nodes=path_nodes,
                        edges=new_path,
                        total_volume=sum(e.volume for e in new_path),
                        risk_score=max(self._severity_weight(e.risk_level) for e in new_path),
                        duration=new_path[-1].timestamp - new_path[0].timestamp,
                        description=f"Data flow from {new_path[0].source_id} to {new_path[-1].destination_id}"
                    )
                    paths.append(path)
                
                # Continue exploring
                find_path(next_node, new_path, visited_nodes.copy())
        
        # Start from source nodes
        source_nodes = [node_id for node_id, node in nodes.items() if node.node_type in ['source', 'application']]
        
        for source in source_nodes:
            find_path(source, [], set())
        
        return paths[:10]  # Return top 10 paths
    
    def _analyze_security(self, evidence_items: List[EvidenceItem], 
                        accounts: Optional[List[Account]] = None,
                        credentials: Optional[List[Credential]] = None) -> Dict[str, Any]:
        """Analyze security-related evidence"""
        security_items = [item for item in evidence_items if any(
            keyword in item.data_type.lower() or keyword in item.source.lower()
            for keyword in ['security', 'vulnerability', 'auth', 'credential', 'privilege']
        )]
        
        # Identity Correlation
        verified_identities = []
        if accounts:
            browser_logins = [item for item in evidence_items if item.type == 'browser_history' and 'login' in item.description.lower()]
            for account in accounts:
                for login in browser_logins:
                    if account.username in login.description and extract_domain(login.metadata.get('url', '')) in account.service:
                        verified_identities.append({
                            "username": account.username,
                            "service": account.service,
                            "source": "OSINT and Browser History Correlation"
                        })

        if not security_items and not verified_identities:
            return {'summary': 'No security-related evidence found.'}
        
        # Security categorization
        vulnerability_items = [item for item in security_items if 'vulnerability' in item.data_type.lower()]
        authentication_items = [item for item in security_items if 'auth' in item.data_type.lower()]
        privilege_items = [item for item in security_items if 'privilege' in item.data_type.lower()]
        
        # Risk assessment
        critical_vulns = [item for item in vulnerability_items if item.severity == 'critical']
        high_vulns = [item for item in vulnerability_items if item.severity == 'high']
        
        # Account security analysis (if data available)
        account_analysis = {}
        if accounts and credentials:
            # This would integrate with the security auditor
            account_analysis = {
                'total_accounts': len(accounts),
                'total_credentials': len(credentials),
                'security_issues': len(security_items)
            }
        
        return {
            'summary': f"Found {len(security_items)} security-related items including {len(vulnerability_items)} vulnerabilities and {len(verified_identities)} verified identities.",
            'verified_identities': verified_identities,
            'vulnerability_analysis': {
                'total_vulnerabilities': len(vulnerability_items),
                'critical_vulnerabilities': len(critical_vulns),
                'high_vulnerabilities': len(high_vulns),
                'vulnerability_types': dict(Counter(item.data_type for item in vulnerability_items)),
                'affected_systems': list(set(item.metadata.get('system', 'unknown') for item in vulnerability_items))
            },
            'authentication_analysis': {
                'total_auth_events': len(authentication_items),
                'failed_attempts': len([item for item in authentication_items if 'failed' in item.description.lower()]),
                'unsuccessful_logins': len([item for item in authentication_items if 'unsuccessful' in item.description.lower()])
            },
            'privilege_analysis': {
                'total_privilege_events': len(privilege_items),
                'escalation_attempts': len([item for item in privilege_items if 'escalation' in item.description.lower()]),
                'abuse_patterns': len([item for item in privilege_items if 'abuse' in item.description.lower()])
            },
            'account_analysis': account_analysis,
            'security_recommendations': self._generate_security_recommendations(security_items)
        }
    
    def _generate_security_recommendations(self, security_items: List[EvidenceItem]) -> List[str]:
        """Generate security-specific recommendations"""
        recommendations = []
        
        vulnerability_count = len([item for item in security_items if 'vulnerability' in item.data_type.lower()])
        auth_issues = len([item for item in security_items if 'failed' in item.description.lower()])
        privilege_issues = len([item for item in security_items if 'privilege' in item.data_type.lower()])
        
        if vulnerability_count > 0:
            recommendations.append(f"Address {vulnerability_count} identified vulnerabilities through patching and remediation")
        
        if auth_issues > 5:
            recommendations.append("Investigate authentication failures - possible brute force or credential stuffing attacks")
        
        if privilege_issues > 0:
            recommendations.append("Review privilege escalation attempts and strengthen access controls")
        
        critical_items = [item for item in security_items if item.severity == 'critical']
        if critical_items:
            recommendations.append(f"IMMEDIATE: Address {len(critical_items)} critical security issues")
        
        return recommendations
    
    def _analyze_behavioral_patterns(self, evidence_items: List[EvidenceItem]) -> Dict[str, Any]:
        """Analyze behavioral patterns from evidence"""
        behavioral_items = [item for item in evidence_items if any(
            keyword in item.data_type.lower() or keyword in item.source.lower()
            for keyword in ['behavior', 'pattern', 'anomaly', 'activity']
        )]
        
        if not behavioral_items:
            return {'summary': 'No behavioral evidence found.'}
        
        # Pattern analysis
        patterns = [item for item in behavioral_items if 'pattern' in item.data_type.lower()]
        anomalies = [item for item in behavioral_items if 'anomaly' in item.data_type.lower()]
        
        # Risk distribution
        risk_distribution = dict(Counter(item.severity for item in behavioral_items))
        
        # Entity analysis
        entities = set()
        for item in behavioral_items:
            if item.metadata:
                if 'entity' in item.metadata:
                    entities.add(item.metadata['entity'])
                if 'user' in item.metadata:
                    entities.add(item.metadata['user'])
                if 'process' in item.metadata:
                    entities.add(item.metadata['process'])
        
        return {
            'summary': f"Analyzed {len(behavioral_items)} behavioral items across {len(entities)} entities",
            'pattern_analysis': {
                'total_patterns': len(patterns),
                'high_risk_patterns': len([p for p in patterns if p.severity in ['critical', 'high']]),
                'pattern_types': dict(Counter(item.data_type for item in patterns)),
                'confidence_distribution': dict(Counter(item.metadata.get('confidence', 'unknown') for item in patterns))
            },
            'anomaly_analysis': {
                'total_anomalies': len(anomalies),
                'severity_distribution': dict(Counter(item.severity for item in anomalies)),
                'anomaly_types': dict(Counter(item.data_type for item in anomalies)),
                'deviation_scores': [item.metadata.get('deviation_score', 0) for item in anomalies if item.metadata.get('deviation_score')]
            },
            'entity_analysis': {
                'total_entities': len(entities),
                'high_risk_entities': len([e for e in entities if any(
                    item.severity in ['critical', 'high']
                    for item in behavioral_items
                    if item.metadata and item.metadata.get('entity') == e
                )]),
                'entity_types': dict(Counter(item.metadata.get('entity_type', 'unknown') for item in behavioral_items if item.metadata))
            },
            'behavioral_recommendations': self._generate_behavioral_recommendations(behavioral_items)
        }
    
    def _generate_behavioral_recommendations(self, behavioral_items: List[EvidenceItem]) -> List[str]:
        """Generate behavioral analysis recommendations"""
        recommendations = []
        
        anomaly_count = len([item for item in behavioral_items if 'anomaly' in item.data_type.lower()])
        high_risk_patterns = len([item for item in behavioral_items if item.severity in ['critical', 'high']])
        
        if anomaly_count > 5:
            recommendations.append(f"Investigate {anomaly_count} behavioral anomalies for potential security incidents")
        
        if high_risk_patterns > 3:
            recommendations.append(f"Address {high_risk_patterns} high-risk behavioral patterns through enhanced monitoring")
        
        # Check for repeated entities
        entities = defaultdict(int)
        for item in behavioral_items:
            if item.metadata and 'entity' in item.metadata:
                entities[item.metadata['entity']] += 1
        
        suspicious_entities = [entity for entity, count in entities.items() if count > 10]
        if suspicious_entities:
            recommendations.append(f"Monitor entities with high activity: {', '.join(suspicious_entities[:3])}")
        
        return recommendations
    
    def _assess_overall_risk(self, evidence_items: List[EvidenceItem]) -> Dict[str, Any]:
        """Assess overall risk level"""
        if not evidence_items:
            return {'overall_risk': 'low', 'risk_score': 0, 'risk_factors': []}
        
        # Calculate risk score
        total_score = 0
        risk_factors = []
        
        severity_weights = {'critical': 10, 'high': 7, 'medium': 4, 'low': 1}
        severity_counts = Counter(item.severity for item in evidence_items)
        
        for severity, count in severity_counts.items():
            weight = severity_weights.get(severity, 0)
            total_score += weight * count
            
            if severity == 'critical' and count > 0:
                risk_factors.append(f"{count} critical severity items")
            elif severity == 'high' and count > 5:
                risk_factors.append(f"{count} high severity items")
            elif severity == 'medium' and count > 20:
                risk_factors.append(f"{count} medium severity items")
        
        # Risk level determination
        if total_score >= 100:
            risk_level = 'critical'
        elif total_score >= 50:
            risk_level = 'high'
        elif total_score >= 20:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        # Additional risk factors
        data_exfil_risk = len([item for item in evidence_items if 'exfil' in item.description.lower()])
        if data_exfil_risk > 0:
            risk_factors.append(f"Potential data exfiltration ({data_exfil_risk} indicators)")
        
        unauthorized_risk = len([item for item in evidence_items if 'unauthorized' in item.description.lower()])
        if unauthorized_risk > 0:
            risk_factors.append(f"Unauthorized access patterns ({unauthorized_risk} indicators)")
        
        return {
            'overall_risk': risk_level,
            'risk_score': total_score,
            'risk_factors': risk_factors,
            'severity_distribution': dict(severity_counts),
            'risk_trend': 'stable',  # Would require historical data
            'mitigation_priority': self._determine_mitigation_priority(risk_level, total_score)
        }
    
    def _determine_mitigation_priority(self, risk_level: str, risk_score: int) -> str:
        """Determine mitigation priority"""
        if risk_level == 'critical':
            return 'IMMEDIATE - Within 1 hour'
        elif risk_level == 'high':
            return 'HIGH - Within 24 hours'
        elif risk_level == 'medium':
            return 'MEDIUM - Within 7 days'
        else:
            return 'LOW - Within 30 days'
    
    def _generate_recommendations(self, evidence_items: List[EvidenceItem]) -> Dict[str, Any]:
        """Generate comprehensive recommendations"""
        recommendations = {
            'immediate_actions': [],
            'short_term_actions': [],
            'long_term_actions': [],
            'policy_recommendations': [],
            'technical_recommendations': []
        }
        
        # Categorize recommendations based on evidence
        critical_items = [item for item in evidence_items if item.severity == 'critical']
        high_items = [item for item in evidence_items if item.severity == 'high']
        
        if critical_items:
            recommendations['immediate_actions'].append(
                f"Address {len(critical_items)} critical issues immediately"
            )
            recommendations['immediate_actions'].append(
                "Isolate affected systems and contain potential damage"
            )
        
        if high_items:
            recommendations['short_term_actions'].append(
                f"Resolve {len(high_items)} high-priority issues within 24 hours"
            )
        
        # Technical recommendations based on evidence types
        evidence_types = set(item.data_type for item in evidence_items)
        
        if 'network_packet' in evidence_types:
            recommendations['technical_recommendations'].append(
                "Enhance network monitoring and intrusion detection"
            )
        
        if 'pii_data' in evidence_types:
            recommendations['technical_recommendations'].append(
                "Implement data loss prevention (DLP) controls"
            )
        
        if 'security_vulnerability' in evidence_types:
            recommendations['technical_recommendations'].append(
                "Establish regular vulnerability scanning and patch management"
            )
        
        if 'behavioral_anomaly' in evidence_types:
            recommendations['technical_recommendations'].append(
                "Deploy user and entity behavior analytics (UEBA)"
            )
        
        # Policy recommendations
        recommendations['policy_recommendations'].extend([
            "Review and update incident response procedures",
            "Enhance security awareness training programs",
            "Implement regular security assessments",
            "Establish data classification and handling policies"
        ])
        
        # Long-term strategic recommendations
        recommendations['long_term_actions'].extend([
            "Develop comprehensive security architecture roadmap",
            "Implement zero-trust security model",
            "Establish continuous monitoring capabilities",
            "Create security metrics and KPI framework"
        ])
        
        return recommendations
    
    def _generate_detailed_findings(self, evidence_items: List[EvidenceItem]) -> List[Dict[str, Any]]:
        """Generate detailed findings from evidence"""
        findings = []
        
        # Group evidence by severity and importance
        critical_findings = [
            {
                'id': item.id,
                'description': item.description,
                'source': item.source,
                'type': item.data_type,
                'severity': item.severity,
                'timestamp': item.timestamp.isoformat(),
                'metadata': item.metadata,
                'recommendation': self._generate_finding_recommendation(item)
            }
            for item in sorted(evidence_items, key=lambda x: self._severity_weight(x.severity), reverse=True)
            if item.severity in ['critical', 'high']
        ]
        
        # Add medium findings if limited critical/high
        if len(critical_findings) < 10:
            medium_findings = [
                {
                    'id': item.id,
                    'description': item.description,
                    'source': item.source,
                    'type': item.data_type,
                    'severity': item.severity,
                    'timestamp': item.timestamp.isoformat(),
                    'metadata': item.metadata,
                    'recommendation': self._generate_finding_recommendation(item)
                }
                for item in sorted(evidence_items, key=lambda x: self._severity_weight(x.severity), reverse=True)
                if item.severity == 'medium'
            ][:10]
            critical_findings.extend(medium_findings)
        
        return critical_findings[:20]  # Return top 20 findings
    
    def _generate_finding_recommendation(self, item: EvidenceItem) -> str:
        """Generate specific recommendation for a finding"""
        if 'vulnerability' in item.data_type.lower():
            return "Patch or mitigate the identified vulnerability immediately"
        elif 'unauthorized' in item.description.lower():
            return "Investigate unauthorized access and strengthen authentication"
        elif 'exfil' in item.description.lower():
            return "Implement data loss prevention and monitor data transfers"
        elif 'anomaly' in item.data_type.lower():
            return "Investigate behavioral anomaly for potential security incident"
        elif 'malicious' in item.description.lower():
            return "Isolate affected system and conduct malware analysis"
        else:
            return "Review and address the identified security issue"
    
    def _generate_visualizations(self, evidence_items: List[EvidenceItem]) -> Dict[str, Any]:
        """Generate visualizations for the report"""
        if not PLOTTING_AVAILABLE:
            return {'message': 'Matplotlib/Seaborn not available for visualizations'}
        
        visualizations = {}
        
        try:
            # Severity distribution chart
            severity_counts = Counter(item.severity for item in evidence_items)
            plt.figure(figsize=(10, 6))
            plt.bar(severity_counts.keys(), severity_counts.values())
            plt.title('Evidence Severity Distribution')
            plt.xlabel('Severity')
            plt.ylabel('Count')
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.savefig('severity_distribution.png')
            plt.close()
            visualizations['severity_chart'] = 'severity_distribution.png'
            
            # Timeline chart
            if evidence_items:
                timestamps = [item.timestamp for item in evidence_items]
                plt.figure(figsize=(12, 6))
                plt.hist(timestamps, bins=50, alpha=0.7)
                plt.title('Evidence Timeline')
                plt.xlabel('Time')
                plt.ylabel('Count')
                plt.xticks(rotation=45)
                plt.tight_layout()
                plt.savefig('evidence_timeline.png')
                plt.close()
                visualizations['timeline_chart'] = 'evidence_timeline.png'
            
            # Source distribution
            source_counts = Counter(item.source for item in evidence_items)
            plt.figure(figsize=(10, 6))
            plt.pie(source_counts.values(), labels=source_counts.keys(), autopct='%1.1f%%')
            plt.title('Evidence by Source')
            plt.axis('equal')
            plt.tight_layout()
            plt.savefig('source_distribution.png')
            plt.close()
            visualizations['source_chart'] = 'source_distribution.png'

            # Privacy Heatmap
            privacy_heatmap_path = self._generate_privacy_heatmap(evidence_items)
            if privacy_heatmap_path:
                visualizations['privacy_heatmap'] = privacy_heatmap_path
            
        except Exception as e:
            visualizations['error'] = f"Error generating visualizations: {str(e)}"
        
        return visualizations

    def _generate_privacy_heatmap(self, evidence_items: List[EvidenceItem]) -> Optional[str]:
        """
        Generates a Heatmap: X-Axis = Days, Y-Axis = Service Category (Social, Shopping, etc.)
        Color = Intensity of data collection (frequency of visits + cookies).
        """
        import pandas as pd
        import seaborn as sns
        
        # 1. Convert EvidenceItems to DataFrame
        data = []
        for item in evidence_items:
            if item.type in ['browser_history', 'cookie', 'network_log']:
                domain = extract_domain(item.metadata.get('url', ''))
                company = self.entity_resolver.resolve(domain)
                
                data.append({
                    'date': item.timestamp.date(),
                    'company': company,
                    'count': 1
                })
                
        if not data:
            return None

        df = pd.DataFrame(data)
        
        # 2. Pivot for Heatmap
        pivot_table = df.pivot_table(index='company', columns='date', values='count', aggfunc='sum')
        
        # 3. Plot
        plt.figure(figsize=(12, 8))
        sns.heatmap(pivot_table, cmap="YlOrRd", annot=True)
        plt.title("Daily Data Extraction by Company")
        plt.savefig('privacy_heatmap.png')
        plt.close()

        return 'privacy_heatmap.png'
    
    def _generate_data_flow_diagrams(self, evidence_items: List[EvidenceItem]) -> Dict[str, Any]:
        """Generate data flow diagrams"""
        if not GRAPHVIZ_AVAILABLE:
            return {'message': 'Graphviz not available for flow diagrams'}
        
        diagrams = {}
        
        try:
            # Create main data flow graph
            dot = graphviz.Digraph('DataFlow', comment='Data Flow Analysis')
            dot.attr(rankdir='LR', size='12,8')
            
            # Extract nodes and edges from evidence
            nodes = set()
            edges = []
            
            for item in evidence_items:
                if item.metadata:
                    if 'source_entity' in item.metadata:
                        source = item.metadata['source_entity']
                        nodes.add(source)
                        dot.node(source, source, shape='box')
                    
                    if 'destination_entity' in item.metadata:
                        dest = item.metadata['destination_entity']
                        nodes.add(dest)
                        dot.node(dest, dest, shape='ellipse')
                    
                    if 'source_entity' in item.metadata and 'destination_entity' in item.metadata:
                        edges.append((item.metadata['source_entity'], item.metadata['destination_entity']))
                        dot.edge(item.metadata['source_entity'], item.metadata['destination_entity'])
            
            # Render the graph
            dot.render('data_flow_graph', format='png', cleanup=True)
            diagrams['main_flow'] = 'data_flow_graph.png'
            
        except Exception as e:
            diagrams['error'] = f"Error generating flow diagrams: {str(e)}"
        
        return diagrams

def generate_enhanced_report(evidence_items: List[EvidenceItem],
                           accounts: Optional[List[Account]] = None,
                           credentials: Optional[List[Credential]] = None,
                           config: Optional[ForensicConfig] = None,
                           include_visualizations: bool = True) -> Dict[str, Any]:
    """Generate enhanced forensic report with data flow analysis"""
    engine = EnhancedReportingEngine(config)
    return engine.generate_comprehensive_report(
        evidence_items, accounts, credentials, include_visualizations
    )
