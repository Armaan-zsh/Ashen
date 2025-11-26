"""
Tracker Domain Database
Loads and manages known tracker domains
"""

class TrackerDB:
    def __init__(self):
        # Top tracking domains (expand this with full lists later)
        self.trackers = {
            # Google
            'google-analytics.com',
            'googletagmanager.com',
            'doubleclick.net',
            'googlesyndication.com',
            'googleadservices.com',
            
            # Facebook/Meta
            'facebook.com',
            'facebook.net',
            'fbcdn.net',
            'connect.facebook.net',
            
            # Amazon
            'amazon-adsystem.com',
            
            # Microsoft
            'ads.microsoft.com',
            'telemetry.microsoft.com',
            
            # Ads
            'ads.yahoo.com',
            'adservice.google.com',
            'pagead2.googlesyndication.com',
            
            # Analytics
            'hotjar.com',
            'clarity.ms',
            'segment.com',
            'mixpanel.com',
            
            # Social
            'twitter.com',
            'platform.twitter.com',
            'tiktok.com',
            'analytics.tiktok.com'
        }
        
        print(f"📊 Loaded {len(self.trackers)} tracker domains")
    
    def is_tracker(self, domain):
        """Check if domain is a known tracker"""
        # Remove port if present
        if ':' in domain:
            domain = domain.split(':')[0]
        
        # Check exact match
        if domain in self.trackers:
            return True
        
        # Check if subdomain of tracker
        for tracker in self.trackers:
            if domain.endswith('.' + tracker) or domain == tracker:
                return True
        
        return False
    
    def add_tracker(self, domain):
        """Add new tracker domain"""
        self.trackers.add(domain)
    
    def load_from_file(self, filepath):
        """Load trackers from file (one per line)"""
        try:
            with open(filepath, 'r') as f:
                for line in f:
                    domain = line.strip()
                    if domain and not domain.startswith('#'):
                        self.trackers.add(domain)
            print(f"✅ Loaded {len(self.trackers)} trackers from {filepath}")
        except FileNotFoundError:
            print(f"⚠️ Tracker file not found: {filepath}")
