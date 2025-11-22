"""
Intelligence module for Digital Forensic Surgeon.
Provides entity resolution and other intelligence-gathering capabilities.
"""

from __future__ import annotations

class EntityResolver:
    """Maps thousands of domains to a few big tech giants."""
    
    DOMAIN_MAP = {
        "instagram.com": "Meta",
        "fbcdn.net": "Meta",
        "whatsapp.com": "Meta",
        "facebook.com": "Meta",
        "messenger.com": "Meta",
        "oculus.com": "Meta",
        "google-analytics.com": "Google",
        "doubleclick.net": "Google",
        "1e100.net": "Google",
        "google.com": "Google",
        "youtube.com": "Google",
        "gmail.com": "Google",
        "googleadservices.com": "Google",
        "googlesyndication.com": "Google",
        "android.com": "Google",
        "aws.amazon.com": "Amazon",
        "amazon.com": "Amazon",
        "a9.com": "Amazon",
        "twitch.tv": "Amazon",
        "apple.com": "Apple",
        "icloud.com": "Apple",
        "itunes.com": "Apple",
        "microsoft.com": "Microsoft",
        "live.com": "Microsoft",
        "office.com": "Microsoft",
        "linkedin.com": "Microsoft",
        "github.com": "Microsoft",
        "skype.com": "Microsoft",
        "twitter.com": "Twitter",
        "t.co": "Twitter",
        "x.com": "Twitter",
    }

    def resolve(self, domain: str) -> str:
        """
        Resolves a domain to a parent entity.
        Returns the entity name (e.g., "Google") or the original domain if no mapping is found.
        """
        if not domain:
            return "Uncategorized"
            
        # Check for exact match
        if domain in self.DOMAIN_MAP:
            return self.DOMAIN_MAP[domain]
            
        # Check for subdomains
        parts = domain.split('.')
        for i in range(len(parts) - 1):
            sub_domain = '.'.join(parts[i:])
            if sub_domain in self.DOMAIN_MAP:
                return self.DOMAIN_MAP[sub_domain]
                
        return domain
