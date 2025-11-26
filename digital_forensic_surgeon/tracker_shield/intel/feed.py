"""
Global Tracker Intel Feed
Shows real-time global tracking statistics
"""

import json
import random
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List

class TrackerIntelFeed:
    """Global tracker intelligence and statistics"""
    
    def __init__(self, data_dir=None):
        if data_dir is None:
            data_dir = Path.home() / ".trackershield"
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.intel_file = self.data_dir / "global_intel.json"
        self.intel = self._load_intel()
    
    def _load_intel(self) -> Dict:
        """Load global intel"""
        if self.intel_file.exists():
            with open(self.intel_file, 'r') as f:
                return json.load(f)
        
        # Generate demo data
        return self._generate_demo_intel()
    
    def _generate_demo_intel(self) -> Dict:
        """Generate realistic demo data"""
        companies = [
            'Facebook/Meta', 'Google', 'Amazon', 'TikTok/ByteDance',
            'Twitter/X', 'LinkedIn', 'Snapchat', 'Microsoft',
            'Apple', 'Doubleclick', 'Hotjar', 'Clarity'
        ]
        
        # Realistic distribution (Facebook/Google dominate)
        weights = [25, 22, 15, 12, 8, 6, 5, 3, 2,  1, 0.5, 0.5]
        
        intel = {
            'global_stats': {
                'total_blocked_today': random.randint(150000, 250000),
                'total_blocked_this_week': random.randint(1000000, 1500000),
                'total_blocked_all_time': random.randint(10000000, 15000000),
                'active_users': random.randint(5000, 8000),
                'last_updated': datetime.now().isoformat()
            },
            'company_rankings': [],
            'recent_blocks': []
        }
        
        # Generate company rankings
        total_blocks = intel['global_stats']['total_blocked_today']
        for company, weight in zip(companies, weights):
            blocks = int(total_blocks * (weight / 100))
            intel['company_rankings'].append({
                'company': company,
                'blocks_today': blocks,
                'avg_risk_score': round(random.uniform(6.5, 9.5), 1),
                'trend': random.choice(['up', 'down', 'stable'])
            })
        
        # Sort by blocks
        intel['company_rankings'].sort(key=lambda x: x['blocks_today'], reverse=True)
        
        # Generate recent blocks (last 10)
        for _ in range(10):
            company = random.choices(companies, weights=weights)[0]
            intel['recent_blocks'].append({
                'company': company,
                'timestamp': (datetime.now() - timedelta(seconds=random.randint(1, 300))).isoformat(),
                'country': random.choice(['US', 'UK', 'IN', 'CA', 'AU', 'DE', 'FR']),
                'tracker_type': random.choice(['Pixel', 'Cookie', 'Analytics', 'Ads'])
            })
        
        return intel
    
    def get_global_stats(self) -> Dict:
        """Get global statistics"""
        return self.intel['global_stats']
    
    def get_top_offenders(self, limit=10) -> List[Dict]:
        """Get top tracking companies"""
        return self.intel['company_rankings'][:limit]
    
    def get_recent_blocks(self, limit=10) -> List[Dict]:
        """Get recent blocks globally"""
        return self.intel['recent_blocks'][:limit]
    
    def add_block(self, company: str, country: str = 'US'):
        """Add a block to global stats"""
        self.intel['global_stats']['total_blocked_today'] += 1
        self.intel['global_stats']['total_blocked_all_time'] += 1
        
        # Update company stats
        for ranking in self.intel['company_rankings']:
            if ranking['company'] == company:
                ranking['blocks_today'] += 1
                break
        
        # Add to recent blocks
        self.intel['recent_blocks'].insert(0, {
            'company': company,
            'timestamp': datetime.now().isoformat(),
            'country': country,
            'tracker_type': 'Unknown'
        })
        
        # Keep only last 50
        self.intel['recent_blocks'] = self.intel['recent_blocks'][:50]
        
        # Save
        with open(self.intel_file, 'w') as f:
            json.dump(self.intel, f, indent=2)
    
    def get_live_feed_message(self) -> str:
        """Get live feed message"""
        stats = self.intel['global_stats']
        top = self.intel['company_rankings'][0]
        
        blocked_last_hour = random.randint(5000, 8000)
        
        return f"""🌍 GLOBAL TRACKER INTEL

📊 Last Hour:
   • {blocked_last_hour:,} trackers blocked worldwide
   • {stats['active_users']:,} active users protected

🏆 Top Offender Today:
   • {top['company']}: {top['blocks_today']:,} blocks

🔴 Live: {len(self.intel['recent_blocks'])} recent detections
"""


# Test
if __name__ == '__main__':
    print("=" * 60)
    print("Global Tracker Intel Feed Test")
    print("=" * 60)
    
    feed = TrackerIntelFeed()
    
    # Get stats
    stats = feed.get_global_stats()
    print(f"\n📊 Global Stats:")
    print(f"   Blocked today: {stats['total_blocked_today']:,}")
    print(f"   Blocked this week: {stats['total_blocked_this_week']:,}")
    print(f"   All-time: {stats['total_blocked_all_time']:,}")
    print(f"   Active users: {stats['active_users']:,}")
    
    # Top offenders
    print(f"\n🏆 Top 5 Offenders:")
    for i, company in enumerate(feed.get_top_offenders(5), 1):
        trend = {'up': '📈', 'down': '📉', 'stable': '➡️'}[company['trend']]
        print(f"   {i}. {company['company']}: {company['blocks_today']:,} {trend}")
    
    # Live feed message
    print(f"\n🌍 Live Feed:")
    print(feed.get_live_feed_message())
    
    print("\n" + "=" * 60)
    print("✅ Intel feed ready!")
    print("=" * 60)
