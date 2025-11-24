"""
Live Event Stream
Broadcasts tracking events from proxy to dashboard in real-time
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Set
from pathlib import Path

class LiveEventStream:
    """Manages live tracking event broadcasting"""
    
    def __init__(self):
        self.events_file = Path.home() / ".mitmproxy" / "live_events.jsonl"
        self.subscribers: Set = set()
        
        # Ensure directory exists
        self.events_file.parent.mkdir(parents=True, exist_ok=True)
    
    def broadcast_event(self, event: Dict):
        """
        Broadcast a tracking event to all subscribers
        
        Args:
            event: Dict with decoded tracking data
        """
        
        # Add timestamp
        event['broadcast_time'] = datetime.now().isoformat()
        
        # Write to file (dashboard will read)
        with open(self.events_file, 'a') as f:
            f.write(json.dumps(event) + '\n')
    
    def get_recent_events(self, count: int = 50) -> list:
        """Get recent N events"""
        
        if not self.events_file.exists():
            return []
        
        events = []
        with open(self.events_file, 'r') as f:
            lines = f.readlines()
            for line in lines[-count:]:
                try:
                    events.append(json.loads(line.strip()))
                except:
                    pass
        
        return events
    
    def clear_old_events(self, keep_last: int = 1000):
        """Keep only last N events to prevent file bloat"""
        
        if not self.events_file.exists():
            return
        
        events = self.get_recent_events(keep_last)
        
        with open(self.events_file, 'w') as f:
            for event in events:
                f.write(json.dumps(event) + '\n')


# Global instance
live_stream = LiveEventStream()
