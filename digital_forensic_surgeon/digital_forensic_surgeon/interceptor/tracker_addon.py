from mitmproxy import http, ctx
from datetime import datetime
import json
import re
from urllib.parse import urlparse, parse_qs
from pathlib import Path

class TrackerInterceptor:
    """Intercepts and decodes tracking requests"""
    
    # Domains to track
    TRACKER_DOMAINS = {
        'facebook.com', 'connect.facebook.net', 'facebook.net',
        'google-analytics.com', 'googletagmanager.com', 'google.com',
        'analytics.tiktok.com', 'tiktok.com',
        'amazon-adsystem.com', 'a9.com',
        'doubleclick.net', 'googlesyndication.com', 'googleadservices.com'
    }
    
    def __init__(self):
        self.events_captured = 0
        self.live_events_file = Path.home() / ".mitmproxy" / "live_events.jsonl"
        self.live_events_file.parent.mkdir(parents=True, exist_ok=True)
    
    def request(self, flow: http.HTTPFlow):
        """Intercept outgoing requests"""
        
        url = flow.request.pretty_url
        domain = urlparse(url).netloc
        
        # Check if this is a tracker domain
        if not any(tracker in domain for tracker in self.TRACKER_DOMAINS):
            return
        
        # Log the tracking request
        self.events_captured += 1
        
        tracker_type = self._identify_tracker(domain, url)
        decoded_data = self._decode_payload(flow, tracker_type)
        
        # Create live event
        live_event = {
            'event_id': self.events_captured,
            'timestamp': datetime.now().isoformat(),
            'tracker': tracker_type,
            'url': url[:100] + '...' if len(url) > 100 else url,
            'data': decoded_data
        }
        
        # Broadcast to live feed
        self._broadcast_live(live_event)
        
        # Log to console
        ctx.log.info(f"🎯 TRACKER #{self.events_captured}: {tracker_type}")
        ctx.log.info(f"   URL: {url[:100]}...")
        ctx.log.info(f"   Data: {json.dumps(decoded_data, indent=2)}")
    
    def _broadcast_live(self, event: dict):
        """Broadcast event to live feed file"""
        try:
            with open(self.live_events_file, 'a') as f:
                f.write(json.dumps(event) + '\n')
        except Exception as e:
            ctx.log.error(f"Failed to broadcast: {e}")
        
    def response(self, flow: http.HTTPFlow):
        """Intercept responses (for future use)"""
        pass
    
    def _identify_tracker(self, domain: str, url: str) -> str:
        """Identify which tracker this is"""
        
        if 'facebook' in domain or 'fb' in domain:
            if '/tr' in url or '/events' in url:
                return "Facebook Pixel"
            return "Facebook SDK"
        
        elif 'google-analytics' in domain:
            return "Google Analytics 4"
        
        elif 'googletagmanager' in domain:
            return "Google Tag Manager"
        
        elif 'tiktok' in domain:
            return "TikTok Pixel"
        
        elif 'amazon' in domain or 'a9' in domain:
            return "Amazon OneTag"
        
        elif 'doubleclick' in domain or 'googlesyndication' in domain:
            return "Google Ads / DoubleClick"
        
        return "Unknown Tracker"
    
    def _decode_payload(self, flow: http.HTTPFlow, tracker_type: str) -> dict:
        """Decode the tracking payload"""
        
        data = {}
        
        # Get query parameters
        parsed = urlparse(flow.request.pretty_url)
        params = parse_qs(parsed.query)
        
        # Get POST body if present
        body = None
        if flow.request.method == "POST":
            try:
                body = flow.request.text
            except:
                body = None
        
        # Decode based on tracker type
        if "Facebook" in tracker_type:
            data = self._decode_facebook(params, body)
        
        elif "Google Analytics" in tracker_type:
            data = self._decode_google_analytics(params, body)
        
        elif "TikTok" in tracker_type:
            data = self._decode_tiktok(params, body)
        
        elif "Amazon" in tracker_type:
            data = self._decode_amazon(params, body)
        
        elif "DoubleClick" in tracker_type or "Google Ads" in tracker_type:
            data = self._decode_google_ads(params, body)
        
        # Common fields
        data['timestamp'] = datetime.now().isoformat()
        data['referrer'] = flow.request.headers.get('referer', 'unknown')
        data['user_agent'] = flow.request.headers.get('user-agent', 'unknown')
        
        return data
    
    def _decode_facebook(self, params: dict, body: str) -> dict:
        """Decode Facebook Pixel data"""
        data = {}
        
        # Common Facebook params
        if 'id' in params:
            data['pixel_id'] = params['id'][0]
        if 'ev' in params:
            data['event'] = params['ev'][0]
        if 'dl' in params:
            data['page_url'] = params['dl'][0]
        
        # Try to parse POST body
        if body:
            try:
                body_data = json.loads(body)
                data['body'] = body_data
            except:
                data['body'] = body[:200]  # First 200 chars
        
        return data
    
    def _decode_google_analytics(self, params: dict, body: str) -> dict:
        """Decode Google Analytics 4 data"""
        data = {}
        
        # GA4 params
        if 'cid' in params:
            data['client_id'] = params['cid'][0]
        if 'en' in params:
            data['event_name'] = params['en'][0]
        if 'dl' in params:
            data['page_url'] = params['dl'][0]
        if 'dt' in params:
            data['page_title'] = params['dt'][0]
        
        return data
    
    def _decode_tiktok(self, params: dict, body: str) -> dict:
        """Decode TikTok Pixel data"""
        data = {}
        
        # TikTok params
        if body:
            try:
                body_data = json.loads(body)
                data['events'] = body_data.get('events', [])
            except:
                pass
        
        return data
    
    def _decode_amazon(self, params: dict, body: str) -> dict:
        """Decode Amazon OneTag data"""
        data = {}
        
        # Amazon params
        if 'id' in params:
            data['advertiser_id'] = params['id'][0]
        
        return data
    
    def _decode_google_ads(self, params: dict, body: str) -> dict:
        """Decode Google Ads / DoubleClick data"""
        data = {}
        
        # DoubleClick params
        if 'id' in params:
            data['advertiser_id'] = params['id'][0]
        if 'label' in params:
            data['conversion_label'] = params['label'][0]
        
        return data


# Entry point for mitmproxy
addons = [TrackerInterceptor()]
