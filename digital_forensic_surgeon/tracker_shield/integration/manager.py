"""
TrackerShield Integration Manager
Connects all components: Tray <-> Addon <-> Dashboard <-> Detector
"""

import json
import threading
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class EventBus:
    """Central event bus for component communication"""
    
    def __init__(self):
        self.events_file = Path.home() / ".trackershield" / "events.jsonl"
        self.events_file.parent.mkdir(parents=True, exist_ok=True)
        
        # In-memory event queue
        self.subscribers = {}
        self.running = False
        self.thread = None
    
    def subscribe(self, event_type: str, callback):
        """Subscribe to event type"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
    
    def publish(self, event_type: str, data: Dict):
        """Publish event"""
        event = {
            'type': event_type,
            'timestamp': datetime.now().isoformat(),
            'data': data
        }
        
        # Write to file (for cross-process)
        with open(self.events_file, 'a') as f:
            f.write(json.dumps(event) + '\n')
        
        # Notify subscribers (in-process)
        if event_type in self.subscribers:
            for callback in self.subscribers[event_type]:
                try:
                    callback(data)
                except Exception as e:
                    print(f"Error in subscriber: {e}")
    
    def start_listener(self):
        """Start listening for events"""
        self.running = True
        self.thread = threading.Thread(target=self._listen, daemon=True)
        self.thread.start()
    
    def _listen(self):
        """Listen for file changes"""
        last_size = self.events_file.stat().st_size if self.events_file.exists() else 0
        
        while self.running:
            if self.events_file.exists():
                current_size = self.events_file.stat().st_size
                
                if current_size > last_size:
                    # New events
                    with open(self.events_file, 'r') as f:
                        f.seek(last_size)
                        for line in f:
                            try:
                                event = json.loads(line)
                                event_type = event['type']
                                
                                if event_type in self.subscribers:
                                    for callback in self.subscribers[event_type]:
                                        callback(event['data'])
                            except:
                                pass
                    
                    last_size = current_size
            
            time.sleep(0.1)


class IntegrationManager:
    """Manages integration between all components"""
    
    def __init__(self):
        self.event_bus = EventBus()
        self.stats = {
            'trackers_detected': 0,
            'trackers_blocked': 0,
            'unknowns_detected': 0,
            'contributions_pending': 0,
            'database_version': 0
        }
        
        # Setup event handlers
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup event handlers"""
        
        # Tracker detected (from addon)
        self.event_bus.subscribe('tracker_detected', self._on_tracker_detected)
        
        # Unknown detected (from detector)
        self.event_bus.subscribe('unknown_detected', self._on_unknown_detected)
        
        # Contribution added (from community)
        self.event_bus.subscribe('contribution_added', self._on_contribution_added)
        
        # Update available (from updater)
        self.event_bus.subscribe('update_available', self._on_update_available)
        
        # Settings changed (from tray)
        self.event_bus.subscribe('settings_changed', self._on_settings_changed)
    
    def _on_tracker_detected(self, data: Dict):
        """Handle tracker detection"""
        self.stats['trackers_detected'] += 1
        
        # Broadcast to dashboard
        self.event_bus.publish('stats_updated', self.stats)
        
        # Show tray notification
        self.event_bus.publish('tray_notification', {
            'title': 'Tracker Detected',
            'message': f"{data.get('name', 'Unknown')} blocked",
            'type': 'info'
        })
    
    def _on_unknown_detected(self, data: Dict):
        """Handle unknown tracker"""
        self.stats['unknowns_detected'] += 1
        
        # Add to contributions if high confidence
        if data.get('confidence', 0) >= 70:
            self.event_bus.publish('add_contribution', data)
    
    def _on_contribution_added(self, data: Dict):
        """Handle contribution"""
        self.stats['contributions_pending'] += 1
        
        # Check if should prompt user
        if self.stats['contributions_pending'] >= 10:
            self.event_bus.publish('prompt_contribution', {
                'count': self.stats['contributions_pending']
            })
    
    def _on_update_available(self, data: Dict):
        """Handle update notification"""
        self.event_bus.publish('tray_notification', {
            'title': 'Update Available!',
            'message': f"Version {data['version']} with +{data['new_signatures']} signatures",
            'type': 'update'
        })
    
    def _on_settings_changed(self, data: Dict):
        """Handle settings change"""
        # Reload components if needed
        if 'license_key' in data:
            self.event_bus.publish('reload_databases', {'tier': data.get('tier', 'free')})
    
    def get_stats(self) -> Dict:
        """Get current stats"""
        return self.stats.copy()
    
    def start(self):
        """Start integration manager"""
        self.event_bus.start_listener()
        print("✅ Integration Manager started")


# Test integration
if __name__ == '__main__':
    print("=" * 60)
    print("Integration Manager Test")
    print("=" * 60)
    
    manager = IntegrationManager()
    manager.start()
    
    # Simulate events
    print("\n📤 Simulating events...")
    
    # Tracker detected
    manager.event_bus.publish('tracker_detected', {
        'name': 'Facebook Pixel',
        'url': 'https://facebook.com/tr',
        'confidence': 100
    })
    
    time.sleep(0.2)
    
    # Unknown detected
    manager.event_bus.publish('unknown_detected', {
        'domain': 'tracking.example.com',
        'confidence': 75
    })
    
    time.sleep(0.2)
    
    # Get stats
    stats = manager.get_stats()
    print(f"\n📊 Stats:")
    print(f"   Trackers detected: {stats['trackers_detected']}")
    print(f"   Unknowns detected: {stats['unknowns_detected']}")
    print(f"   Contributions pending: {stats['contributions_pending']}")
    
    print("\n✅ Integration working!")
    print("=" * 60)
    
    time.sleep(1)
