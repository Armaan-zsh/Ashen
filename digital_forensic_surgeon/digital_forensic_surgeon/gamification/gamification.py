"""
Gamification System
Achievements, challenges, and privacy score tracking
"""

from typing import Dict, List
from datetime import datetime, timedelta
from dataclasses import dataclass


@dataclass
class Achievement:
    """Represents an achievement"""
    id: str
    name: str
    description: str
    icon: str
    unlocked: bool = False
    unlocked_date: datetime = None


class GamificationEngine:
    """Handles achievements, challenges, and privacy scoring"""
    
    ACHIEVEMENTS = {
        'first_scan': Achievement(
            id='first_scan',
            name="🔍 Privacy Detective",
            description="Ran your first tracking scan",
            icon="🔍"
        ),
        'data_value_check': Achievement(
            id='data_value_check',
            name="💰 Money Matters",
            description="Checked your data value for the first time",
            icon="💰"
        ),
        'privacy_fixer': Achievement(
            id='privacy_fixer',
            name="🛡️ Privacy Guardian",
            description="Generated blocking rules",
            icon="🛡️"
        ),
        'tracker_hunter_100': Achievement(
            id='tracker_hunter_100',
            name="🎯 Tracker Hunter",
            description="Discovered 100+ tracking events",
            icon="🎯"
        ),
        'tracker_hunter_1000': Achievement(
            id='tracker_hunter_1000',
            name="🔥 Tracking Master",
            description="Discovered 1,000+ tracking events",
            icon="🔥"
        ),
        'high_risk_finder': Achievement(
            id='high_risk_finder',
            name="⚠️ Danger Detector",
            description="Found 10+ high-risk tracking events",
            icon="⚠️"
        ),
        'week_monitor': Achievement(
            id='week_monitor',
            name="📅 Weekly Watcher",
            description="Kept monitor running for 7 days",
            icon="📅"
        ),
        'ghostmode': Achievement(
            id='ghostmode',
            name="👻 Ghost Mode",
            description="Blocked 100+ trackers",
            icon="👻"
        ),
        'data_millionaire': Achievement(
            id='data_millionaire',
            name="💎 Data Millionaire",
            description="Your data is worth $1000+/year",
            icon="💎"
        ),
    }
    
    def __init__(self):
        self.unlocked_achievements = set()
    
    def check_achievements(self, stats: Dict) -> List[Achievement]:
        """
        Check which achievements should be unlocked
        
        Args:
            stats: Dict with tracking statistics
        
        Returns:
            List of newly unlocked achievements
        """
        newly_unlocked = []
        
        total_events = stats.get('total_events', 0)
        high_risk = stats.get('high_risk_events', 0)
        data_value_yearly = stats.get('data_value_yearly', 0)
        
        # First scan
        if total_events > 0 and 'first_scan' not in self.unlocked_achievements:
            newly_unlocked.append(self._unlock('first_scan'))
        
        # Tracker hunter
        if total_events >= 100 and 'tracker_hunter_100' not in self.unlocked_achievements:
            newly_unlocked.append(self._unlock('tracker_hunter_100'))
        
        if total_events >= 1000 and 'tracker_hunter_1000' not in self.unlocked_achievements:
            newly_unlocked.append(self._unlock('tracker_hunter_1000'))
        
        # High risk finder
        if high_risk >= 10 and 'high_risk_finder' not in self.unlocked_achievements:
            newly_unlocked.append(self._unlock('high_risk_finder'))
        
        # Data millionaire
        if data_value_yearly >= 1000 and 'data_millionaire' not in self.unlocked_achievements:
            newly_unlocked.append(self._unlock('data_millionaire'))
        
        return newly_unlocked
    
    def _unlock(self, achievement_id: str) -> Achievement:
        """Unlock an achievement"""
        achievement = self.ACHIEVEMENTS[achievement_id]
        achievement.unlocked = True
        achievement.unlocked_date = datetime.now()
        self.unlocked_achievements.add(achievement_id)
        return achievement
    
    def calculate_privacy_score(self, stats: Dict) -> Dict:
        """
        Calculate comprehensive privacy score (0-100)
        
        Higher score = better privacy
        """
        
        score = 100  # Start perfect
        
        total_events = stats.get('total_events', 0)
        high_risk = stats.get('high_risk_events', 0)
        unique_companies = stats.get('unique_companies', 0)
        
        # Deduct for tracking volume
        if total_events > 0:
            # Logarithmic penalty for events
            import math
            event_penalty = min(30, math.log10(total_events + 1) * 10)
            score -= event_penalty
        
        # Deduct for high-risk events
        if high_risk > 0:
            risk_penalty = min(25, high_risk / 10)
            score -= risk_penalty
        
        # Deduct for unique trackers
        if unique_companies > 0:
            company_penalty = min(20, unique_companies / 2)
            score -= company_penalty
        
        score = max(0, int(score))
        
        # Determine grade
        if score >= 90:
            grade = "A+"
            message = "🛡️ Excellent Privacy!"
        elif score >= 80:
            grade = "A"
            message = "✅ Great Privacy"
        elif score >= 70:
            grade = "B"
            message = "👍 Good Privacy"
        elif score >= 60:
            grade = "C"
            message = "⚠️ Fair Privacy"
        elif score >= 50:
            grade = "D"
            message = "😟 Poor Privacy"
        else:
            grade = "F"
            message = "🚨 Critical - Take Action!"
        
        return {
            'score': score,
            'grade': grade,
            'message': message,
            'breakdown': {
                'tracking_volume': f"-{int(event_penalty if total_events > 0 else 0)} pts",
                'high_risk_events': f"-{int(risk_penalty if high_risk > 0 else 0)} pts",
                'unique_trackers': f"-{int(company_penalty if unique_companies > 0 else 0)} pts"
            }
        }
    
    def get_daily_challenge(self) -> Dict:
        """Get today's privacy challenge"""
        
        challenges = [
            {
                'title': "🎯 Zero Tolerance",
                'description': "Go 24 hours without being tracked",
                'reward': "👻 Ghost Badge"
            },
            {
                'title': "🛡️ Block Party",
                'description': "Block 50+ tracking domains",
                'reward': "⚔️ Defender Badge"
            },
            {
                'title': "🔍 Deep Dive",
                'description': "Analyze your last month of tracking",
                'reward': "🔬 Analyst Badge"
            },
            {
                'title': "💰 Know Your Worth",
                'description': "Calculate your data value",
                'reward': "💎 Valuator Badge"
            },
            {
                'title': "📊 Privacy Audit",
                'description': "Review all high-risk tracking events",
                'reward': "🎖️ Auditor Badge"
            }
        ]
        
        # Rotate challenge daily
        day_of_year = datetime.now().timetuple().tm_yday
        challenge_index = day_of_year % len(challenges)
        
        return challenges[challenge_index]
    
    def format_achievements_report(self, stats: Dict) -> str:
        """Format achievements into a report"""
        
        newly_unlocked = self.check_achievements(stats)
        
        report = "\n🏆 YOUR ACHIEVEMENTS\n"
        report += "="*50 + "\n\n"
        
        unlocked_count = len(self.unlocked_achievements)
        total_count = len(self.ACHIEVEMENTS)
        
        report += f"Unlocked: {unlocked_count}/{total_count}\n\n"
        
        for achievement in self.ACHIEVEMENTS.values():
            status = "✅" if achievement.unlocked else "🔒"
            report += f"{status} {achievement.icon} {achievement.name}\n"
            report += f"   {achievement.description}\n\n"
        
        return report
