"""
Privacy Score Gamification System
Makes privacy protection fun and engaging
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List

class PrivacyGameifier:
    """Gamification system for privacy protection"""
    
    def __init__(self, user_dir=None):
        if user_dir is None:
            user_dir = Path.home() / ".trackershield"
        self.user_dir = Path(user_dir)
        self.user_dir.mkdir(exist_ok=True)
        
        self.stats_file = self.user_dir / "gamification_stats.json"
        self.stats = self._load_stats()
    
    def _load_stats(self) -> Dict:
        """Load user stats"""
        if self.stats_file.exists():
            with open(self.stats_file, 'r') as f:
                return json.load(f)
        
        return {
            'total_blocked': 0,
            'streak_days': 0,
            'last_active': None,
            'achievements': [],
            'level': 1,
            'xp': 0,
            'daily_scores': {}  # date -> score
        }
    
    def _save_stats(self):
        """Save user stats"""
        with open(self.stats_file, 'w') as f:
            json.dump(self.stats, f, indent=2)
    
    def add_blocked_tracker(self, tracker_name: str):
        """Record a blocked tracker"""
        self.stats['total_blocked'] += 1
        self.stats['xp'] += 10  # 10 XP per block
        
        # Update streak
        today = datetime.now().date().isoformat()
        if self.stats['last_active'] != today:
            yesterday = (datetime.now() - timedelta(days=1)).date().isoformat()
            
            if self.stats['last_active'] == yesterday:
                self.stats['streak_days'] += 1
            else:
                self.stats['streak_days'] = 1
            
            self.stats['last_active'] = today
        
        # Check for level up
        self._check_level_up()
        
        # Check achievements
        self._check_achievements()
        
        self._save_stats()
    
    def _check_level_up(self):
        """Check if user leveled up"""
        xp_needed = self.stats['level'] * 100
        
        if self.stats['xp'] >= xp_needed:
            self.stats['level'] += 1
            self.stats['xp'] = 0
            return True
        return False
    
    def _check_achievements(self):
        """Check and unlock achievements"""
        achievements = []
        
        # Tracker count achievements
        if self.stats['total_blocked'] >= 100 and 'Century' not in self.stats['achievements']:
            achievements.append({
                'name': 'Century',
                'description': '100 trackers blocked!',
                'icon': '💯',
                'unlocked_at': datetime.now().isoformat()
            })
            self.stats['achievements'].append('Century')
        
        if self.stats['total_blocked'] >= 1000 and 'Millennium' not in self.stats['achievements']:
            achievements.append({
                'name': 'Millennium',
                'description': '1,000 trackers blocked!',
                'icon': '🏆',
                'unlocked_at': datetime.now().isoformat()
            })
            self.stats['achievements'].append('Millennium')
        
        if self.stats['total_blocked'] >= 10000 and 'Legend' not in self.stats['achievements']:
            achievements.append({
                'name': 'Legend',
                'description': '10,000 trackers blocked!',
                'icon': '👑',
                'unlocked_at': datetime.now().isoformat()
            })
            self.stats['achievements'].append('Legend')
        
        # Streak achievements
        if self.stats['streak_days'] >= 7 and 'Week Warrior' not in self.stats['achievements']:
            achievements.append({
                'name': 'Week Warrior',
                'description': '7 day streak!',
                'icon': '🔥',
                'unlocked_at': datetime.now().isoformat()
            })
            self.stats['achievements'].append('Week Warrior')
        
        if self.stats['streak_days'] >= 30 and 'Month Master' not in self.stats['achievements']:
            achievements.append({
                'name': 'Month Master',
                'description': '30 day streak!',
                'icon': '🚀',
                'unlocked_at': datetime.now().isoformat()
            })
            self.stats['achievements'].append('Month Master')
        
        return achievements
    
    def calculate_daily_score(self, trackers_blocked_today: int) -> int:
        """Calculate privacy score (0-100)"""
        # Higher score = better privacy
        base_score = 50
        
        # Bonus for blocking trackers
        bonus = min(trackers_blocked_today * 2, 40)
        
        # Bonus for streak
        streak_bonus = min(self.stats['streak_days'], 10)
        
        score = base_score + bonus + streak_bonus
        
        # Cap at 100
        return min(score, 100)
    
    def get_leaderboard_entry(self) -> Dict:
        """Get anonymous leaderboard entry"""
        return {
            'user_id': self.stats.get('anonymous_id', 'user_xxx'),
            'total_blocked': self.stats['total_blocked'],
            'level': self.stats['level'],
            'streak': self.stats['streak_days']
        }
    
    def get_share_message(self) -> str:
        """Get shareable message"""
        return f"""🛡️ TrackerShield

I've blocked {self.stats['total_blocked']:,} trackers!

Level: {self.stats['level']}
Streak: {self.stats['streak_days']} days

Protect your privacy: trackershield.io
"""


# Test
if __name__ == '__main__':
    print("=" * 60)
    print("Privacy Gamification System Test")
    print("=" * 60)
    
    game = PrivacyGameifier()
    
    # Simulate blocking trackers
    print("\n📊 Simulating tracker blocks...")
    for i in range(15):
        game.add_blocked_tracker(f"Tracker_{i}")
    
    print(f"\n🎮 Stats:")
    print(f"   Total blocked: {game.stats['total_blocked']}")
    print(f"   Level: {game.stats['level']}")
    print(f"   XP: {game.stats['xp']}")
    print(f"   Streak: {game.stats['streak_days']} days")
    print(f"   Achievements: {len(game.stats['achievements'])}")
    
    # Calculate score
    score = game.calculate_daily_score(15)
    print(f"\n💯 Today's Privacy Score: {score}/100")
    
    # Share message
    print(f"\n📱 Share message:")
    print(game.get_share_message())
    
    print("\n" + "=" * 60)
    print("✅ Gamification system ready!")
    print("=" * 60)
