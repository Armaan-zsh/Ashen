"""
Advanced Behavioral Intelligence Engine
Analyzes patterns, anomalies, and behavioral indicators across digital activities
"""

import time
import numpy as np
from typing import Dict, List, Any, Optional, Generator, Tuple, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import logging
import json

try:
    from sklearn.cluster import DBSCAN
    from sklearn.preprocessing import StandardScaler
    from sklearn.ensemble import IsolationForest
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

from ..core.models import EvidenceItem, ScannerType
from ..core.config import ForensicConfig
from .base import BaseScanner

@dataclass
class BehavioralPattern:
    """Represents a detected behavioral pattern"""
    pattern_id: str
    pattern_type: str
    description: str
    confidence: float
    frequency: int
    time_span: timedelta
    associated_entities: List[str]
    risk_level: str
    indicators: List[str]

@dataclass
class BehavioralAnomaly:
    """Represents a detected behavioral anomaly"""
    anomaly_id: str
    anomaly_type: str
    description: str
    severity: str
    deviation_score: float
    baseline_behavior: str
    current_behavior: str
    timestamp: datetime
    context: Dict[str, Any]

@dataclass
class BehaviorProfile:
    """Represents behavioral profile for an entity"""
    entity_id: str
    entity_type: str
    profile_type: str
    baseline_patterns: List[str]
    typical_behaviors: Dict[str, Any]
    risk_indicators: List[str]
    behavior_score: float
    last_updated: datetime
    activity_timeline: List[Dict[str, Any]]

@dataclass
class BehaviorCluster:
    """Represents a cluster of similar behaviors"""
    cluster_id: str
    cluster_type: str
    members: List[str]
    common_patterns: List[str]
    risk_level: str
    description: str

class BehavioralIntelligenceEngine(BaseScanner):
    """Advanced behavioral intelligence and pattern analysis"""
    
    def __init__(self, config: Optional[ForensicConfig] = None):
        super().__init__(ScannerType.BEHAVIORAL_INTELLIGENCE, config)
        self.behavioral_patterns = {}
    
    def scan(self) -> Generator[EvidenceItem, None, None]:
        """Main scan method for behavioral intelligence."""
        yield EvidenceItem(
            id="behavioral_intel_test",
            source="behavioral_intelligence",
            type="test",
            content="Behavioral intelligence initialized successfully",
            metadata={"test": True}
        )
    """Advanced behavioral analysis and pattern recognition"""
    
    def __init__(self, config: Optional[ForensicConfig] = None):
        super().__init__(ScannerType.BEHAVIORAL_INTELLIGENCE, config)
        self.behavior_profiles = {}
        self.detected_patterns = []
        self.anomalies = []
        self.behavior_clusters = {}
        self.activity_timeline = deque(maxlen=10000)
        
        # Pattern libraries
        self.malicious_patterns = self._init_malicious_patterns()
        self.normal_patterns = self._init_normal_patterns()
        self.risk_indicators = self._init_risk_indicators()
        
        # Analysis parameters
        self.anomaly_threshold = 0.7
        self.pattern_confidence_threshold = 0.6
        self.cluster_min_samples = 2
        self.time_window_hours = 24
        
    def _init_malicious_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize known malicious behavioral patterns"""
        return {
            'data_exfiltration': {
                'indicators': [
                    'large_file_transfers',
                    'unusual_destinations',
                    'off_hours_activity',
                    'rapid_data_access',
                    'compression_tools_usage'
                ],
                'thresholds': {
                    'data_volume_mb': 100,
                    'unique_destinations': 5,
                    'off_hours_start': 22,
                    'off_hours_end': 6,
                    'access_frequency_per_hour': 50
                },
                'risk_score': 9.0
            },
            'credential_theft': {
                'indicators': [
                    'password_tool_usage',
                    'browser_credential_access',
                    'system_file_access',
                    'network_scanning',
                    'privilege_escalation_attempts'
                ],
                'thresholds': {
                    'credential_access_count': 3,
                    'system_files_accessed': 10,
                    'network_ports_scanned': 100,
                    'privilege_attempts': 5
                },
                'risk_score': 8.5
            },
            'lateral_movement': {
                'indicators': [
                    'remote_access_tools',
                    'multiple_host_connections',
                    'authentication_attempts',
                    'service_discovery',
                    'pass_the_hash_attempts'
                ],
                'thresholds': {
                    'unique_hosts_connected': 3,
                    'auth_failures': 10,
                    'services_discovered': 20,
                    'remote_tools_used': 2
                },
                'risk_score': 7.5
            },
            'persistence_mechanisms': {
                'indicators': [
                    'registry_modifications',
                    'scheduled_task_creation',
                    'startup_programs',
                    'service_installation',
                    'wmi_persistence'
                ],
                'thresholds': {
                    'registry_changes': 5,
                    'scheduled_tasks': 2,
                    'startup_items': 3,
                    'new_services': 1
                },
                'risk_score': 7.0
            },
            'command_control': {
                'indicators': [
                    'dns_queries_to_c2',
                    'beaconing_activity',
                    'encrypted_communications',
                    'regular_connection_intervals',
                    'user_agent_anomalies'
                ],
                'thresholds': {
                    'dns_query_frequency': 10,
                    'connection_interval_variance': 0.1,
                    'encryption_usage': 0.8,
                    'beacon_interval_minutes': 5
                },
                'risk_score': 8.0
            },
            'privilege_escalation': {
                'indicators': [
                    'exploit_usage',
                    'vulnerability_scanning',
                    'admin_tool_usage',
                    'system_configuration_changes',
                    'token_manipulation'
                ],
                'thresholds': {
                    'exploit_attempts': 3,
                    'vulnerabilities_scanned': 50,
                    'admin_tools_used': 5,
                    'system_changes': 10
                },
                'risk_score': 8.5
            }
        }
    
    def _init_normal_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize normal behavioral patterns"""
        return {
            'regular_work_activity': {
                'indicators': [
                    'business_hours_activity',
                    'consistent_application_usage',
                    'normal_data_access_patterns',
                    'regular_communication',
                    'standard_network_usage'
                ],
                'characteristics': {
                    'activity_hours': (8, 18),
                    'application_consistency': 0.7,
                    'data_access_volume_mb': 10,
                    'communication_frequency': 20
                }
            },
            'system_maintenance': {
                'indicators': [
                    'scheduled_updates',
                    'backup_operations',
                    'system_scans',
                    'log_rotation',
                    'health_checks'
                ],
                'characteristics': {
                    'regular_intervals': True,
                    'system_processes': True,
                    'low_user_interaction': True
                }
            },
            'development_activity': {
                'indicators': [
                    'code_compilation',
                    'file_editing',
                    'debugging_sessions',
                    'version_control',
                    'testing_operations'
                ],
                'characteristics': {
                    'ide_usage': True,
                    'file_operations': 50,
                    'build_processes': 5
                }
            }
        }
    
    def _init_risk_indicators(self) -> Dict[str, Dict[str, Any]]:
        """Initialize behavioral risk indicators"""
        return {
            'high_frequency_actions': {
                'threshold': 100,
                'time_window_minutes': 60,
                'risk_weight': 0.3
            },
            'unusual_time_activity': {
                'early_hour': 6,
                'late_hour': 22,
                'risk_weight': 0.4
            },
            'unusual_destinations': {
                'known_malicious_domains': [],
                'risk_weight': 0.5
            },
            'privilege_escalation': {
                'admin_actions': ['registry', 'system32', 'services'],
                'risk_weight': 0.6
            },
            'data_anomaly': {
                'volume_threshold_mb': 50,
                'access_patterns': ['bulk_access', 'rapid_download'],
                'risk_weight': 0.4
            }
        }
    
    def analyze_behavioral_patterns(self, activities: List[Dict[str, Any]]) -> Generator[EvidenceItem, None, None]:
        """Analyze activities for behavioral patterns and anomalies"""
        try:
            # Process activities and update timeline
            for activity in activities:
                self._add_to_timeline(activity)
            
            # Update behavior profiles
            self._update_behavior_profiles(activities)
            
            # Detect patterns
            patterns = self._detect_behavioral_patterns(activities)
            
            for pattern in patterns:
                self.detected_patterns.append(pattern)
                
                yield EvidenceItem(
                    id=f"behavioral_pattern_{pattern.pattern_id}_{int(time.time())}",
                    source="behavioral_intelligence",
                    data_type="behavioral_pattern",
                    description=f"Behavioral Pattern: {pattern.pattern_type} - {pattern.description}",
                    severity=pattern.risk_level,
                    metadata=asdict(pattern)
                )
            
            # Detect anomalies
            anomalies = self._detect_behavioral_anomalies(activities)
            
            for anomaly in anomalies:
                self.anomalies.append(anomaly)
                
                yield EvidenceItem(
                    id=f"behavioral_anomaly_{anomaly.anomaly_id}_{int(time.time())}",
                    source="behavioral_intelligence",
                    data_type="behavioral_anomaly",
                    description=f"Behavioral Anomaly: {anomaly.anomaly_type} - {anomaly.description}",
                    severity=anomaly.severity,
                    metadata=asdict(anomaly)
                )
            
            # Cluster similar behaviors
            clusters = self._cluster_behaviors(activities)
            
            for cluster in clusters:
                self.behavior_clusters[cluster.cluster_id] = cluster
                
                yield EvidenceItem(
                    id=f"behavior_cluster_{cluster.cluster_id}_{int(time.time())}",
                    source="behavioral_intelligence",
                    data_type="behavior_cluster",
                    description=f"Behavior Cluster: {cluster.cluster_type} - {cluster.description}",
                    severity=cluster.risk_level,
                    metadata=asdict(cluster)
                )
            
            # Generate behavior profiles
            profiles = self._generate_behavior_profiles(activities)
            
            for profile in profiles:
                self.behavior_profiles[profile.entity_id] = profile
                
                yield EvidenceItem(
                    id=f"behavior_profile_{profile.entity_id}_{int(time.time())}",
                    source="behavioral_intelligence",
                    data_type="behavior_profile",
                    description=f"Behavior Profile: {profile.entity_type} - {profile.entity_id}",
                    severity='medium' if profile.behavior_score < 6.0 else 'low',
                    metadata=asdict(profile)
                )
                
        except Exception as e:
            yield EvidenceItem(
                id="behavioral_analysis_error",
                source="behavioral_intelligence",
                data_type="error",
                description=f"Error in behavioral analysis: {str(e)}",
                severity="medium",
                metadata={"error": str(e)}
            )
    
    def _add_to_timeline(self, activity: Dict[str, Any]):
        """Add activity to timeline"""
        timeline_entry = {
            'timestamp': activity.get('timestamp', datetime.now()),
            'entity': activity.get('entity', 'unknown'),
            'action': activity.get('action', 'unknown'),
            'details': activity.get('details', {}),
            'risk_score': activity.get('risk_score', 0.0)
        }
        self.activity_timeline.append(timeline_entry)
    
    def _update_behavior_profiles(self, activities: List[Dict[str, Any]]):
        """Update behavior profiles based on new activities"""
        # Group activities by entity
        entity_activities = defaultdict(list)
        for activity in activities:
            entity = activity.get('entity', 'unknown')
            entity_activities[entity].append(activity)
        
        # Update or create profiles
        for entity, entity_acts in entity_activities.items():
            if entity not in self.behavior_profiles:
                # Create new profile
                profile = BehaviorProfile(
                    entity_id=entity,
                    entity_type=self._classify_entity_type(entity, entity_acts),
                    profile_type='dynamic',
                    baseline_patterns=[],
                    typical_behaviors={},
                    risk_indicators=[],
                    behavior_score=5.0,
                    last_updated=datetime.now(),
                    activity_timeline=[]
                )
                self.behavior_profiles[entity] = profile
            
            # Update existing profile
            profile = self.behavior_profiles[entity]
            profile.last_updated = datetime.now()
            profile.activity_timeline.extend([
                {
                    'timestamp': act.get('timestamp', datetime.now()),
                    'action': act.get('action', 'unknown'),
                    'risk_score': act.get('risk_score', 0.0)
                }
                for act in entity_acts[-100:]  # Keep last 100 activities
            ])
            
            # Update typical behaviors
            profile.typical_behaviors = self._analyze_typical_behaviors(entity_acts)
            
            # Update behavior score
            profile.behavior_score = self._calculate_behavior_score(profile)
    
    def _classify_entity_type(self, entity: str, activities: List[Dict[str, Any]]) -> str:
        """Classify entity type based on activities"""
        actions = [act.get('action', '').lower() for act in activities]
        
        # User patterns
        user_indicators = ['browse', 'login', 'email', 'document', 'chat']
        if any(indicator in ' '.join(actions) for indicator in user_indicators):
            return 'user'
        
        # System patterns
        system_indicators = ['service', 'process', 'system', 'driver', 'kernel']
        if any(indicator in ' '.join(actions) for indicator in system_indicators):
            return 'system'
        
        # Application patterns
        app_indicators = ['execute', 'install', 'update', 'config', 'plugin']
        if any(indicator in ' '.join(actions) for indicator in app_indicators):
            return 'application'
        
        # Network patterns
        network_indicators = ['connect', 'transfer', 'packet', 'dns', 'http']
        if any(indicator in ' '.join(actions) for indicator in network_indicators):
            return 'network'
        
        return 'unknown'
    
    def _analyze_typical_behaviors(self, activities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze typical behaviors for an entity"""
        if not activities:
            return {}
        
        # Time patterns
        timestamps = [act.get('timestamp', datetime.now()) for act in activities]
        hours = [ts.hour for ts in timestamps]
        
        # Action frequency
        actions = [act.get('action', 'unknown') for act in activities]
        action_counts = defaultdict(int)
        for action in actions:
            action_counts[action] += 1
        
        # Risk distribution
        risk_scores = [act.get('risk_score', 0.0) for act in activities]
        
        return {
            'most_common_actions': sorted(action_counts.items(), key=lambda x: x[1], reverse=True)[:5],
            'activity_hours': {
                'most_active_hour': max(set(hours), key=hours.count) if hours else 12,
                'business_hours_activity': sum(1 for h in hours if 8 <= h <= 18) / len(hours) if hours else 0,
                'off_hours_activity': sum(1 for h in hours if h < 8 or h > 18) / len(hours) if hours else 0
            },
            'risk_profile': {
                'average_risk': np.mean(risk_scores) if risk_scores else 0.0,
                'max_risk': max(risk_scores) if risk_scores else 0.0,
                'high_risk_percentage': sum(1 for r in risk_scores if r > 7.0) / len(risk_scores) if risk_scores else 0.0
            },
            'activity_frequency': len(activities) / max(1, (max(timestamps) - min(timestamps)).total_seconds() / 3600) if len(timestamps) > 1 else 0
        }
    
    def _calculate_behavior_score(self, profile: BehaviorProfile) -> float:
        """Calculate overall behavior score for a profile"""
        score = 5.0  # Base score
        
        # Risk from typical behaviors
        if profile.typical_behaviors:
            avg_risk = profile.typical_behaviors.get('risk_profile', {}).get('average_risk', 0.0)
            score -= avg_risk * 0.3
        
        # Off-hours activity penalty
        off_hours_pct = profile.typical_behaviors.get('activity_hours', {}).get('off_hours_activity', 0.0)
        if off_hours_pct > 0.3:
            score -= off_hours_pct * 2.0
        
        # High-risk actions penalty
        high_risk_pct = profile.typical_behaviors.get('risk_profile', {}).get('high_risk_percentage', 0.0)
        if high_risk_pct > 0.2:
            score -= high_risk_pct * 3.0
        
        # Activity frequency (very high or very low can be suspicious)
        freq = profile.typical_behaviors.get('activity_frequency', 0.0)
        if freq > 100:  # Very high activity
            score -= 1.0
        elif freq < 0.1:  # Very low activity
            score -= 0.5
        
        return max(0.0, min(10.0, score))
    
    def _detect_behavioral_patterns(self, activities: List[Dict[str, Any]]) -> List[BehavioralPattern]:
        """Detect behavioral patterns in activities"""
        patterns = []
        
        # Check for malicious patterns
        for pattern_name, pattern_config in self.malicious_patterns.items():
            matched_activities = self._match_pattern(activities, pattern_config)
            
            if len(matched_activities) >= 3:  # Minimum pattern occurrences
                confidence = min(1.0, len(matched_activities) / 10.0)
                
                if confidence >= self.pattern_confidence_threshold:
                    pattern = BehavioralPattern(
                        pattern_id=f"{pattern_name}_{int(time.time())}",
                        pattern_type=pattern_name,
                        description=f"Detected {pattern_name.replace('_', ' ').title()} behavior pattern",
                        confidence=confidence,
                        frequency=len(matched_activities),
                        time_span=timedelta(hours=self.time_window_hours),
                        associated_entities=list(set(act.get('entity', 'unknown') for act in matched_activities)),
                        risk_level=self._risk_score_to_severity(pattern_config['risk_score']),
                        indicators=pattern_config['indicators']
                    )
                    patterns.append(pattern)
        
        # Check for normal patterns (for baseline establishment)
        for pattern_name, pattern_config in self.normal_patterns.items():
            matched_activities = self._match_normal_pattern(activities, pattern_config)
            
            if len(matched_activities) >= 5:  # More occurrences for normal patterns
                confidence = min(1.0, len(matched_activities) / 15.0)
                
                pattern = BehavioralPattern(
                    pattern_id=f"normal_{pattern_name}_{int(time.time())}",
                    pattern_type=f"normal_{pattern_name}",
                    description=f"Normal {pattern_name.replace('_', ' ').title()} behavior pattern",
                    confidence=confidence,
                    frequency=len(matched_activities),
                    time_span=timedelta(hours=self.time_window_hours),
                    associated_entities=list(set(act.get('entity', 'unknown') for act in matched_activities)),
                    risk_level='low',
                    indicators=pattern_config['indicators']
                )
                patterns.append(pattern)
        
        return patterns
    
    def _match_pattern(self, activities: List[Dict[str, Any]], pattern_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Match activities against a malicious pattern"""
        matched = []
        indicators = pattern_config['indicators']
        thresholds = pattern_config['thresholds']
        
        for activity in activities:
            score = 0
            total_indicators = len(indicators)
            
            # Check each indicator
            if 'large_file_transfers' in indicators:
                if activity.get('data_volume', 0) > thresholds.get('data_volume_mb', 100) * 1024 * 1024:
                    score += 1
            
            if 'unusual_destinations' in indicators:
                if activity.get('destination_risk', 0) > 0.7:
                    score += 1
            
            if 'off_hours_activity' in indicators:
                hour = activity.get('timestamp', datetime.now()).hour
                if hour < thresholds.get('off_hours_end', 6) or hour > thresholds.get('off_hours_start', 22):
                    score += 1
            
            if 'rapid_data_access' in indicators:
                if activity.get('access_frequency', 0) > thresholds.get('access_frequency_per_hour', 50):
                    score += 1
            
            if 'compression_tools_usage' in indicators:
                if 'compress' in activity.get('action', '').lower():
                    score += 1
            
            # Add more indicator checks as needed...
            
            # If enough indicators match, consider it a match
            if score >= total_indicators * 0.6:  # 60% of indicators
                matched.append(activity)
        
        return matched
    
    def _match_normal_pattern(self, activities: List[Dict[str, Any]], pattern_config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Match activities against a normal pattern"""
        matched = []
        characteristics = pattern_config.get('characteristics', {})
        
        for activity in activities:
            score = 0
            
            # Check business hours
            if 'activity_hours' in characteristics:
                hours = characteristics['activity_hours']
                hour = activity.get('timestamp', datetime.now()).hour
                if hours[0] <= hour <= hours[1]:
                    score += 1
            
            # Check for consistent patterns
            if 'application_consistency' in characteristics:
                # This would require more complex analysis of application usage patterns
                score += 0.5
            
            # Add more characteristic checks...
            
            if score >= 1:  # Lower threshold for normal patterns
                matched.append(activity)
        
        return matched
    
    def _detect_behavioral_anomalies(self, activities: List[Dict[str, Any]]) -> List[BehavioralAnomaly]:
        """Detect behavioral anomalies using statistical analysis"""
        anomalies = []
        
        if not SKLEARN_AVAILABLE or len(activities) < 10:
            return anomalies
        
        try:
            # Extract features for anomaly detection
            features = []
            activity_data = []
            
            for activity in activities:
                feature_vector = [
                    activity.get('risk_score', 0.0),
                    activity.get('timestamp', datetime.now()).hour,
                    activity.get('data_volume', 0) / (1024 * 1024),  # Convert to MB
                    len(activity.get('details', {})),
                    1 if activity.get('destination_risk', 0) > 0.5 else 0
                ]
                features.append(feature_vector)
                activity_data.append(activity)
            
            # Standardize features
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(features)
            
            # Use Isolation Forest for anomaly detection
            iso_forest = IsolationForest(contamination=0.1, random_state=42)
            anomaly_labels = iso_forest.fit_predict(features_scaled)
            
            # Generate anomaly evidence for detected outliers
            for i, label in enumerate(anomaly_labels):
                if label == -1:  # Anomaly detected
                    activity = activity_data[i]
                    anomaly_score = abs(iso_forest.decision_function([features_scaled[i]])[0])
                    
                    if anomaly_score > self.anomaly_threshold:
                        anomaly = BehavioralAnomaly(
                            anomaly_id=f"anomaly_{i}_{int(time.time())}",
                            anomaly_type='statistical_outlier',
                            description=f"Statistical anomaly detected in {activity.get('action', 'unknown')} activity",
                            severity='high' if anomaly_score > 0.8 else 'medium',
                            deviation_score=anomaly_score,
                            baseline_behavior='normal_activity_pattern',
                            current_behavior=json.dumps(activity.get('details', {})),
                            timestamp=activity.get('timestamp', datetime.now()),
                            context={
                                'features': features[i],
                                'entity': activity.get('entity', 'unknown'),
                                'risk_score': activity.get('risk_score', 0.0)
                            }
                        )
                        anomalies.append(anomaly)
            
        except Exception as e:
            logging.error(f"Error in anomaly detection: {str(e)}")
        
        return anomalies
    
    def _cluster_behaviors(self, activities: List[Dict[str, Any]]) -> List[BehaviorCluster]:
        """Cluster similar behaviors"""
        clusters = []
        
        if not SKLEARN_AVAILABLE or len(activities) < self.cluster_min_samples:
            return clusters
        
        try:
            # Extract features for clustering
            features = []
            activity_entities = []
            
            for activity in activities:
                feature_vector = [
                    activity.get('risk_score', 0.0),
                    activity.get('timestamp', datetime.now()).hour,
                    activity.get('data_volume', 0) / (1024 * 1024),  # Convert to MB
                    hash(activity.get('action', 'unknown')) % 100,  # Action hash
                    hash(activity.get('entity', 'unknown')) % 100  # Entity hash
                ]
                features.append(feature_vector)
                activity_entities.append(activity.get('entity', 'unknown'))
            
            # Standardize features
            scaler = StandardScaler()
            features_scaled = scaler.fit_transform(features)
            
            # Use DBSCAN for clustering
            dbscan = DBSCAN(eps=0.5, min_samples=self.cluster_min_samples)
            cluster_labels = dbscan.fit_predict(features_scaled)
            
            # Generate clusters
            unique_labels = set(cluster_labels)
            for label in unique_labels:
                if label != -1:  # Ignore noise points
                    cluster_indices = [i for i, l in enumerate(cluster_labels) if l == label]
                    cluster_activities = [activities[i] for i in cluster_indices]
                    cluster_entities = [activity_entities[i] for i in cluster_indices]
                    
                    # Analyze cluster characteristics
                    common_actions = [act.get('action', 'unknown') for act in cluster_activities]
                    action_counts = defaultdict(int)
                    for action in common_actions:
                        action_counts[action] += 1
                    
                    most_common_action = max(action_counts.items(), key=lambda x: x[1])[0] if action_counts else 'unknown'
                    
                    # Calculate cluster risk
                    cluster_risks = [act.get('risk_score', 0.0) for act in cluster_activities]
                    avg_risk = np.mean(cluster_risks) if cluster_risks else 0.0
                    
                    cluster = BehaviorCluster(
                        cluster_id=f"cluster_{label}_{int(time.time())}",
                        cluster_type=most_common_action,
                        members=list(set(cluster_entities)),
                        common_patterns=list(action_counts.keys()),
                        risk_level=self._risk_score_to_severity(avg_risk),
                        description=f"Cluster of {len(cluster_activities)} similar {most_common_action} behaviors"
                    )
                    clusters.append(cluster)
            
        except Exception as e:
            logging.error(f"Error in behavior clustering: {str(e)}")
        
        return clusters
    
    def _generate_behavior_profiles(self, activities: List[Dict[str, Any]]) -> List[BehaviorProfile]:
        """Generate comprehensive behavior profiles"""
        profiles = []
        
        # Group activities by entity
        entity_activities = defaultdict(list)
        for activity in activities:
            entity = activity.get('entity', 'unknown')
            entity_activities[entity].append(activity)
        
        # Generate profile for each entity
        for entity, entity_acts in entity_activities.items():
            if len(entity_acts) >= 3:  # Minimum activities for profiling
                profile = BehaviorProfile(
                    entity_id=entity,
                    entity_type=self._classify_entity_type(entity, entity_acts),
                    profile_type='comprehensive',
                    baseline_patterns=self._extract_baseline_patterns(entity_acts),
                    typical_behaviors=self._analyze_typical_behaviors(entity_acts),
                    risk_indicators=self._identify_risk_indicators(entity_acts),
                    behavior_score=self._calculate_entity_behavior_score(entity_acts),
                    last_updated=datetime.now(),
                    activity_timeline=[
                        {
                            'timestamp': act.get('timestamp', datetime.now()),
                            'action': act.get('action', 'unknown'),
                            'risk_score': act.get('risk_score', 0.0)
                        }
                        for act in entity_acts[-50:]  # Keep last 50 activities
                    ]
                )
                profiles.append(profile)
        
        return profiles
    
    def _extract_baseline_patterns(self, activities: List[Dict[str, Any]]) -> List[str]:
        """Extract baseline behavioral patterns"""
        patterns = []
        
        # Time patterns
        hours = [act.get('timestamp', datetime.now()).hour for act in activities]
        if hours:
            most_common_hour = max(set(hours), key=hours.count)
            patterns.append(f"peak_activity_hour_{most_common_hour}")
        
        # Action patterns
        actions = [act.get('action', 'unknown') for act in activities]
        action_counts = defaultdict(int)
        for action in actions:
            action_counts[action] += 1
        
        if action_counts:
            most_common_action = max(action_counts.items(), key=lambda x: x[1])[0]
            patterns.append(f"primary_action_{most_common_action}")
        
        # Risk patterns
        risk_scores = [act.get('risk_score', 0.0) for act in activities]
        if risk_scores:
            avg_risk = np.mean(risk_scores)
            if avg_risk < 3.0:
                patterns.append("low_risk_profile")
            elif avg_risk > 7.0:
                patterns.append("high_risk_profile")
            else:
                patterns.append("moderate_risk_profile")
        
        return patterns
    
    def _identify_risk_indicators(self, activities: List[Dict[str, Any]]) -> List[str]:
        """Identify risk indicators in activities"""
        indicators = []
        
        for activity in activities:
            # High-risk actions
            if activity.get('risk_score', 0.0) > 7.0:
                indicators.append("high_risk_activity")
            
            # Unusual timing
            hour = activity.get('timestamp', datetime.now()).hour
            if hour < 6 or hour > 22:
                indicators.append("unusual_timing")
            
            # Large data transfers
            if activity.get('data_volume', 0) > 50 * 1024 * 1024:  # 50MB
                indicators.append("large_data_transfer")
            
            # Suspicious destinations
            if activity.get('destination_risk', 0) > 0.7:
                indicators.append("suspicious_destination")
            
            # Privilege escalation
            action = activity.get('action', '').lower()
            if any(admin_action in action for admin_action in ['admin', 'privilege', 'escalate', 'system']):
                indicators.append("privilege_escalation")
        
        return list(set(indicators))
    
    def _calculate_entity_behavior_score(self, activities: List[Dict[str, Any]]) -> float:
        """Calculate behavior score for an entity"""
        if not activities:
            return 5.0
        
        # Risk-based scoring
        risk_scores = [act.get('risk_score', 0.0) for act in activities]
        avg_risk = np.mean(risk_scores) if risk_scores else 0.0
        
        # Base score inverted from risk
        base_score = 10.0 - avg_risk
        
        # Frequency adjustment
        time_span = (max(act.get('timestamp', datetime.now()) for act in activities) - 
                    min(act.get('timestamp', datetime.now()) for act in activities))
        frequency = len(activities) / max(1, time_span.total_seconds() / 3600)
        
        # Very high or very low frequency can be suspicious
        if frequency > 50:
            base_score -= 1.0
        elif frequency < 0.1:
            base_score -= 0.5
        
        return max(0.0, min(10.0, base_score))
    
    def _risk_score_to_severity(self, risk_score: float) -> str:
        """Convert risk score to severity level"""
        if risk_score >= 8.0:
            return 'critical'
        elif risk_score >= 6.0:
            return 'high'
        elif risk_score >= 4.0:
            return 'medium'
        else:
            return 'low'
    
    def generate_behavioral_report(self) -> Dict[str, Any]:
        """Generate comprehensive behavioral intelligence report"""
        current_time = datetime.now()
        
        # Pattern analysis
        pattern_analysis = {
            'total_patterns': len(self.detected_patterns),
            'malicious_patterns': len([p for p in self.detected_patterns if p.risk_level in ['critical', 'high']]),
            'normal_patterns': len([p for p in self.detected_patterns if p.pattern_type.startswith('normal_')]),
            'pattern_types': defaultdict(int),
            'high_confidence_patterns': len([p for p in self.detected_patterns if p.confidence > 0.8])
        }
        
        for pattern in self.detected_patterns:
            pattern_analysis['pattern_types'][pattern.pattern_type] += 1
        
        # Anomaly analysis
        anomaly_analysis = {
            'total_anomalies': len(self.anomalies),
            'by_severity': defaultdict(int),
            'by_type': defaultdict(int),
            'recent_anomalies': len([a for a in self.anomalies if current_time - a.timestamp < timedelta(hours=24)])
        }
        
        for anomaly in self.anomalies:
            anomaly_analysis['by_severity'][anomaly.severity] += 1
            anomaly_analysis['by_type'][anomaly.anomaly_type] += 1
        
        # Profile analysis
        profile_analysis = {
            'total_profiles': len(self.behavior_profiles),
            'by_entity_type': defaultdict(int),
            'average_behavior_score': 0.0,
            'high_risk_profiles': 0,
            'low_risk_profiles': 0
        }
        
        if self.behavior_profiles:
            scores = [p.behavior_score for p in self.behavior_profiles.values()]
            profile_analysis['average_behavior_score'] = np.mean(scores)
            profile_analysis['high_risk_profiles'] = len([s for s in scores if s < 4.0])
            profile_analysis['low_risk_profiles'] = len([s for s in scores if s > 7.0])
        
        for profile in self.behavior_profiles.values():
            profile_analysis['by_entity_type'][profile.entity_type] += 1
        
        # Cluster analysis
        cluster_analysis = {
            'total_clusters': len(self.behavior_clusters),
            'by_risk_level': defaultdict(int),
            'average_cluster_size': 0.0,
            'largest_cluster_size': 0
        }
        
        if self.behavior_clusters:
            cluster_sizes = [len(c.members) for c in self.behavior_clusters.values()]
            cluster_analysis['average_cluster_size'] = np.mean(cluster_sizes)
            cluster_analysis['largest_cluster_size'] = max(cluster_sizes)
        
        for cluster in self.behavior_clusters.values():
            cluster_analysis['by_risk_level'][cluster.risk_level] += 1
        
        # Timeline analysis
        timeline_analysis = {
            'total_activities': len(self.activity_timeline),
            'activity_rate': len(self.activity_timeline) / max(1, self.time_window_hours),
            'risk_distribution': defaultdict(int),
            'peak_activity_hours': self._find_peak_activity_hours()
        }
        
        for activity in self.activity_timeline:
            risk_score = activity.get('risk_score', 0.0)
            if risk_score > 7.0:
                timeline_analysis['risk_distribution']['high'] += 1
            elif risk_score > 4.0:
                timeline_analysis['risk_distribution']['medium'] += 1
            else:
                timeline_analysis['risk_distribution']['low'] += 1
        
        return {
            'summary': {
                'analysis_timestamp': current_time.isoformat(),
                'time_window_hours': self.time_window_hours,
                'total_entities_analyzed': len(self.behavior_profiles),
                'overall_risk_level': self._calculate_overall_risk_level(),
                'key_findings': self._generate_key_findings()
            },
            'pattern_analysis': pattern_analysis,
            'anomaly_analysis': anomaly_analysis,
            'profile_analysis': profile_analysis,
            'cluster_analysis': cluster_analysis,
            'timeline_analysis': timeline_analysis,
            'recommendations': self._generate_behavioral_recommendations(),
            'threat_indicators': self._extract_threat_indicators()
        }
    
    def _find_peak_activity_hours(self) -> List[int]:
        """Find peak activity hours from timeline"""
        if not self.activity_timeline:
            return []
        
        hour_counts = defaultdict(int)
        for activity in self.activity_timeline:
            hour = activity.get('timestamp', datetime.now()).hour
            hour_counts[hour] += 1
        
        # Return top 3 peak hours
        sorted_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)
        return [hour for hour, count in sorted_hours[:3]]
    
    def _calculate_overall_risk_level(self) -> str:
        """Calculate overall risk level from all analyses"""
        risk_factors = []
        
        # Pattern risk
        malicious_patterns = len([p for p in self.detected_patterns if p.risk_level in ['critical', 'high']])
        if malicious_patterns > 5:
            risk_factors.append('critical')
        elif malicious_patterns > 2:
            risk_factors.append('high')
        elif malicious_patterns > 0:
            risk_factors.append('medium')
        
        # Anomaly risk
        critical_anomalies = len([a for a in self.anomalies if a.severity == 'critical'])
        if critical_anomalies > 3:
            risk_factors.append('critical')
        elif critical_anomalies > 1:
            risk_factors.append('high')
        elif critical_anomalies > 0:
            risk_factors.append('medium')
        
        # Profile risk
        high_risk_profiles = len([p for p in self.behavior_profiles.values() if p.behavior_score < 4.0])
        if high_risk_profiles > len(self.behavior_profiles) * 0.3:
            risk_factors.append('critical')
        elif high_risk_profiles > len(self.behavior_profiles) * 0.1:
            risk_factors.append('high')
        elif high_risk_profiles > 0:
            risk_factors.append('medium')
        
        if 'critical' in risk_factors:
            return 'critical'
        elif 'high' in risk_factors:
            return 'high'
        elif 'medium' in risk_factors:
            return 'medium'
        else:
            return 'low'
    
    def _generate_key_findings(self) -> List[str]:
        """Generate key findings from behavioral analysis"""
        findings = []
        
        # Pattern findings
        malicious_count = len([p for p in self.detected_patterns if p.risk_level in ['critical', 'high']])
        if malicious_count > 0:
            findings.append(f"Detected {malicious_count} malicious behavioral patterns")
        
        # Anomaly findings
        anomaly_count = len(self.anomalies)
        if anomaly_count > 0:
            findings.append(f"Identified {anomaly_count} behavioral anomalies requiring investigation")
        
        # Profile findings
        if self.behavior_profiles:
            avg_score = np.mean([p.behavior_score for p in self.behavior_profiles.values()])
            if avg_score < 5.0:
                findings.append("Overall behavioral profile indicates elevated risk levels")
        
        # Timeline findings
        if len(self.activity_timeline) > 0:
            high_risk_activities = len([a for a in self.activity_timeline if a.get('risk_score', 0) > 7.0])
            if high_risk_activities > len(self.activity_timeline) * 0.2:
                findings.append("High proportion of high-risk activities detected")
        
        # Cluster findings
        if self.behavior_clusters:
            risky_clusters = len([c for c in self.behavior_clusters.values() if c.risk_level in ['critical', 'high']])
            if risky_clusters > 0:
                findings.append(f"Identified {risky_clusters} high-risk behavior clusters")
        
        if not findings:
            findings.append("Behavioral analysis shows normal activity patterns")
        
        return findings
    
    def _generate_behavioral_recommendations(self) -> List[str]:
        """Generate recommendations based on behavioral analysis"""
        recommendations = []
        
        # Pattern-based recommendations
        malicious_patterns = [p for p in self.detected_patterns if p.risk_level in ['critical', 'high']]
        if malicious_patterns:
            pattern_types = set(p.pattern_type for p in malicious_patterns)
            for pattern_type in pattern_types:
                if pattern_type == 'data_exfiltration':
                    recommendations.append("Implement data loss prevention measures and monitor large file transfers")
                elif pattern_type == 'credential_theft':
                    recommendations.append("Strengthen credential protection and monitor authentication attempts")
                elif pattern_type == 'lateral_movement':
                    recommendations.append("Enhance network segmentation and monitor cross-system access")
        
        # Anomaly-based recommendations
        if len(self.anomalies) > 5:
            recommendations.append("Investigate multiple behavioral anomalies - potential security incident")
        
        # Profile-based recommendations
        high_risk_profiles = [p for p in self.behavior_profiles.values() if p.behavior_score < 4.0]
        if len(high_risk_profiles) > len(self.behavior_profiles) * 0.2:
            recommendations.append("Review and investigate high-risk behavioral profiles")
        
        # General recommendations
        if not recommendations:
            recommendations.append("Continue behavioral monitoring - current patterns appear normal")
        
        return recommendations
    
    def _extract_threat_indicators(self) -> List[Dict[str, Any]]:
        """Extract current threat indicators"""
        indicators = []
        
        # From patterns
        for pattern in self.detected_patterns:
            if pattern.risk_level in ['critical', 'high']:
                indicators.append({
                    'type': 'malicious_pattern',
                    'indicator': pattern.pattern_type,
                    'confidence': pattern.confidence,
                    'entities': pattern.associated_entities,
                    'risk_level': pattern.risk_level
                })
        
        # From anomalies
        for anomaly in self.anomalies:
            if anomaly.severity in ['critical', 'high']:
                indicators.append({
                    'type': 'behavioral_anomaly',
                    'indicator': anomaly.anomaly_type,
                    'confidence': anomaly.deviation_score,
                    'entity': anomaly.context.get('entity', 'unknown'),
                    'risk_level': anomaly.severity
                })
        
        return indicators

def scan_behavioral_intelligence(activities: List[Dict[str, Any]], config: Optional[ForensicConfig] = None) -> Dict[str, Any]:
    """Perform comprehensive behavioral intelligence analysis"""
    engine = BehavioralIntelligenceEngine(config)
    
    results = {
        'patterns': [],
        'anomalies': [],
        'profiles': [],
        'clusters': [],
        'report': {}
    }
    
    # Generate evidence items
    evidence_items = list(engine.analyze_behavioral_patterns(activities))
    
    # Categorize evidence items
    for evidence in evidence_items:
        if evidence.data_type == 'behavioral_pattern':
            results['patterns'].append(asdict(evidence))
        elif evidence.data_type == 'behavioral_anomaly':
            results['anomalies'].append(asdict(evidence))
        elif evidence.data_type == 'behavior_profile':
            results['profiles'].append(asdict(evidence))
        elif evidence.data_type == 'behavior_cluster':
            results['clusters'].append(asdict(evidence))
    
    # Generate comprehensive report
    results['report'] = engine.generate_behavioral_report()
    
    return results
