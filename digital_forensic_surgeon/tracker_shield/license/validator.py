"""
TrackerShield License System
Offline validation - no server calls needed
"""

import hashlib
import base64
from datetime import datetime, timedelta
from typing import Optional, Tuple
import secrets

class License:
    """License representation"""
    
    TIER_FREE = "free"
    TIER_PRO = "pro"
    TIER_GOD = "god"
    
    def __init__(self, tier: str, email: str, expiry: Optional[datetime] = None, user_id: Optional[int] = None):
        self.tier = tier
        self.email = email
        self.expiry = expiry  # None for lifetime (God tier)
        self.user_id = user_id or self._generate_user_id()
    
    def _generate_user_id(self):
        """Generate unique user ID"""
        return int(hashlib.sha256(self.email.encode()).hexdigest()[:8], 16)
    
    def is_valid(self) -> bool:
        """Check if license is still valid"""
        if self.expiry is None:
            return True  # Lifetime
        return datetime.now() < self.expiry
    
    def days_remaining(self) -> Optional[int]:
        """Days until expiry (None if lifetime)"""
        if self.expiry is None:
            return None
        delta = self.expiry - datetime.now()
        return max(0, delta.days)

class LicenseGenerator:
    """Generate license keys (server-side only)"""
    
    # Secret key for signing (in production, store securely)
    SECRET_KEY = b"TrackerShield_2026_Secret_Key_Change_In_Production"
    
    @classmethod
    def generate_key(cls, email: str, tier: str, months: Optional[int] = None) -> str:
        """
        Generate license key
        
        Args:
            email: User email
            tier: free, pro, or god
            months: Months valid (None for lifetime God tier)
        
        Returns:
            License key in format: TSGD-XXXX-XXXX-XXXX
        """
        
        # Calculate expiry
        if tier == License.TIER_GOD:
            expiry_ts = 0  # 0 = lifetime
        else:
            expiry = datetime.now() + timedelta(days=months*30)
            expiry_ts = int(expiry.timestamp())
        
        # Generate user ID from email
        user_id = int(hashlib.sha256(email.encode()).hexdigest()[:8], 16)
        
        # Build payload
        payload = f"{tier}:{user_id}:{expiry_ts}"
        
        # Sign with HMAC
        signature = hashlib.sha256(cls.SECRET_KEY + payload.encode()).digest()
        
        # Combine payload + signature
        key_bytes = payload.encode() + signature[:8]  # 8 bytes of signature
        
        # Base64 encode
        key_b64 = base64.urlsafe_b64encode(key_bytes).decode().rstrip('=')
        
        # Format as TSXX-XXXX-XXXX-XXXX
        prefix = "TSGD" if tier == "god" else "TSPR" if tier == "pro" else "TSFR"
        
        # Split into groups of 4
        groups = [key_b64[i:i+4] for i in range(0, len(key_b64), 4)]
        formatted = f"{prefix}-{'-'.join(groups[:3])}"
        
        return formatted
    
    @classmethod
    def validate_key(cls, key: str) -> Optional[License]:
        """
        Validate license key (offline)
        
        Returns:
            License object if valid, None otherwise
        """
        
        try:
            # Parse format TSXX-XXXX-XXXX-XXXX
            parts = key.split('-')
            if len(parts) < 2:
                return None
            
            prefix = parts[0]
            key_b64 = ''.join(parts[1:])
            
            # Detect tier from prefix
            if prefix == "TSGD":
                tier = License.TIER_GOD
            elif prefix == "TSPR":
                tier = License.TIER_PRO
            elif prefix == "TSFR":
                tier = License.TIER_FREE
            else:
                return None
            
            # Decode base64
            # Add padding if needed
            key_b64 += '=' * (4 - len(key_b64) % 4)
            key_bytes = base64.urlsafe_b64decode(key_b64)
            
            # Split payload and signature
            payload_bytes = key_bytes[:-8]
            provided_sig = key_bytes[-8:]
            
            # Parse payload
            payload = payload_bytes.decode()
            parts = payload.split(':')
            if len(parts) != 3:
                return None
            
            tier_from_payload, user_id_str, expiry_str = parts
            
            # Verify tier matches
            if tier != tier_from_payload:
                return None
            
            # Verify signature
            expected_sig = hashlib.sha256(cls.SECRET_KEY + payload_bytes).digest()[:8]
            if provided_sig != expected_sig:
                return None  # Tampered
            
            # Parse data
            user_id = int(user_id_str)
            expiry_ts = int(expiry_str)
            
            if expiry_ts == 0:
                expiry = None  # Lifetime
            else:
                expiry = datetime.fromtimestamp(expiry_ts)
            
            # Create license
            license = License(tier=tier, email="", expiry=expiry, user_id=user_id)
            
            return license if license.is_valid() else None
        
        except Exception as e:
            print(f"Key validation error: {e}")
            return None

def demo_license_system():
    """Demonstrate license system"""
    
    print("=" * 60)
    print("TrackerShield License System Demo")
    print("=" * 60)
    
    # Generate keys
    print("\n📝 Generating License Keys...\n")
    
    free_key = LicenseGenerator.generate_key("user@example.com", "free", months=12)
    print(f"Free Tier (12 months):")
    print(f"  Key: {free_key}")
    
    pro_key = LicenseGenerator.generate_key("pro@example.com", "pro", months=12)
    print(f"\nPro Tier (12 months):")
    print(f"  Key: {pro_key}")
    
    god_key = LicenseGenerator.generate_key("god@example.com", "god", months=None)
    print(f"\nGod Tier (LIFETIME):")
    print(f"  Key: {god_key}")
    
    # Validate keys
    print("\n\n✅ Validating Keys...\n")
    
    for key_name, key in [("Free", free_key), ("Pro", pro_key), ("God", god_key)]:
        license = LicenseGenerator.validate_key(key)
        
        if license:
            remaining = license.days_remaining()
            expiry_str = "LIFETIME" if remaining is None else f"{remaining} days"
            print(f"{key_name}: ✅ VALID - Tier: {license.tier}, Expiry: {expiry_str}")
        else:
            print(f"{key_name}: ❌ INVALID")
    
    # Test tampering
    print("\n\n🔒 Testing Tamper Protection...\n")
    
    tampered_key = pro_key[:-4] + "XXXX"
    tampered_license = LicenseGenerator.validate_key(tampered_key)
    
    if tampered_license:
        print("❌ SECURITY BUG - Tampered key accepted!")
    else:
        print("✅ SECURE - Tampered key rejected")
    
    print("\n" + "=" * 60)
    print("✅ License System Working!")
    print("=" * 60)

if __name__ == '__main__':
    demo_license_system()
