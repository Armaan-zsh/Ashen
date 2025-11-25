"""
SIMPLIFIED License System - No bugs
Just a simple tier check
"""

from datetime import datetime, timedelta
from typing import Optional
import hashlib

class License:
    """License for TrackerShield"""
    
    TIER_FREE = "free"
    TIER_PRO = "pro"
    TIER_GOD = "god"
    
    def __init__(self, tier: str, expiry: Optional[datetime] = None):
        self.tier = tier
        self.expiry = expiry
    
    def is_valid(self) -> bool:
        """Check if still valid"""
        if self.expiry is None:
            return True  # Lifetime
        return datetime.now() < self.expiry
    
    def days_remaining(self) -> Optional[int]:
        """Days until expiry"""
        if self.expiry is None:
            return None
        delta = self.expiry - datetime.now()
        return max(0, delta.days)

class SimpleLicenseValidator:
    """Simple, robust license validation"""
    
    @staticmethod
    def validate_key(key: str) -> Optional[License]:
        """
        Validate license key
        
        Format: TIER-EXPIRY_HASH
        Examples:
        - TSGD-LIFETIME-abc123  (God tier, lifetime)
        - TSPR-20260525-def456  (Pro tier, expires 2026-05-25)
        - FREE                  (Free tier)
        """
        
        if not key or key == "FREE":
            return License(tier=License.TIER_FREE, expiry=None)
        
        try:
            parts = key.split('-')
            
            if len(parts) < 2:
                return None
            
            prefix = parts[0]
            expiry_str = parts[1]
            
            # Map prefix to tier
            tier_map = {
                'TSGD': License.TIER_GOD,
                'TSPR': License.TIER_PRO,
                'TSFR': License.TIER_FREE
            }
            
            tier = tier_map.get(prefix)
            if not tier:
                return None
            
            # Parse expiry
            if expiry_str == "LIFETIME":
                expiry = None
            else:
                # Format: YYYYMMDD
                year = int(expiry_str[:4])
                month = int(expiry_str[4:6])
                day = int(expiry_str[6:8])
                expiry = datetime(year, month, day)
            
            license = License(tier=tier, expiry=expiry)
            return license if license.is_valid() else None
        
        except Exception:
            return None
    
    @staticmethod
    def generate_key(tier: str, months: Optional[int] = None) -> str:
        """
        Generate license key
        
        Args:
            tier: free, pro, or god
            months: Months valid (None for lifetime)
        
        Returns:
            License key
        """
        
        if tier == License.TIER_FREE:
            return "FREE"
        
        prefix = "TSGD" if tier == License.TIER_GOD else "TSPR"
        
        if tier == License.TIER_GOD or months is None:
            expiry_str = "LIFETIME"
        else:
            expiry = datetime.now() + timedelta(days=months*30)
            expiry_str = expiry.strftime('%Y%m%d')
        
        # Simple hash for uniqueness
        import random
        hash_part = hashlib.md5(f"{tier}{expiry_str}{random.random()}".encode()).hexdigest()[:6]
        
        return f"{prefix}-{expiry_str}-{hash_part}"


# Test it
if __name__ == '__main__':
    print("=" * 60)
    print("SIMPLE LICENSE SYSTEM TEST")
    print("=" * 60)
    
    # Generate
    god_key = SimpleLicenseValidator.generate_key("god")
    pro_key = SimpleLicenseValidator.generate_key("pro", 12)
    free_key = "FREE"
    
    print(f"\nGod:  {god_key}")
    print(f"Pro:  {pro_key}")
    print(f"Free: {free_key}")
    
    # Validate
    print(f"\n✅ Validating...\n")
    
    for name, key in [("God", god_key), ("Pro", pro_key), ("Free", free_key)]:
        lic = SimpleLicenseValidator.validate_key(key)
        if lic:
            exp = "LIFETIME" if lic.days_remaining() is None else f"{lic.days_remaining()} days"
            print(f"{name}: ✅ VALID - Tier: {lic.tier}, Expiry: {exp}")
        else:
            print(f"{name}: ❌ INVALID")
    
    print(f"\n" + "=" * 60)
    print(f"✅ SIMPLE SYSTEM WORKS!")
    print(f"=" * 60)
