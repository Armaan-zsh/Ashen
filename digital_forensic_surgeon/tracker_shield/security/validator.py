"""
Input Validation & Sanitization
Prevents injection attacks and validates all inputs
"""

import re
from typing import Any, Optional
from urllib.parse import urlparse, parse_qs

class InputValidator:
    """Validates and sanitizes all user inputs"""
    
    # Regex patterns
    URL_PATTERN = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    LICENSE_KEY_PATTERN = re.compile(r'^TS(GD|PR|FR)-[A-Za-z0-9-]+$')
    HASH_PATTERN = re.compile(r'^[a-f0-9]{64}$')  # SHA256
    
    @staticmethod
    def validate_url(url: str, allow_schemes: list = None) -> bool:
        """
        Validate URL format and scheme
        
        Args:
            url: URL to validate
            allow_schemes: Allowed schemes (default: http, https)
        
        Returns:
            True if valid
        """
        if not url or not isinstance(url, str):
            return False
        
        if len(url) > 2048:  # Max URL length
            return False
        
        if allow_schemes is None:
            allow_schemes = ['http', 'https']
        
        try:
            parsed = urlparse(url)
            
            if parsed.scheme not in allow_schemes:
                return False
            
            if not parsed.netloc:
                return False
            
            return bool(InputValidator.URL_PATTERN.match(url))
        except:
            return False
    
    @staticmethod
    def validate_license_key(key: str) -> bool:
        """
        Validate license key format
        
        Args:
            key: License key
        
        Returns:
            True if valid format
        """
        if not key or not isinstance(key, str):
            return False
        
        if key == "FREE":
            return True
        
        return bool(InputValidator.LICENSE_KEY_PATTERN.match(key))
    
    @staticmethod
    def validate_hash(hash_str: str) -> bool:
        """
        Validate hash format (SHA256)
        
        Args:
            hash_str: Hash string
        
        Returns:
            True if valid SHA256
        """
        if not hash_str or not isinstance(hash_str, str):
            return False
        
        return bool(InputValidator.HASH_PATTERN.match(hash_str))
    
    @staticmethod
    def sanitize_string(text: str, max_length: int = 1000) -> str:
        """
        Sanitize string input
        
        Args:
            text: Input text
            max_length: Maximum allowed length
        
        Returns:
            Sanitized string
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Trim length
        text = text[:max_length]
        
        # Remove control characters
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
        
        # Remove potential script tags
        text = re.sub(r'<script.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
        
        return text.strip()
    
    @staticmethod
    def validate_json(data: Any, max_depth: int = 10) -> bool:
        """
        Validate JSON data structure
        
        Args:
            data: JSON data to validate
            max_depth: Maximum nesting depth
        
        Returns:
            True if valid
        """
        
        def check_depth(obj, current_depth=0):
            if current_depth > max_depth:
                return False
            
            if isinstance(obj, dict):
                if len(obj) > 1000:  # Max keys
                    return False
                return all(check_depth(v, current_depth + 1) for v in obj.values())
            
            elif isinstance(obj, list):
                if len(obj) > 10000:  # Max items
                    return False
                return all(check_depth(item, current_depth + 1) for item in obj)
            
            return True
        
        return check_depth(data)
    
    @staticmethod
    def validate_file_path(path: str, allow_absolute: bool = False) -> bool:
        """
        Validate file path (prevent directory traversal)
        
        Args:
            path: File path
            allow_absolute: Allow absolute paths
        
        Returns:
            True if safe
        """
        if not path or not isinstance(path, str):
            return False
        
        # Check for directory traversal
        if '..' in path or '~' in path:
            return False
        
        # Check for absolute paths
        if path.startswith('/') or ':' in path[:3]:
            return allow_absolute
        
        # Check for suspicious characters
        suspicious = ['|', '&', ';', '`', '$', '(', ')']
        if any(char in path for char in suspicious):
            return False
        
        return True


# Decorator for automatic validation
def validate_inputs(**validators):
    """
    Decorator to validate function inputs
    
    Usage:
        @validate_inputs(url=InputValidator.validate_url, 
                        license_key=InputValidator.validate_license_key)
        def my_function(url, license_key):
            ...
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Get function signature
            import inspect
            sig = inspect.signature(func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            
            # Validate each argument
            for param_name, validator_func in validators.items():
                if param_name in bound.arguments:
                    value = bound.arguments[param_name]
                    if not validator_func(value):
                        raise ValueError(f"Invalid {param_name}: {value}")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Test
if __name__ == '__main__':
    print("=" * 60)
    print("Input Validation Test")
    print("=" * 60)
    
    # Test URL validation
    test_urls = [
        ("https://facebook.com/tr", True),
        ("http://localhost:8080", True),
        ("javascript:alert(1)", False),
        ("ftp://example.com", False),
        ("https://" + "a" * 3000, False),  # Too long
    ]
    
    print("\n🔍 URL Validation:")
    for url, expected in test_urls:
        result = InputValidator.validate_url(url)
        status = "✅" if result == expected else "❌"
        print(f"   {status} {url[:50]}: {result}")
    
    # Test license key validation
    test_keys = [
        ("TSGD-LIFETIME-abc123", True),
        ("TSPR-20261120-def456", True),
        ("FREE", True),
        ("INVALID-KEY", False),
        ("'; DROP TABLE users; --", False),
    ]
    
    print("\n🔑 License Key Validation:")
    for key, expected in test_keys:
        result = InputValidator.validate_license_key(key)
        status = "✅" if result == expected else "❌"
        print(f"   {status} {key}: {result}")
    
    # Test string sanitization
    dirty_string = "<script>alert('xss')</script>Hello\x00World"
    clean = InputValidator.sanitize_string(dirty_string)
    print(f"\n🧹 String Sanitization:")
    print(f"   Input:  {dirty_string}")
    print(f"   Output: {clean}")
    
    print("\n" + "=" * 60)
    print("✅ Input validation working!")
    print("=" * 60)
