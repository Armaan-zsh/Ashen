"""
Tracking Reconstructor
Analyzes browser history to identify and reconstruct tracking events
"""

from typing import List, Dict, Any
from datetime import datetime
from dataclasses import dataclass
from collections import Counter

from .browser_history_scanner import HistoricalEvent
from .data_broker_database import DataBrokerDatabase


@dataclass
class TrackingTimeline:
    """Represents a timeline of tracking events"""
    total_events: int
    total_visits: int
    total_cookies: int
    tracking_events: int
    tracking_cookies: int
    unique_trackers: int
    date_range: tuple
    events_by_date: Dict[str, int]
    top_trackers: List[tuple]
    categories: Dict[str, int]
    high_risk_events: List[Dict[str, Any]]


class TrackingReconstructor:
    """Reconstructs tracking timeline from browser history"""
    
    def __init__(self):
        self.broker_db = DataBrokerDatabase()
    
    def reconstruct_timeline(self, events: List[HistoricalEvent]) -> TrackingTimeline:
        """Analyze historical events and identify tracking"""
        
        print("\n📊 Reconstructing tracking timeline...")
        
        tracking_events = []
        tracking_cookies = []
        trackers_found = set()
        categories_count = Counter()
        events_by_date = Counter()
        high_risk = []
        
        for event in events:
            # Classify URL/domain against tracker database
            classification = self.broker_db.classify_url(event.url)
            
            if classification['is_tracker']:
                trackers_found.add(classification['entity_name'])
                categories_count[classification['category']] += 1
                
                # Record tracking event
                tracking_event = {
                    'timestamp': event.timestamp,
                    'browser': event.browser,
                    'url': event.url,
                    'domain': event.domain,
                    'tracker': classification['entity_name'],
                    'category': classification['category'],
                    'risk_score': classification['risk_score'],
                    'event_type': event.event_type,
                    'title': event.title
                }
                
                if event.event_type == 'visit':
                    tracking_events.append(tracking_event)
                elif event.event_type == 'cookie':
                    tracking_cookies.append(tracking_event)
                    tracking_event['cookie_name'] = event.cookie_name
                
                # Track by date
                date_key = event.timestamp.strftime('%Y-%m-%d')
                events_by_date[date_key] += 1
                
                # High risk events
                if classification['risk_score'] >= 8.0:
                    high_risk.append(tracking_event)
        
        # Calculate date range
        if events:
            dates = [e.timestamp for e in events]
            date_range = (min(dates), max(dates))
        else:
            date_range = (datetime.now(), datetime.now())
        
        # Top trackers
        tracker_counts = Counter()
        for event in tracking_events + tracking_cookies:
            tracker_counts[event['tracker']] += 1
        top_trackers = tracker_counts.most_common(20)
        
        # Create timeline
        timeline = TrackingTimeline(
            total_events=len(events),
            total_visits=len([e for e in events if e.event_type == 'visit']),
            total_cookies=len([e for e in events if e.event_type == 'cookie']),
            tracking_events=len(tracking_events),
            tracking_cookies=len(tracking_cookies),
            unique_trackers=len(trackers_found),
            date_range=date_range,
            events_by_date=dict(events_by_date),
            top_trackers=top_trackers,
            categories=dict(categories_count),
            high_risk_events=high_risk
        )
        
        # Print summary
        print(f"  ✓ Total events analyzed: {len(events):,}")
        print(f"  ✓ Tracking events found: {len(tracking_events):,}")
        print(f"  ✓ Tracking cookies found: {len(tracking_cookies):,}")
        print(f"  ✓ Unique trackers: {len(trackers_found)}")
        print(f"  ✓ High-risk events: {len(high_risk):,}")
        print(f"  ✓ Date range: {date_range[0].strftime('%Y-%m-%d')} to {date_range[1].strftime('%Y-%m-%d')}")
        
        return timeline
    
    def get_timeline_for_date(self, events: List[HistoricalEvent], target_date: str) -> List[Dict[str, Any]]:
        """Get tracking events for a specific date"""
        matching_events = []
        
        for event in events:
            event_date = event.timestamp.strftime('%Y-%m-%d')
            if event_date == target_date:
                classification = self.broker_db.classify_url(event.url)
                if classification['is_tracker']:
                    matching_events.append({
                        'time': event.timestamp.strftime('%H:%M:%S'),
                        'tracker': classification['entity_name'],
                        'url': event.url,
                        'risk': classification['risk_score']
                    })
        
        return matching_events
    
    def get_timeline_for_daterange(self, events: List[HistoricalEvent], start_date: str, end_date: str) -> List[Dict[str, Any]]:
        """Get tracking events for a date range"""
        matching_events = []
        
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        for event in events:
            if start_dt <= event.timestamp <= end_dt:
                classification = self.broker_db.classify_url(event.url)
                if classification['is_tracker']:
                    matching_events.append({
                        'timestamp': event.timestamp,
                        'tracker': classification['entity_name'],
                        'category': classification['category'],
                        'url': event.url,
                        'risk': classification['risk_score'],
                        'browser': event.browser
                    })
        
        return matching_events
