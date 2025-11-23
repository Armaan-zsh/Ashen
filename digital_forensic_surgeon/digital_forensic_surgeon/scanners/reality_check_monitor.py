"""
Reality Check Monitor - Core Orchestrator
Coordinates mitmproxy, browser extension, and dashboard for real-time tracking detection
"""

import time
import threading
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import json

from .mitm_proxy_manager import MITMProxyManager, TrackingEvent
from .data_broker_database import DataBrokerDatabase, TrackerEntity


class PrivacyViolation:
    """Represents a pri vacy violation event"""
    def __init__(self, timestamp: datetime, severity: str, violation_type: str,
                 entity: str, description: str, data: Dict[str, Any]):
        self.timestamp = timestamp
        self.severity = severity  # low, medium, high, critical
        self.violation_type = violation_type
        self.entity = entity
        self.description = description
        self.data = data
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp.isoformat(),
            "severity": self.severity,
            "type": self.violation_type,
            "entity": self.entity,
            "description": self.description,
            "data": self.data
        }


class RealityCheckMonitor:
    """Core orchestrator for Reality Check system"""
    
    def __init__(self, proxy_port: int = 8080):
        self.proxy_manager = MITMProxyManager(port=proxy_port)
        self.broker_db = DataBrokerDatabase()
        
        # State
        self.is_monitoring = False
        self.start_time = None
        self.monitor_thread = None
        
        # Events and violations
        self.tracking_events: List[TrackingEvent] = []
        self.violations: List[PrivacyViolation] = []
        
        # Statistics
        self.stats = {
            "total_requests": 0,
            "total_trackers": 0,
            "unique_companies": set(),
            "categories": Counter(),
            "tracking_types": Counter(),
            "high_risk_events": 0,
            "data_points_leaked": 0
        }
        
        # Timeline (for dashboard)
        self.timeline: List[Dict[str, Any]] = []
        
        # Tracker network (entity relationships)
        self.tracker_network: Dict[str, List[str]] = defaultdict(list)
    
    def start(self, duration_seconds: int = 3600):
        """Start Reality Check monitoring"""
        if self.is_monitoring:
            print("[Reality Check] Already monitoring")
            return
        
        print("\n" + "="*70)
        print("  🔥 REALITY CHECK - BEAST MODE ACTIVATED")
        print("="*70)
        print()
        print(f"  Duration: {duration_seconds // 60} minutes ({duration_seconds} seconds)")
        print(f"  Proxy Port: {self.proxy_manager.port}")
        print()
        print("  Configure your browser to use proxy:")
        print(f"    HTTP Proxy: localhost:{self.proxy_manager.port}")
        print(f"    HTTPS Proxy: localhost:{self.proxy_manager.port}")
        print()
        print("  Or visit http://mitm.it to install the certificate first")
        print()
        print("="*70)
        print()
        
        # Start proxy
        self.proxy_manager.start()
        
        # Start monitoring
        self.is_monitoring = True
        self.start_time = datetime.now()
        
        # Start background processing thread
        self.monitor_thread = threading.Thread(
            target=self._monitor_loop,
            args=(duration_seconds,),
            daemon=True
        )
        self.monitor_thread.start()
        
        print("[Reality Check] ✓ Monitoring started")
        print("[Reality Check]   Now browse the web normally...")
        print("[Reality Check]   We'll show you the terrifying reality.\n")
    
    def _monitor_loop(self, duration_seconds: int):
        """Background monitoring loop"""
        end_time = datetime.now() + timedelta(seconds=duration_seconds)
        
        while self.is_monitoring and datetime.now() < end_time:
            # Fetch new events from proxy
            new_events = self.proxy_manager.get_events(max_events=100)
            
            for event in new_events:
                self._process_event(event)
            
            # Update stats
            self._update_stats()
            
            # Sleep briefly
            time.sleep(0.5)
        
        # Monitoring duration elapsed - just stop monitoring, don't call stop() from thread
        if self.is_monitoring:
            self.is_monitoring = False
            self.proxy_manager.stop()
            self._update_stats()
            print("\n[Reality Check] ⏱ Monitoring duration completed")
            self._print_summary()
    
    def stop(self):
        """Stop Reality Check monitoring"""
        if not self.is_monitoring:
            return
        
        print("\n[Reality Check] Stopping monitoring...")
        
        self.is_monitoring = False
        
        # Stop proxy
        self.proxy_manager.stop()
        
        # Wait for thread (only if called from outside the thread)
        import threading
        if self.monitor_thread and self.monitor_thread.is_alive() and threading.current_thread() != self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        
        # Final stats update
        self._update_stats()
        
        print("[Reality Check] ✓ Monitoring stopped")
        self._print_summary()
    
    def _process_event(self, event: TrackingEvent):
        """Process a tracking event"""
        # Add to list
        self.tracking_events.append(event)
        
        # Update statistics
        self.stats["total_trackers"] += 1
        self.stats["unique_companies"].add(event.entity_name)
        self.stats["categories"][event.category] += 1
        self.stats["tracking_types"][event.tracking_type] += 1
        
        # Count data points
        data_points = len(event.cookies) + len(event.request_headers) + len(event.data_sent)
        self.stats["data_points_leaked"] += data_points
        
        # High risk tracking?
        if event.risk_score >= 8.0:
            self.stats["high_risk_events"] += 1
            
            # Create violation
            violation = PrivacyViolation(
                timestamp=event.timestamp,
                severity="high" if event.risk_score < 9.0 else "critical",
                violation_type=event.tracking_type,
                entity=event.entity_name,
                description=f"{event.entity_name} tracked you via {event.tracking_type}",
                data={
                    "url": event.url,
                    "risk_score": event.risk_score,
                    "cookies": len(event.cookies),
                    "category": event.category
                }
            )
            self.violations.append(violation)
        
        # Add to timeline
        self.timeline.append({
            "timestamp": event.timestamp,
            "event_type": "tracker",
            "entity": event.entity_name,
            "category": event.category,
            "tracking_type": event.tracking_type,
            "url": event.url,
            "risk_score": event.risk_score
        })
        
        # Build tracker network (entity relationships)
        # This shows which first-party sites connect to which trackers
        from urllib.parse import urlparse
        domain = urlparse(event.url).netloc
        if domain:
            self.tracker_network[event.entity_name].append(domain)
    
    def _update_stats(self):
        """Update statistics from proxy"""
        proxy_stats = self.proxy_manager.get_stats()
        self.stats["total_requests"] = proxy_stats["total_requests"]
    
    def _print_summary(self):
        """Print a summary of findings"""
        runtime = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        
        print("\n" + "="*70)
        print("  🔥 REALITY CHECK RESULTS - THE TRUTH")
        print("="*70)
        print()
        print(f"  Runtime: {runtime / 60:.1f} minutes")
        print()
        print("  📊 SHOCKING STATISTICS:")
        print(f"     • {self.stats['total_requests']:,} total web requests")
        print(f"     • {self.stats['total_trackers']:,} tracking requests intercepted")
        print(f"     • {len(self.stats['unique_companies'])} companies received your data")
        print(f"     • {self.stats['data_points_leaked']:,} data points leaked")
        print(f"     • {self.stats['high_risk_events']} high-risk violations")
        print()
        print(f"  🎯 Privacy Score: {self.calculate_privacy_score()}/100")
        print()
        
        if self.stats['unique_companies']:
            print("  💀 TOP TRACKERS:")
            # Get top trackers by frequency
            tracker_counts = Counter()
            for event in self.tracking_events:
                tracker_counts[event.entity_name] += 1
            
            for tracker, count in tracker_counts.most_common(10):
                entity = self.broker_db.get_entity_by_name(tracker)
                risk = entity.risk_score if entity else 0.0
                print(f"     • {tracker}: {count} requests (Risk: {risk}/10)")
        
        print()
        print("="*70)
    
    def calculate_privacy_score(self) -> int:
        """Calculate privacy score (0-100, higher is better)"""
        if not self.start_time:
            return 100
        
        runtime_minutes = (datetime.now() - self.start_time).total_seconds() / 60
        if runtime_minutes < 1:
            return 100
        
        # Scoring factors (inverse - more violations = lower score)
        companies_penalty = min(len(self.stats['unique_companies']) * 2, 40)
        tracker_rate_penalty = min((self.stats['total_trackers'] / runtime_minutes) * 2, 30)
        high_risk_penalty = min(self.stats['high_risk_events'] * 3, 20)
        data_leak_penalty = min((self.stats['data_points_leaked'] / 100) * 2, 10)
        
        score = 100 - companies_penalty - tracker_rate_penalty - high_risk_penalty - data_leak_penalty
        
        return max(0, int(score))
    
    def get_live_stats(self) -> Dict[str, Any]:
        """Get live statistics for dashboard"""
        runtime = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        
        return {
            "is_running": self.is_monitoring,
            "runtime_seconds": runtime,
            "runtime_display": f"{int(runtime // 60)}m {int(runtime % 60)}s",
            
            # Shock metrics
            "total_companies": len(self.stats['unique_companies']),
            "total_trackers": self.stats['total_trackers'],
            "total_requests": self.stats['total_requests'],
            "data_points_leaked": self.stats['data_points_leaked'],
            "high_risk_events": self.stats['high_risk_events'],
            
            # Rates
            "trackers_per_minute": (self.stats['total_trackers'] / (runtime / 60)) if runtime > 0 else 0,
            "companies_per_minute": (len(self.stats['unique_companies']) / (runtime / 60)) if runtime > 0 else 0,
            
            # Privacy score
            "privacy_score": self.calculate_privacy_score(),
            
            # Lists
            "company_names": list(self.stats['unique_companies']),
            "categories": dict(self.stats['categories']),
            "tracking_types": dict(self.stats['tracking_types']),
            
            # Recent events
            "recent_events": [e.to_dict() for e in self.tracking_events[-10:]],
            
            # Timeline
            "timeline_count": len(self.timeline)
        }
    
    def get_tracker_network(self) -> Dict[str, Any]:
        """Get tracker network graph data"""
        # Build network graph
        nodes = []
        edges = []
        
        # Add "You" as center node
        nodes.append({
            "id": "you",
            "label": "YOU",
            "type": "user",
            "risk": 0
        })
        
        # Add tracker nodes
        for company in self.stats['unique_companies']:
            entity = self.broker_db.get_entity_by_name(company)
            risk_score = entity.risk_score if entity else 5.0
            category = entity.category if entity else "Unknown"
            
            nodes.append({
                "id": company,
                "label": company,
                "type": "tracker",
                "category": category,
                "risk": risk_score
            })
            
            # Edge from you to tracker
            edges.append({
                "from": "you",
                "to": company,
                "weight": len([e for e in self.tracking_events if e.entity_name == company])
            })
        
        return {
            "nodes": nodes,
            "edges": edges
        }
    
    def get_violations_timeline(self) -> List[Dict[str, Any]]:
        """Get privacy violations timeline"""
        return [v.to_dict() for v in self.violations]
    
    def get_detailed_report(self) -> Dict[str, Any]:
        """Get comprehensive report data"""
        return {
            "summary": self.get_live_stats(),
            "tracker_network": self.get_tracker_network(),
            "violations": self.get_violations_timeline(),
            "timeline": self.timeline,
            "top_trackers": self._get_top_trackers(),
            "category_breakdown": dict(self.stats['categories']),
            "tracking_methods": dict(self.stats['tracking_types'])
        }
    
    def _get_top_trackers(self) -> List[Dict[str, Any]]:
        """Get top trackers with details"""
        tracker_counts = Counter()
        for event in self.tracking_events:
            tracker_counts[event.entity_name] += 1
        
        top_trackers = []
        for tracker, count in tracker_counts.most_common(20):
            entity = self.broker_db.get_entity_by_name(tracker)
            
            if entity:
                top_trackers.append({
                    "name": tracker,
                    "count": count,
                    "risk_score": entity.risk_score,
                    "category": entity.category,
                    "known_for": entity.known_for,
                    "data_collected": entity.data_collected
                })
        
        return top_trackers
