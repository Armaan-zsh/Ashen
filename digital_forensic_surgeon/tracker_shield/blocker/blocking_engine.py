"""
Tracker Blocking Engine
Actually BLOCKS trackers, not just detects them
"""

from typing import Optional
from mitmproxy import http

class TrackerBlocker:
    """Blocks tracking requests in real-time"""
    
    def __init__(self, block_mode: str = 'soft'):
        """
        Args:
            block_mode: 'soft' (return empty), 'hard' (return 403), or 'redirect'
        """
        self.block_mode = block_mode
        self.blocked_count = 0
        self.whitelist = set()  # Domains users want to allow
    
    def should_block(self, url: str, tracker_name: str, confidence: float) -> bool:
        """
        Determine if request should be blocked
        
        Args:
            url: Request URL
            tracker_name: Name of detected tracker
            confidence: Detection confidence (0-1)
        
        Returns:
            True if should block
        """
        # Check whitelist
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        
        if domain in self.whitelist:
            return False  # User whitelisted
        
        # Block high-confidence trackers
        if confidence >= 0.7:
            return True
        
        return False
    
    def block_request(self, flow: http.HTTPFlow, tracker_name: str):
        """
        Block tracking request
        
        Args:
            flow: mitmproxy flow
            tracker_name: Name of tracker being blocked
        """
        
        self.blocked_count += 1
        
        if self.block_mode == 'soft':
            # Return empty response (tracker thinks it worked)
            flow.response = http.Response.make(
                200,  # OK status
                b"",  # Empty body
                {"Content-Type": "text/plain"}
            )
        
        elif self.block_mode == 'hard':
            # Return 403 Forbidden
            flow.response = http.Response.make(
                403,
                f"Blocked by TrackerShield: {tracker_name}".encode(),
                {"Content-Type": "text/plain"}
            )
        
        elif self.block_mode == 'redirect':
            # Redirect to localhost
            flow.response = http.Response.make(
                302,
                b"",
                {"Location": "http://localhost/blocked"}
            )
    
    def add_to_whitelist(self, domain: str):
        """Allow domain (disable blocking)"""
        self.whitelist.add(domain)
    
    def remove_from_whitelist(self, domain: str):
        """Remove domain from whitelist"""
        self.whitelist.discard(domain)


# Test
if __name__ == '__main__':
    print("=" * 60)
    print("Tracker Blocking Engine Test")
    print("=" * 60)
    
    blocker = TrackerBlocker(block_mode='soft')
    
    # Test blocking decision
    test_cases = [
        ("https://facebook.com/tr", "Facebook Pixel", 0.95),
        ("https://google.com/search", "Google Search", 0.3),
        ("https://analytics.example.com", "Unknown", 0.8),
    ]
    
    for url, tracker, confidence in test_cases:
        should_block = blocker.should_block(url, tracker, confidence)
        status = "🚫 BLOCK" if should_block else "✅ ALLOW"
        print(f"\n{status}: {tracker}")
        print(f"   URL: {url}")
        print(f"   Confidence: {confidence:.0%}")
    
    print(f"\n📊 Total blocked: {blocker.blocked_count}")
    
    print("\n" + "=" * 60)
    print("✅ Blocking engine ready!")
    print("=" * 60)
