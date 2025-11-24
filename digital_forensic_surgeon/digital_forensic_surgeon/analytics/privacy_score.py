"""
Privacy Score Calculator
Rates user privacy (0-100) based on tracking patterns
"""

from typing import Dict
from datetime import datetime, timedelta

class PrivacyScoreCalculator:
    """Calculate privacy score based on tracking data"""
    
    # Average user benchmarks
    AVERAGE_USER = {
        'events_per_day': 47,
        'unique_trackers': 8,
        'high_risk_percentage': 0.15,
        'data_brokers': 3
    }
    
    def calculate_score(self, db_conn) -> Dict:
        """
        Calculate privacy score (0-100)
        Higher = better privacy
        """
        
        cursor = db_conn.cursor()
        
        # Get tracking stats
        cursor.execute("""
            SELECT 
                COUNT(*) as total_events,
                COUNT(DISTINCT company_name) as unique_companies,
                COUNT(DISTINCT DATE(timestamp)) as active_days,
                MIN(timestamp) as first_seen,
                MAX(timestamp) as last_seen
            FROM tracking_events
        """)
        row = cursor.fetchone()
        
        if not row or row[0] == 0:
            return self._get_default_score()
        
        total_events = row[0]
        unique_companies = row[1]
        active_days = max(row[2], 1)
        
        # Events per day
        events_per_day = total_events / active_days
        
        # High risk events
        cursor.execute("SELECT COUNT(*) FROM tracking_events WHERE risk_score >= 8.0")
        high_risk_count = cursor.fetchone()[0]
        high_risk_percentage = high_risk_count / total_events if total_events > 0 else 0
        
        # Data brokers
        data_broker_domains = ['acxiom', 'oracle', 'nielsen', 'experian', 'equifax']
        cursor.execute(f"""
            SELECT COUNT(DISTINCT company_name)
            FROM tracking_events
            WHERE {' OR '.join([f"LOWER(domain) LIKE '%{db}%'" for db in data_broker_domains])}
        """)
        data_brokers = cursor.fetchone()[0]
        
        # Calculate component scores (0-100 each)
        
        # 1. Tracking Frequency Score (40% weight)
        # Lower tracking = higher score
        freq_ratio = self.AVERAGE_USER['events_per_day'] / max(events_per_day, 1)
        freq_score = min(100, freq_ratio * 100)
        
        # 2. Tracker Diversity Score (30% weight)
        # Fewer unique trackers = higher score
        diversity_ratio = self.AVERAGE_USER['unique_trackers'] / max(unique_companies, 1)
        diversity_score = min(100, diversity_ratio * 100)
        
        # 3. Risk Level Score (20% weight)
        # Lower high-risk percentage = higher score
        risk_ratio = (1 - high_risk_percentage) / (1 - self.AVERAGE_USER['high_risk_percentage'])
        risk_score = min(100, risk_ratio * 100)
        
        # 4. Data Broker Score (10% weight)
        # Fewer data brokers = higher score
        broker_ratio = max(0, 1 - (data_brokers / 5))  # 5+ brokers = 0 score
        broker_score = broker_ratio * 100
        
        # Weighted total
        total_score = (
            freq_score * 0.40 +
            diversity_score * 0.30 +
            risk_score * 0.20 +
            broker_score * 0.10
        )
        
        # Grade
        if total_score >= 90:
            grade = "A+"
            emoji = "🟢"
        elif total_score >= 80:
            grade = "A"
            emoji = "🟢"
        elif total_score >= 70:
            grade = "B"
            emoji = "🟡"
        elif total_score >= 60:
            grade = "C"
            emoji = "🟠"
        elif total_score >= 50:
            grade = "D"
            emoji = "🔴"
        else:
            grade = "F"
            emoji = "🔴"
        
        # Comparison
        vs_average = {
            'events_per_day': events_per_day / self.AVERAGE_USER['events_per_day'],
            'unique_trackers': unique_companies / self.AVERAGE_USER['unique_trackers'],
            'high_risk': high_risk_percentage / self.AVERAGE_USER['high_risk_percentage'],
        }
        
        # Improvement tips
        tips = self._generate_tips(
            events_per_day, unique_companies, high_risk_percentage, data_brokers
        )
        
        return {
            'score': round(total_score, 1),
            'grade': grade,
            'emoji': emoji,
            'components': {
                'frequency': round(freq_score, 1),
                'diversity': round(diversity_score, 1),
                'risk': round(risk_score, 1),
                'brokers': round(broker_score, 1)
            },
            'stats': {
                'events_per_day': round(events_per_day, 1),
                'unique_trackers': unique_companies,
                'high_risk_pct': round(high_risk_percentage * 100, 1),
                'data_brokers': data_brokers
            },
            'vs_average': vs_average,
            'tips': tips
        }
    
    def _generate_tips(self, events_per_day, unique_trackers, high_risk_pct, data_brokers):
        """Generate personalized improvement tips"""
        tips = []
        
        if events_per_day > self.AVERAGE_USER['events_per_day'] * 1.5:
            tips.append("🎯 **High tracking frequency** - Use browser extensions like uBlock Origin to reduce tracking")
        
        if unique_trackers > self.AVERAGE_USER['unique_trackers'] * 1.5:
            tips.append("🌐 **Many trackers** - Clear cookies regularly and use incognito mode for browsing")
        
        if high_risk_pct > self.AVERAGE_USER['high_risk_percentage'] * 1.5:
            tips.append("⚠️ **High-risk trackers** - Avoid clicking ads and use VPN for sensitive browsing")
        
        if data_brokers > 0:
            tips.append("📊 **Data brokers detected** - Opt-out from data broker databases using services like DeleteMe")
        
        if not tips:
            tips.append("✅ **Good job!** Your privacy is better than average. Keep it up!")
        
        return tips
    
    def _get_default_score(self):
        """Default score for no data"""
        return {
            'score': 100,
            'grade': "A+",
            'emoji': "🟢",
            'components': {'frequency': 100, 'diversity': 100, 'risk': 100, 'brokers': 100},
            'stats': {'events_per_day': 0, 'unique_trackers': 0, 'high_risk_pct': 0, 'data_brokers': 0},
            'vs_average': {},
            'tips': ["📭 No tracking data yet!"]
        }
