"""Entity Mapper for Digital Forensic Surgeon.
Translates technical domains into human-readable company names.
"""

from typing import Dict, Optional

class EntityMapper:
    """Maps domains to company entities."""
    
    def __init__(self):
        self.entity_map = self._init_entity_map()
        
    def _init_entity_map(self) -> Dict[str, str]:
        """Initialize the domain to entity mapping."""
        return {
            # Google / Alphabet
            'google.com': 'Google',
            'googleapis.com': 'Google',
            'gstatic.com': 'Google',
            'google-analytics.com': 'Google',
            'googlesyndication.com': 'Google',
            'doubleclick.net': 'Google',
            '1e100.net': 'Google',
            'youtube.com': 'Google',
            'ytimg.com': 'Google',
            'ggpht.com': 'Google',
            'googleusercontent.com': 'Google',
            'gvt1.com': 'Google',
            'gvt2.com': 'Google',
            'gmail.com': 'Google',
            'googleadservices.com': 'Google',
            
            # Meta / Facebook
            'facebook.com': 'Meta',
            'fbcdn.net': 'Meta',
            'fbsbx.com': 'Meta',
            'instagram.com': 'Meta',
            'cdninstagram.com': 'Meta',
            'whatsapp.com': 'Meta',
            'whatsapp.net': 'Meta',
            'messenger.com': 'Meta',
            'tfbnw.net': 'Meta',
            
            # Amazon
            'amazon.com': 'Amazon',
            'amazonaws.com': 'Amazon',
            'ssl-images-amazon.com': 'Amazon',
            'media-amazon.com': 'Amazon',
            'a2z.com': 'Amazon',
            'cloudfront.net': 'Amazon (AWS)',
            
            # Microsoft
            'microsoft.com': 'Microsoft',
            'live.com': 'Microsoft',
            'office.com': 'Microsoft',
            'office365.com': 'Microsoft',
            'bing.com': 'Microsoft',
            'azure.com': 'Microsoft',
            'windows.net': 'Microsoft',
            'azureedge.net': 'Microsoft',
            'skype.com': 'Microsoft',
            'linkedin.com': 'Microsoft',
            'licdn.com': 'Microsoft',
            'github.com': 'Microsoft',
            'githubusercontent.com': 'Microsoft',
            
            # Apple
            'apple.com': 'Apple',
            'icloud.com': 'Apple',
            'mzstatic.com': 'Apple',
            'cdn-apple.com': 'Apple',
            'aaplimg.com': 'Apple',
            
            # Twitter / X
            'twitter.com': 'X (Twitter)',
            'twimg.com': 'X (Twitter)',
            't.co': 'X (Twitter)',
            'x.com': 'X (Twitter)',
            
            # Ad Tech & Trackers
            'criteo.com': 'Criteo (Ad Tech)',
            'outbrain.com': 'Outbrain (Ad Tech)',
            'taboola.com': 'Taboola (Ad Tech)',
            'rubiconproject.com': 'Rubicon Project (Ad Tech)',
            'pubmatic.com': 'PubMatic (Ad Tech)',
            'openx.net': 'OpenX (Ad Tech)',
            'adnxs.com': 'AppNexus (Ad Tech)',
            'smartadserver.com': 'Smart AdServer',
            'adroll.com': 'AdRoll',
            'hotjar.com': 'Hotjar (Analytics)',
            'segment.io': 'Segment (Analytics)',
            'mixpanel.com': 'Mixpanel (Analytics)',
            'newrelic.com': 'New Relic (Analytics)',
            'scorecardresearch.com': 'Comscore (Analytics)',
            
            # CDNs & Infrastructure
            'cloudflare.com': 'Cloudflare',
            'cloudflare.net': 'Cloudflare',
            'fastly.net': 'Fastly',
            'akamai.net': 'Akamai',
            'akamaiedge.net': 'Akamai',
            'akamaitechnologies.com': 'Akamai',
        }
        
    def get_entity(self, domain: str) -> str:
        """Get the entity name for a given domain."""
        if not domain:
            return "Unknown"
            
        domain = domain.lower().strip()
        
        # Direct match
        if domain in self.entity_map:
            return self.entity_map[domain]
            
        # Suffix match (e.g., sub.google.com -> Google)
        parts = domain.split('.')
        if len(parts) >= 2:
            # Check root domain (example.com)
            root_domain = f"{parts[-2]}.{parts[-1]}"
            if root_domain in self.entity_map:
                return self.entity_map[root_domain]
                
            # Check with one more level (co.uk, etc - simplified)
            if len(parts) >= 3:
                sub_root = f"{parts[-3]}.{parts[-2]}.{parts[-1]}"
                if sub_root in self.entity_map:
                    return self.entity_map[sub_root]
                    
        return domain  # Return original domain if no mapping found
