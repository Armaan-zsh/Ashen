"""Cryptographic utilities for Digital Forensic Surgeon."""

from __future__ import annotations

import os
import base64
import hashlib
import secrets
import logging
from pathlib import Path
from typing import Optional, Tuple
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


logger = logging.getLogger(__name__)


def generate_secure_hash(data: str, algorithm: str = "sha256") -> str:
    """Generate secure hash of data."""
    if algorithm not in ["sha256", "sha512", "blake2b", "blake2s"]:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")
    
    hasher = hashlib.new(algorithm)
    hasher.update(data.encode('utf-8'))
    return hasher.hexdigest()


def encrypt_sensitive_data(data: str, key: bytes) -> str:
    """Encrypt sensitive data using Fernet."""
    try:
        fernet = Fernet(key)
        encrypted_data = fernet.encrypt(data.encode('utf-8'))
        return base64.urlsafe_b64encode(encrypted_data).decode('utf-8')
    except Exception as e:
        logger.error(f"Failed to encrypt data: {e}")
        raise


def decrypt_sensitive_data(encrypted_data: str, key: bytes) -> str:
    """Decrypt sensitive data using Fernet."""
    try:
        fernet = Fernet(key)
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode('utf-8'))
        decrypted_data = fernet.decrypt(encrypted_bytes)
        return decrypted_data.decode('utf-8')
    except Exception as e:
        logger.error(f"Failed to decrypt data: {e}")
        raise


def create_master_key(password: str, salt: Optional[bytes] = None) -> Tuple[bytes, bytes]:
    """Create master encryption key from password."""
    if salt is None:
        salt = os.urandom(16)
    
    # Use PBKDF2 to derive key from password
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    
    key = kdf.derive(password.encode('utf-8'))
    return key, salt


def derive_key_from_password(password: str, salt: bytes) -> bytes:
    """Derive encryption key from password and salt."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    
    return kdf.derive(password.encode('utf-8'))


def generate_salt(size: int = 16) -> bytes:
    """Generate cryptographically secure random salt."""
    return secrets.token_bytes(size)


def hash_password(password: str, salt: Optional[bytes] = None) -> Tuple[str, bytes]:
    """Hash password using scrypt."""
    if salt is None:
        salt = os.urandom(16)
    
    # Use scrypt for password hashing
    hashed = hashlib.scrypt(
        password.encode('utf-8'),
        salt=salt,
        n=16384,
        r=8,
        p=1,
        maxmem=67108864  # 64MB
    )
    
    # Format: algorithm$salt$hash
    return f"scrypt${salt.hex()}${hashed.hex()}", salt


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    try:
        algorithm, salt_hex, hash_hex = hashed_password.split('$')
        
        if algorithm != "scrypt":
            return False
        
        salt = bytes.fromhex(salt_hex)
        expected_hash = hash_hex
        
        # Hash the provided password with the same salt
        actual_hash = hashlib.scrypt(
            password.encode('utf-8'),
            salt=salt,
            n=16384,
            r=8,
            p=1,
            maxmem=67108864
        )
        
        return actual_hash.hex() == expected_hash
        
    except (ValueError, Exception) as e:
        logger.error(f"Password verification failed: {e}")
        return False


def generate_api_key(length: int = 32) -> str:
    """Generate secure API key."""
    return secrets.token_urlsafe(length)


def secure_compare(a: str, b: str) -> bool:
    """Secure string comparison to prevent timing attacks."""
    if len(a) != len(b):
        return False
    
    result = 0
    for x, y in zip(a, b):
        result |= ord(x) ^ ord(y)
    
    return result == 0


def mask_sensitive_data(data: str, keep_start: int = 4, keep_end: int = 4, 
                       mask_char: str = "*") -> str:
    """Mask sensitive data while keeping start and end visible."""
    if len(data) <= keep_start + keep_end:
        return mask_char * len(data)
    
    return (data[:keep_start] + 
            mask_char * (len(data) - keep_start - keep_end) + 
            data[-keep_end:])


def secure_delete_file(file_path: Path, passes: int = 3) -> bool:
    """Securely delete file by overwriting multiple times."""
    try:
        if not file_path.exists():
            return True
        
        file_size = file_path.stat().st_size
        
        with open(file_path, 'r+b') as f:
            for _ in range(passes):
                # Overwrite with random data
                f.seek(0)
                f.write(os.urandom(file_size))
                f.flush()
                os.fsync(f.fileno())
        
        # Finally delete the file
        file_path.unlink()
        return True
        
    except Exception as e:
        logger.error(f"Failed to securely delete file {file_path}: {e}")
        return False


class EncryptionManager:
    """Manager for encryption operations."""
    
    def __init__(self, key_file: Optional[Path] = None):
        self.key_file = key_file or Path.home() / '.local' / 'share' / 'forensic_surgeon' / 'encryption.key'
        self._key = None
    
    def get_key(self) -> bytes:
        """Get or create encryption key."""
        if self._key is None:
            self._key = self._load_or_create_key()
        return self._key
    
    def _load_or_create_key(self) -> bytes:
        """Load existing key or create new one."""
        try:
            if self.key_file.exists():
                with open(self.key_file, 'rb') as f:
                    return f.read()
        except Exception as e:
            logger.warning(f"Failed to load encryption key: {e}")
        
        # Create new key
        key = Fernet.generate_key()
        self._save_key(key)
        return key
    
    def _save_key(self, key: bytes) -> None:
        """Save encryption key to file."""
        self.key_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Set restrictive permissions
        old_umask = os.umask(0o077)
        try:
            with open(self.key_file, 'wb') as f:
                f.write(key)
        finally:
            os.umask(old_umask)
    
    def encrypt_file(self, file_path: Path) -> Path:
        """Encrypt a file."""
        try:
            key = self.get_key()
            fernet = Fernet(key)
            
            with open(file_path, 'rb') as f:
                data = f.read()
            
            encrypted_data = fernet.encrypt(data)
            encrypted_path = file_path.with_suffix(file_path.suffix + '.encrypted')
            
            with open(encrypted_path, 'wb') as f:
                f.write(encrypted_data)
            
            return encrypted_path
            
        except Exception as e:
            logger.error(f"Failed to encrypt file {file_path}: {e}")
            raise
    
    def decrypt_file(self, encrypted_path: Path) -> Path:
        """Decrypt a file."""
        try:
            key = self.get_key()
            fernet = Fernet(key)
            
            with open(encrypted_path, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = fernet.decrypt(encrypted_data)
            original_path = encrypted_path.with_suffix('')
            
            if original_path.suffix == '.encrypted':
                original_path = original_path.with_suffix('')
            
            with open(original_path, 'wb') as f:
                f.write(decrypted_data)
            
            return original_path
            
        except Exception as e:
            logger.error(f"Failed to decrypt file {encrypted_path}: {e}")
            raise
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt string data."""
        key = self.get_key()
        fernet = Fernet(key)
        encrypted_data = fernet.encrypt(data.encode('utf-8'))
        return base64.urlsafe_b64encode(encrypted_data).decode('utf-8')
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt string data."""
        key = self.get_key()
        fernet = Fernet(key)
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode('utf-8'))
        decrypted_data = fernet.decrypt(encrypted_bytes)
        return decrypted_data.decode('utf-8')


def create_secure_config(encrypted_data: dict, password: str) -> dict:
    """Create secure configuration with encryption."""
    manager = EncryptionManager()
    encrypted_password = manager.encrypt_data(password)
    
    return {
        "encrypted_data": manager.encrypt_data(str(encrypted_data)),
        "password_hash": hash_password(password)[0],
        "salt": base64.b64encode(generate_salt()).decode('utf-8'),
        "version": "1.0"
    }


def load_secure_config(config_data: dict, password: str) -> dict:
    """Load and decrypt secure configuration."""
    manager = EncryptionManager()
    
    # Verify password
    if not verify_password(password, config_data["password_hash"]):
        raise ValueError("Invalid password")
    
    # Decrypt data
    encrypted_data = config_data["encrypted_data"]
    decrypted_data = manager.decrypt_data(encrypted_data)
    
    return eval(decrypted_data)  # Note: eval should be replaced with json.loads in production


# Optional dependency check for cryptography
try:
    import cryptography
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("Cryptography library not installed. Some features will be limited.")
