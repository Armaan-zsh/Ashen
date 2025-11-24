"""
Query Cache for Dashboard
Caches expensive queries to reduce database load
"""

from functools import lru_cache
from datetime import datetime, timedelta
import hashlib
import json

class QueryCache:
    """Simple in-memory cache for database queries"""
    
    def __init__(self, ttl_seconds=60):
        self.cache = {}
        self.ttl = ttl_seconds
    
    def _make_key(self, query, params):
        """Generate cache key from query and params"""
        key_str = f"{query}:{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, query, params):
        """Get cached result if still valid"""
        key = self._make_key(query, params)
        
        if key in self.cache:
            result, timestamp = self.cache[key]
            age = (datetime.now() - timestamp).total_seconds()
            
            if age < self.ttl:
                return result
            else:
                # Expired
                del self.cache[key]
        
        return None
    
    def set(self, query, params, result):
        """Cache query result"""
        key = self._make_key(query, params)
        self.cache[key] = (result, datetime.now())
    
    def clear(self):
        """Clear all cached entries"""
        self.cache.clear()
    
    def clear_old(self, max_age_seconds=300):
        """Remove entries older than max_age"""
        now = datetime.now()
        expired = [
            key for key, (_, timestamp) in self.cache.items()
            if (now - timestamp).total_seconds() > max_age_seconds
        ]
        for key in expired:
            del self.cache[key]


# Global cache instance (60 second TTL)
query_cache = QueryCache(ttl_seconds=60)
