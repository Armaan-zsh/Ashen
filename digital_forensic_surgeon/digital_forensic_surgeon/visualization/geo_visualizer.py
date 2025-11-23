"""
Geographic Visualizer
Shows where tracking data travels globally
"""

from typing import List, Dict
import plotly.graph_objects as go
import plotly.express as px
from collections import Counter


# Company headquarters locations (approximate)
COMPANY_LOCATIONS = {
    'Google': {'lat': 37.4220, 'lon': -122.0841, 'country': 'USA', 'city': 'Mountain View'},
    'Facebook': {'lat': 37.4849, 'lon': -122.1477, 'country': 'USA', 'city': 'Menlo Park'},
    'Meta': {'lat': 37.4849, 'lon': -122.1477, 'country': 'USA', 'city': 'Menlo Park'},
    'Amazon': {'lat': 47.6062, 'lon': -122.3321, 'country': 'USA', 'city': 'Seattle'},
    'Microsoft': {'lat': 47.6420, 'lon': -122.1392, 'country': 'USA', 'city': 'Redmond'},
    'Apple': {'lat': 37.3349, 'lon': -122.0090, 'country': 'USA', 'city': 'Cupertino'},
    'TikTok': {'lat': 39.9042, 'lon': 116.4074, 'country': 'China', 'city': 'Beijing'},
    'ByteDance': {'lat': 39.9042, 'lon': 116.4074, 'country': 'China', 'city': 'Beijing'},
    'Twitter': {'lat': 37.7749, 'lon': -122.4194, 'country': 'USA', 'city': 'San Francisco'},
    'LinkedIn': {'lat': 37.4220, 'lon': -122.0841, 'country': 'USA', 'city': 'Mountain View'},
    'Adobe': {'lat': 37.3352, 'lon': -121.8939, 'country': 'USA', 'city': 'San Jose'},
    'Oracle': {'lat': 37.5483, 'lon': -121.9886, 'country': 'USA', 'city': 'Redwood City'},
    'Salesforce': {'lat': 37.7897, 'lon': -122.3972, 'country': 'USA', 'city': 'San Francisco'},
    'Acxiom': {'lat': 34.7465, 'lon': -92.2896, 'country': 'USA', 'city': 'Little Rock'},
    'Nielsen': {'lat': 40.7128, 'lon': -74.0060, 'country': 'USA', 'city': 'New York'},
    'Hotjar': {'lat': 35.8997, 'lon': 14.5146, 'country': 'Malta', 'city': 'Sliema'},
    'Cloudflare': {'lat': 37.7749, 'lon': -122.4194, 'country': 'USA', 'city': 'San Francisco'},
    # Add more as needed
}

# Fallback location for unknown companies (center of USA tech hub)
DEFAULT_LOCATION = {'lat': 37.7749, 'lon': -122.4194, 'country': 'USA', 'city': 'San Francisco'}


class GeoVisualizer:
    """Creates geographic visualizations of data travel"""
    
    def __init__(self, user_location: Dict = None):
        """
        Args:
            user_location: Dict with 'lat', 'lon', 'country', 'city'
        """
        if user_location is None:
            # Default to center of map
            user_location = {'lat': 20.0, 'lon': 0.0, 'country': 'Unknown', 'city': 'Your Location'}
        
        self.user_location = user_location
        self.company_data = []
    
    def analyze_tracking_geography(self, tracking_events: List[Dict]) -> Dict:
        """
        Analyze geographic distribution of trackers
        
        Args:
            tracking_events: List of dicts with 'company'
        
        Returns:
            Dict with geographic statistics
        """
        
        company_counts = Counter()
        country_counts = Counter()
        total_distance = 0
        
        for event in tracking_events:
            company = event.get('company', 'Unknown')
            company_counts[company] += 1
        
        # Map companies to locations
        for company, count in company_counts.items():
            location = COMPANY_LOCATIONS.get(company, DEFAULT_LOCATION)
            
            self.company_data.append({
                'company': company,
                'lat': location['lat'],
                'lon': location['lon'],
                'country': location['country'],
                'city': location['city'],
                'count': count
            })
            
            country_counts[location['country']] += count
            
            # Calculate distance (haversine formula simplified)
            import math
            lat1, lon1 = self.user_location['lat'], self.user_location['lon']
            lat2, lon2 = location['lat'], location['lon']
            
            # Simplified distance calculation
            dlat = math.radians(lat2 - lat1)
            dlon = math.radians(lon2 - lon1)
            a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
            c = 2 * math.asin(math.sqrt(a))
            distance = 6371 * c  # Earth radius in km
            
            total_distance += distance * count
        
        return {
            'total_distance_km': total_distance,
            'total_distance_miles': total_distance * 0.621371,
            'countries': dict(country_counts),
            'unique_countries': len(country_counts),
            'company_locations': self.company_data
        }
    
    def create_world_map(self, show_flows: bool = True) -> go.Figure:
        """
        Create interactive world map showing tracker locations
        
        Args:
            show_flows: Whether to show data flow lines
        
        Returns:
            Plotly Figure
        """
        
        fig = go.Figure()
        
        # Add data flow lines (if enabled)
        if show_flows:
            for company_loc in self.company_data:
                fig.add_trace(go.Scattergeo(
                    lon=[self.user_location['lon'], company_loc['lon']],
                    lat=[self.user_location['lat'], company_loc['lat']],
                    mode='lines',
                    line=dict(width=1, color='red'),
                    opacity=0.3,
                    hoverinfo='skip',
                    showlegend=False
                ))
        
        # Add company markers
        if self.company_data:
            lons = [c['lon'] for c in self.company_data]
            lats = [c['lat'] for c in self.company_data]
            counts = [c['count'] for c in self.company_data]
            texts = [f"{c['company']}<br>{c['city']}, {c['country']}<br>{c['count']} tracks" 
                     for c in self.company_data]
            
            fig.add_trace(go.Scattergeo(
                lon=lons,
                lat=lats,
                mode='markers+text',
                marker=dict(
                    size=[min(10 + c/10, 40) for c in counts],
                    color='red',
                    line=dict(width=1, color='white'),
                    opacity=0.8
                ),
                text=[c['company'] for c in self.company_data],
                textposition='top center',
                hovertext=texts,
                hoverinfo='text',
                showlegend=False
            ))
        
        # Add user location
        fig.add_trace(go.Scattergeo(
            lon=[self.user_location['lon']],
            lat=[self.user_location['lat']],
            mode='markers+text',
            marker=dict(
                size=30,
                color='cyan',
                symbol='star',
                line=dict(width=2, color='white')
            ),
            text=['🎯 YOU'],
            textposition='top center',
            hovertext=f"Your Location<br>{self.user_location.get('city', 'Unknown')}",
            hoverinfo='text',
            showlegend=False
        ))
        
        fig.update_layout(
            title='🌍 Where Your Data Travels',
            geo=dict(
                projection_type='natural earth',
                showland=True,
                landcolor='rgb(30, 30, 30)',
                coastlinecolor='rgb(100, 100, 100)',
                showocean=True,
                oceancolor='rgb(10, 10, 10)',
                showlakes=False,
                showcountries=True,
                countrycolor='rgb(50, 50, 50)',
                bgcolor='rgba(0, 0, 0, 0)'
            ),
            height=600,
            paper_bgcolor='#1a1a1a',
            font=dict(color='white')
        )
        
        return fig
    
    def create_country_breakdown(self) -> go.Figure:
        """Create bar chart of tracking by country"""
        
        country_counts = Counter()
        for c in self.company_data:
            country_counts[c['country']] += c['count']
        
        countries = list(country_counts.keys())
        counts = list(country_counts.values())
        
        fig = go.Figure(data=[
            go.Bar(
                x=countries,
                y=counts,
                marker_color='red',
                text=counts,
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            title='📊 Tracking by Country',
            xaxis_title='Country',
            yaxis_title='Tracking Events',
            plot_bgcolor='#1a1a1a',
            paper_bgcolor='#1a1a1a',
            font=dict(color='white'),
            height=400
        )
        
        return fig
    
    def get_travel_statistics(self) -> Dict:
        """Get interesting travel statistics"""
        
        stats = self.analyze_tracking_geography([
            {'company': c['company']} for c in self.company_data for _ in range(c['count'])
        ])
        
        facts = []
        
        km = stats['total_distance_km']
        miles = stats['total_distance_miles']
        
        if km > 0:
            # Comparisons
            earth_circumference = 40075  # km
            moon_distance = 384400  # km
            
            if km >= moon_distance:
                facts.append(f"🌙 Your data traveled far enough to reach the Moon {int(km/moon_distance)}x!")
            elif km >= earth_circumference:
                facts.append(f"🌍 Your data traveled around Earth {int(km/earth_circumference)}x!")
            else:
                facts.append(f"✈️ Your data traveled {km:,.0f} km ({miles:,.0f} miles)!")
            
            # Country stats
            facts.append(f"🗺️ Your data went to {stats['unique_countries']} countries")
            
            # Top country
            top_country = max(stats['countries'].items(), key=lambda x: x[1])
            facts.append(f"🎯 Most data went to: {top_country[0]} ({top_country[1]:,} events)")
        
        return {
            'facts': facts,
            **stats
        }


def create_from_database(db_connection, user_location: Dict = None) -> Dict:
    """
    Create geographic visualizations from database
    
    Returns:
        Dict with figures and stats
    """
    
    visualizer = GeoVisualizer(user_location)
    
    # Query events
    cursor = db_connection.cursor()
    cursor.execute("""
        SELECT company_name
        FROM tracking_events
    """)
    
    events = [{'company': row[0]} for row in cursor.fetchall()]
    
    # Analyze
    visualizer.analyze_tracking_geography(events)
    
    return {
        'world_map': visualizer.create_world_map(show_flows=True),
        'country_chart': visualizer.create_country_breakdown(),
        'stats': visualizer.get_travel_statistics()
    }
