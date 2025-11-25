"""
Unknown Payload Detector
Detects tracking even without signatures using heuristics
"""

from typing import Dict, List, Optional
from urllib.parse import urlparse, parse_qs
import re
import base64
import json

class UnknownPayloadDetector:
    """Detects unknown trackers using heuristics"""
    
    # Known tracking domains (for quick filtering)
    KNOWN_TRACKERS = {
        'facebook.com', 'google-analytics.com', 'tiktok.com',
        'amazon-adsystem.com', 'doubleclick.net', 'googleadservices.com',
        'analytics', 'tracker', 'pixel', 'collect', 'ping', 'beacon'
    }
    
    # Suspicious patterns
    TRACKING_INDICATORS = [
        r'pixel',
        r'track',
        r'analytics',
        r'beacon',
        r'collect',
        r'event',
        r'impression',
        r'click',
        r'conversion'
    ]
    
    def __init__(self):
        self.suspicious_requests = []
    
    def is_tracking_request(self, url: str, method: str = 'GET', 
                           headers: Dict = None, body: str = None) -> Optional[Dict]:
        """
        Detect if request is likely tracking
        
        Returns:
            Dict with detection details if tracking, None otherwise
        """
        
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        
        score = 0
        reasons = []
        
        # 1. Domain check
        if self._is_known_tracker_domain(parsed.netloc):
            score += 30
            reasons.append("Known tracker domain")
        
        # 2. Path analysis
        if self._has_tracking_path(parsed.path):
            score += 20
            reasons.append("Tracking-related path")
        
        # 3. Parameter analysis
        param_score = self._analyze_parameters(params)
        score += param_score
        if param_score > 0:
            reasons.append(f"Suspicious parameters ({param_score} points)")
        
        # 4. Data size check
        if len(parsed.query) > 200:
            score += 15
            reasons.append("Large query string")
        
        # 5. Base64 encoded data
        if self._has_encoded_data(parsed.query):
            score += 20
            reasons.append("Base64 encoded data")
        
        # 6. POST body analysis
        if body and len(body) > 100:
            score += 10
            reasons.append("Large POST body")
        
        # 7. Headers analysis
        if headers:
            if self._has_tracking_headers(headers):
                score += 15
                reasons.append("Tracking headers")
        
        # Decision threshold
        if score >= 40:  # Likely tracking
            return {
                'url': url,
                'score': score,
                'confidence': min(100, score),
                'reasons': reasons,
                'domain': parsed.netloc,
                'path': parsed.path,
                'param_count': len(params)
            }
        
        return None
    
    def _is_known_tracker_domain(self, domain: str) -> bool:
        """Check if domain is known tracker"""
        domain_lower = domain.lower()
        return any(tracker in domain_lower for tracker in self.KNOWN_TRACKERS)
    
    def _has_tracking_path(self, path: str) -> bool:
        """Check if path suggests tracking"""
        path_lower = path.lower()
        return any(re.search(pattern, path_lower) for pattern in self.TRACKING_INDICATORS)
    
    def _analyze_parameters(self, params: Dict) -> int:
        """Analyze URL parameters for tracking indicators"""
        score = 0
        
        # Common tracking parameter names
        tracking_params = {
            'id', 'uid', 'cid', 'tid', 'pid', 'event', 'ev',
            'session', 'user', 'click', 'impression', 'conversion',
            'timestamp', 'ts', 'referrer', 'ref', 'url', 'page'
        }
        
        for key in params.keys():
            key_lower = key.lower()
            if key_lower in tracking_params:
                score += 5
            
            # Long parameter values (likely IDs)
            values = params[key]
            if values and len(values[0]) > 20:
                score += 3
        
        return min(score, 30)  # Cap at 30
    
    def _has_encoded_data(self, query: str) -> bool:
        """Check for base64 encoded data"""
        if not query:
            return False
        
        # Look for base64-like strings
        base64_pattern = r'[A-Za-z0-9+/]{20,}={0,2}'
        matches = re.findall(base64_pattern, query)
        
        for match in matches:
            try:
                decoded = base64.b64decode(match)
                # If it decodes successfully, likely encoded data
                return True
            except:
                pass
        
        return False
    
    def _has_tracking_headers(self, headers: Dict) -> bool:
        """Check for tracking-related headers"""
        tracking_headers = {
            'x-requested-with',
            'x-tracking',
            'x-analytics',
            'x-client-id'
        }
        
        header_keys = {k.lower() for k in headers.keys()}
        return bool(tracking_headers & header_keys)
    
    def store_unknown(self, detection: Dict) -> str:
        """
        Store unknown tracking request
        
        Returns:
            Hash of the anonymized request
        """
        
        # Strip PII before hashing
        anonymized = {
            'domain': detection['domain'],
            'path': detection['path'],
            'param_count': detection['param_count'],
            'score': detection['score']
        }
        
        # Hash it
        import hashlib
        hash_str = json.dumps(anonymized, sort_keys=True)
        req_hash = hashlib.sha256(hash_str.encode()).hexdigest()
        
        # Store locally
        self.suspicious_requests.append({
            'hash': req_hash,
            'data': anonymized,
            'timestamp': __import__('datetime').datetime.now().isoformat()
        })
        
        return req_hash


# Test it
if __name__ == '__main__':
    detector = UnknownPayloadDetector()
    
    # Test URLs
    test_urls = [
        "https://tracking.example.com/pixel?id=12345&event=pageview&uid=abc123def456",
        "https://analytics.site.com/collect?v=1&tid=UA-12345&cid=xyz&t=pageview",
        "https://example.com/api/users",  # Not tracking
        "https://ad.doubleclick.net/ddm/trackimp/N123.456?dc_trk_aid=789&dc_trk_cid=012",
    ]
    
    print("=" * 60)
    print("Unknown Payload Detector Test")
    print("=" * 60)
    
    for url in test_urls:
        result = detector.is_tracking_request(url)
        
        if result:
            print(f"\n🚨 TRACKING DETECTED:")
            print(f"   URL: {url[:60]}...")
            print(f"   Score: {result['score']}")
            print(f"   Confidence: {result['confidence']}%")
            print(f"   Reasons: {', '.join(result['reasons'])}")
            
            hash_id = detector.store_unknown(result)
            print(f"   Hash: {hash_id[:16]}...")
        else:
            print(f"\n✅ Clean: {url[:60]}...")
    
    print(f"\n📊 Stored {len(detector.suspicious_requests)} unknown tracking requests")
