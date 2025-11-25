"""
TrackerShield mitmproxy Addon
Signature-based tracker detection
"""

from mitmproxy import http, ctx
from datetime import datetime
import json
from pathlib import Path
from urllib.parse import urlparse

from tracker_shield.compiler.sig_compiler import SignatureCompiler
from tracker_shield.engine.matcher import SignatureMatcher
from tracker_shield.license.validator import LicenseGenerator, License

class TrackerShieldAddon:
    """TrackerShield signature-based interceptor"""
    
    def __init__(self, license_key: str = None):
        """
        Initialize with license key
        
        Args:
            license_key: License key (None = free tier)
        """
        self.events_captured = 0
        self.live_events_file = Path.home() / ".mitmproxy" / "live_events.jsonl"
        self.live_events_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Validate license and load appropriate database
        self.license = self._validate_license(license_key)
        self.tier = self.license.tier if self.license else License.TIER_FREE
        
        # Load signature database
        self.matcher = self._load_signatures()
        
        # Store initialization info for later logging
        self.init_info = {
            'tier': self.tier.upper(),
            'signatures': len(self.matcher.signatures)
        }
    
    def _validate_license(self, key: str) -> License:
        """Validate license key"""
        if not key:
            return License(tier=License.TIER_FREE, email="", expiry=None)
        
        license = LicenseGenerator.validate_key(key)
        
        if license:
            # Store validation result for later logging
            self.license_status = f"Valid {license.tier} license"
            if license.days_remaining():
                self.license_status += f" - Expires in {license.days_remaining()} days"
            else:
                self.license_status += " - LIFETIME access"
            return license
        else:
            self.license_status = "Invalid license - using FREE tier"
            return License(tier=License.TIER_FREE, email="", expiry=None)
    
    def _load_signatures(self) -> SignatureMatcher:
        """Load signature database for current tier"""
        
        compiler = SignatureCompiler()
        db_path = Path(f'tracker_shield/data/tracker_shield_{self.tier}.tsdb')
        
        if not db_path.exists():
            raise FileNotFoundError(f"Signature database missing: {db_path}")
        
        signatures = compiler.load_database(db_path)
        return SignatureMatcher(signatures)
    
    def request(self, flow: http.HTTPFlow):
        """Intercept and analyze requests"""
        
        # Log initialization info on first request
        if self.events_captured == 0:
            ctx.log.info(f"🛡️  TrackerShield - Tier: {self.init_info['tier']}")
            ctx.log.info(f"📊 Loaded {self.init_info['signatures']} signatures")
            if hasattr(self, 'license_status'):
                ctx.log.info(f"🔑 {self.license_status}")
        
        url = flow.request.pretty_url
        
        # Match against signatures
        matches = self.matcher.match(
            url=url,
            method=flow.request.method,
            headers=dict(flow.request.headers),
            body=flow.request.text if flow.request.method == "POST" else None
        )
        
        if not matches:
            return  # Not a tracker
        
        # Process matches
        for match in matches:
            self.events_captured += 1
            
            # Create event
            event = {
                'event_id': self.events_captured,
                'timestamp': datetime.now().isoformat(),
                'signature_id': match.signature.id,
                'tracker_name': match.signature.name,
                'company': match.signature.company,
                'category': match.signature.category,
                'risk_score': match.signature.risk_score,
                'confidence': round(match.confidence * 100, 1),
                'url': url[:150] + '...' if len(url) > 150 else url,
                'evidence': match.evidence,
                'tier': match.signature.tier
            }
            
            # Broadcast to live feed
            self._broadcast_live(event)
            
            # Log to console
            risk_emoji = "🔴" if match.signature.risk_score >= 8 else "🟡" if match.signature.risk_score >= 6 else "🟢"
            ctx.log.info(f"{risk_emoji} TRACKER #{self.events_captured}: {match.signature.name}")
            ctx.log.info(f"   Company: {match.signature.company}")
            ctx.log.info(f"   Risk: {match.signature.risk_score}/10")
            ctx.log.info(f"   Confidence: {match.confidence:.0%}")
            
            if match.evidence:
                ctx.log.info(f"   Evidence: {json.dumps(match.evidence, indent=2)}")
    
    def _broadcast_live(self, event: dict):
        """Broadcast event to live feed"""
        try:
            with open(self.live_events_file, 'a') as f:
                f.write(json.dumps(event) + '\n')
        except Exception as e:
            ctx.log.error(f"Failed to broadcast: {e}")
    
    def response(self, flow: http.HTTPFlow):
        """Intercept responses (for future use)"""
        pass


# Entry point for mitmproxy
def load(loader):
    """Load addon with configuration"""
    loader.add_option(
        name="trackershield_license",
        typespec=str,
        default="",
        help="TrackerShield license key (leave empty for free tier)"
    )

def configure(updates):
    """Called when configuration changes"""
    pass

# Create addon instance
addons = [
    TrackerShieldAddon(
        license_key=None  # Will be set via --set trackershield_license=KEY
    )
]
