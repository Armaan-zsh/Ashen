"""
Data Value Calculator
Calculates the monetary value of user's tracked data based on industry estimates
"""

from typing import Dict, List
from datetime import datetime, timedelta


class DataValueCalculator:
    """Calculates how much money companies make from user's tracked data"""
    
    # Industry average CPM (Cost Per Mille/1000 impressions) and data values
    # Based on real industry data from advertising platforms
    COMPANY_VALUES = {
        'Google': {
            'per_event': 0.05,  # Average value per tracking event
            'annual_multiplier': 1.2,  # They make MORE over time
            'category_multipliers': {
                'Advertising': 2.0,
                'Analytics': 1.5,
                'Search': 1.8,
            }
        },
        'Facebook': {
            'per_event': 0.04,
            'annual_multiplier': 1.3,
            'category_multipliers': {
                'Social Media': 2.5,
                'Advertising': 2.2,
            }
        },
        'Meta': {
            'per_event': 0.04,
            'annual_multiplier': 1.3,
            'category_multipliers': {
                'Social Media': 2.5,
                'Advertising': 2.2,
            }
        },
        'Amazon': {
            'per_event': 0.06,  # Amazon data is VALUABLE
            'annual_multiplier': 1.4,
            'category_multipliers': {
                'E-Commerce': 2.8,
                'Advertising': 2.0,
            }
        },
        'Microsoft': {
            'per_event': 0.03,
            'annual_multiplier': 1.1,
            'category_multipliers': {
                'Analytics': 1.5,
                'Advertising': 1.7,
            }
        },
        'TikTok': {
            'per_event': 0.045,
            'annual_multiplier': 1.5,
            'category_multipliers': {
                'Social Media': 2.3,
                'Video': 2.0,
            }
        },
        # Data brokers make BANK
        'Acxiom': {'per_event': 0.08, 'annual_multiplier': 1.5},
        'Oracle': {'per_event': 0.07, 'annual_multiplier': 1.4},
        'Nielsen': {'per_event': 0.06, 'annual_multiplier': 1.3},
        
        # Default for unknown trackers
        'default': {'per_event': 0.02, 'annual_multiplier': 1.1}
    }
    
    # Premium data types are worth MORE
    PREMIUM_MULTIPLIERS = {
        'high_income': 2.5,  # High-income users worth 2.5x more
        'purchase_intent': 3.0,  # Shopping data = $$$$
        'location': 2.0,  # Location data is valuable
        'financial': 4.0,  # Financial data = GOLD
        'health': 3.5,  # Health data very valuable
    }
    
    def calculate_event_value(self, company: str, category: str, risk_score: float) -> float:
        """Calculate value of a single tracking event"""
        
        # Get company data or use default
        company_data = self.COMPANY_VALUES.get(company, self.COMPANY_VALUES['default'])
        base_value = company_data['per_event']
        
        # Apply category multiplier if exists
        category_mult = company_data.get('category_multipliers', {}).get(category, 1.0)
        
        # Higher risk = more valuable data being collected
        risk_mult = 1.0 + (risk_score / 10.0)
        
        value = base_value * category_mult * risk_mult
        return round(value, 4)
    
    def calculate_total_value(self, tracking_events: List[Dict]) -> Dict[str, float]:
        """
        Calculate total value from tracking events
        
        Args:
            tracking_events: List of dicts with 'company', 'category', 'risk_score', 'timestamp'
        
        Returns:
            Dict with value breakdowns
        """
        
        if not tracking_events:
            return {
                'total_value': 0.0,
                'daily_value': 0.0,
                'monthly_value': 0.0,
                'yearly_value': 0.0,
                'by_company': {},
                'top_earners': []
            }
        
        # Calculate total value
        total_value = 0.0
        company_values = {}
        
        for event in tracking_events:
            company = event.get('company', 'Unknown')
            category = event.get('category', 'Other')
            risk = event.get('risk_score', 5.0)
            
            event_value = self.calculate_event_value(company, category, risk)
            total_value += event_value
            
            # Track by company
            if company not in company_values:
                company_values[company] = 0.0
            company_values[company] += event_value
        
        # Calculate time-based values
        if tracking_events:
            timestamps = [e.get('timestamp') for e in tracking_events if e.get('timestamp')]
            if timestamps:
                oldest = min(timestamps) if isinstance(timestamps[0], datetime) else datetime.now()
                newest = max(timestamps) if isinstance(timestamps[0], datetime) else datetime.now()
                days_tracked = max((newest - oldest).days, 1)
            else:
                days_tracked = 1
        else:
            days_tracked = 1
        
        daily_avg = total_value / days_tracked
        monthly_value = daily_avg * 30
        yearly_value = daily_avg * 365
        
        # Get top earners
        top_earners = sorted(
            [(company, value) for company, value in company_values.items()],
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return {
            'total_value': round(total_value, 2),
            'daily_value': round(daily_avg, 2),
            'monthly_value': round(monthly_value, 2),
            'yearly_value': round(yearly_value, 2),
            'days_tracked': days_tracked,
            'by_company': {k: round(v, 2) for k, v in company_values.items()},
            'top_earners': top_earners,
            'events_analyzed': len(tracking_events)
        }
    
    def get_shocking_facts(self, value_data: Dict) -> List[str]:
        """Generate shocking facts about data value"""
        
        yearly = value_data['yearly_value']
        monthly = value_data['monthly_value']
        
        facts = []
        
        # Comparison facts
        if yearly > 0:
            facts.append(f"💰 Companies make ${yearly:.2f}/year from YOUR data")
            
            if yearly >= 1000:
                facts.append(f"🤯 That's ${yearly * 10:.2f} over 10 years!")
            
            if yearly >= 100:
                netflix_months = int(yearly / 15.49)  # Netflix subscription
                facts.append(f"📺 That's {netflix_months} months of Netflix!")
            
            if monthly >= 50:
                facts.append(f"☕ That's {int(monthly / 5)} fancy coffees per month!")
            
            # Per company
            top_earner = value_data['top_earners'][0] if value_data['top_earners'] else None
            if top_earner:
                company, value = top_earner
                facts.append(f"🎯 {company} alone makes ${value:.2f} from you")
        
        # Event-based facts
        events = value_data['events_analyzed']
        if events > 0:
            per_event_avg = value_data['total_value'] / events
            facts.append(f"📊 Each tracking event = ${per_event_avg:.4f}")
            
            if events > 1000:
                facts.append(f"😱 You've been tracked {events:,} times!")
        
        return facts
    
    def format_value_report(self, value_data: Dict) -> str:
        """Format a text report of data value"""
        
        report = "\n" + "="*70 + "\n"
        report += "💰 YOUR DATA VALUE REPORT\n"
        report += "="*70 + "\n\n"
        
        report += f"Total Events Analyzed: {value_data['events_analyzed']:,}\n"
        report += f"Tracking Period: {value_data['days_tracked']} days\n\n"
        
        report += "📊 WHAT YOUR DATA IS WORTH:\n"
        report += f"  Daily:   ${value_data['daily_value']:.2f}\n"
        report += f"  Monthly: ${value_data['monthly_value']:.2f}\n"
        report += f"  Yearly:  ${value_data['yearly_value']:.2f}\n\n"
        
        report += "🎯 TOP COMPANIES PROFITING FROM YOU:\n"
        for idx, (company, value) in enumerate(value_data['top_earners'][:5], 1):
            report += f"  {idx}. {company}: ${value:.2f}\n"
        
        report += "\n🔥 SHOCKING FACTS:\n"
        for fact in self.get_shocking_facts(value_data):
            report += f"  • {fact}\n"
        
        report += "\n" + "="*70 + "\n"
        
        return report


def calculate_from_database(db_connection) -> Dict:
    """
    Calculate data value from tracking database
    
    Args:
        db_connection: Database connection with tracking events
    
    Returns:
        Value calculation results
    """
    calculator = DataValueCalculator()
    
    # Query all tracking events
    cursor = db_connection.cursor()
    cursor.execute("""
        SELECT company_name, category, risk_score, timestamp
        FROM tracking_events
        ORDER BY timestamp
    """)
    
    events = []
    for row in cursor.fetchall():
        events.append({
            'company': row[0],
            'category': row[1],
            'risk_score': row[2],
            'timestamp': datetime.fromisoformat(row[3]) if row[3] else datetime.now()
        })
    
    return calculator.calculate_total_value(events)
