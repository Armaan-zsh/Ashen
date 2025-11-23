"""Helper utilities for Digital Forensic Surgeon."""

from __future__ import annotations

import os
import re
import json
import logging
import platform
import hashlib
import secrets
import string
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
from urllib.parse import urlparse
import tempfile
import shutil


def setup_logging(level: str = "INFO", log_file: Optional[str] = None, 
                 enable_console: bool = True) -> logging.Logger:
    """Setup logging configuration."""
    
    # Create logger
    logger = logging.getLogger("digital_forensic_surgeon")
    logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    if enable_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # File handler
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def sanitize_path(path: Union[str, Path]) -> Path:
    """Sanitize file path for safe file operations."""
    path = Path(path)
    
    # Resolve to absolute path
    try:
        path = path.resolve(strict=False)
    except (OSError, RuntimeError):
        # Fallback to safe path
        safe_path = Path.home() / "sanitized" / str(secrets.token_hex(8))
        return safe_path
    
    # Remove null bytes and control characters
    path_str = str(path)
    path_str = re.sub(r'[\x00-\x1f\x7f]', '', path_str)
    
    return Path(path_str)


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB", "PB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format."""
    if seconds < 1:
        return f"{seconds*1000:.0f} ms"
    elif seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{int(minutes)}m {remaining_seconds:.0f}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{int(hours)}h {int(minutes)}m"


def safe_filename(filename: str, max_length: int = 255) -> str:
    """Create safe filename by removing invalid characters."""
    # Remove invalid characters
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing dots and spaces
    safe_name = safe_name.strip('. ')
    
    # Ensure not empty
    if not safe_name:
        safe_name = f"file_{secrets.token_hex(4)}"
    
    # Truncate if too long
    if len(safe_name) > max_length:
        name, ext = os.path.splitext(safe_name)
        max_name_length = max_length - len(ext)
        safe_name = name[:max_name_length] + ext
    
    return safe_name


def validate_email(email: str) -> bool:
    """Validate email address format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_url(url: str) -> bool:
    """Validate URL format."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def extract_domain(url: str) -> str:
    """Extracts the domain from a URL."""
    try:
        return urlparse(url).netloc
    except Exception:
        return ""


def hash_data(data: str, algorithm: str = "sha256") -> str:
    """Hash data using specified algorithm."""
    hasher = hashlib.new(algorithm)
    hasher.update(data.encode('utf-8'))
    return hasher.hexdigest()


def encrypt_data(data: str, key: bytes) -> str:
    """Encrypt data using simple XOR cipher (for demonstration)."""
    # This is a simplified example - in production, use proper encryption
    encrypted = []
    for i, char in enumerate(data):
        encrypted_char = chr(ord(char) ^ key[i % len(key)])
        encrypted.append(encrypted_char)
    return ''.join(encrypted)


def decrypt_data(encrypted_data: str, key: bytes) -> str:
    """Decrypt data using simple XOR cipher (for demonstration)."""
    # This is a simplified example - in production, use proper encryption
    decrypted = []
    for i, char in enumerate(encrypted_data):
        decrypted_char = chr(ord(char) ^ key[i % len(key)])
        decrypted.append(decrypted_char)
    return ''.join(decrypted)


def load_json_safe(file_path: Union[str, Path]) -> Optional[Dict[str, Any]]:
    """Safely load JSON file with error handling."""
    try:
        file_path = Path(file_path)
        if not file_path.exists():
            return None
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError, PermissionError, OSError):
        return None


def save_json_safe(data: Dict[str, Any], file_path: Union[str, Path], 
                  indent: int = 2) -> bool:
    """Safely save JSON file with error handling."""
    try:
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)
        return True
    except (TypeError, OSError, PermissionError):
        return False


def ensure_directory(path: Union[str, Path]) -> Path:
    """Ensure directory exists, create if necessary."""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_platform_info() -> Dict[str, Any]:
    """Get detailed platform information."""
    return {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "architecture": platform.architecture(),
        "python_version": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "hostname": platform.node(),
        "cpu_count": os.cpu_count(),
        "machine_id": secrets.token_hex(16),
    }


def generate_random_string(length: int = 32, 
                          include_symbols: bool = False) -> str:
    """Generate cryptographically secure random string."""
    characters = string.ascii_letters + string.digits
    if include_symbols:
        characters += string.punctuation
    
    return ''.join(secrets.choice(characters) for _ in range(length))


def create_temp_directory(prefix: str = "forensic_") -> Path:
    """Create temporary directory for forensic operations."""
    temp_dir = Path(tempfile.mkdtemp(prefix=prefix))
    return temp_dir


def cleanup_temp_directory(temp_dir: Path) -> None:
    """Clean up temporary directory."""
    try:
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
    except OSError:
        pass


def is_admin() -> bool:
    """Check if running with administrator privileges."""
    try:
        if platform.system() == "Windows":
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin()
        else:
            return os.getuid() == 0
    except Exception:
        return False


def format_timestamp(timestamp: Union[datetime, float, str], 
                    format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format timestamp to human-readable string."""
    if isinstance(timestamp, str):
        try:
            timestamp = datetime.fromisoformat(timestamp)
        except ValueError:
            return timestamp
    
    if isinstance(timestamp, float):
        timestamp = datetime.fromtimestamp(timestamp)
    
    return timestamp.strftime(format_str)


def get_file_hash(file_path: Union[str, Path], 
                 algorithm: str = "sha256") -> Optional[str]:
    """Calculate file hash using specified algorithm."""
    try:
        hasher = hashlib.new(algorithm)
        file_path = Path(file_path)
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        
        return hasher.hexdigest()
    except (FileNotFoundError, PermissionError, OSError):
        return None


def calculate_directory_size(directory: Union[str, Path]) -> int:
    """Calculate total size of directory."""
    total_size = 0
    directory = Path(directory)
    
    try:
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(filepath)
                except (OSError, FileNotFoundError):
                    continue
    except OSError:
        pass
    
    return total_size


def find_files_by_extension(directory: Union[str, Path], 
                           extensions: List[str]) -> List[Path]:
    """Find all files with specified extensions in directory."""
    directory = Path(directory)
    found_files = []
    
    for ext in extensions:
        if not ext.startswith('.'):
            ext = '.' + ext
        
        found_files.extend(directory.rglob(f'*{ext}'))
    
    return found_files


def get_file_info(file_path: Union[str, Path]) -> Dict[str, Any]:
    """Get comprehensive file information."""
    file_path = Path(file_path)
    
    if not file_path.exists():
        return {}
    
    try:
        stat = file_path.stat()
        
        return {
            "path": str(file_path),
            "name": file_path.name,
            "stem": file_path.stem,
            "suffix": file_path.suffix,
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime),
            "created": datetime.fromtimestamp(stat.st_ctime) if hasattr(stat, 'st_ctime') else None,
            "accessed": datetime.fromtimestamp(stat.st_atime) if hasattr(stat, 'st_atime') else None,
            "is_file": file_path.is_file(),
            "is_dir": file_path.is_dir(),
            "is_symlink": file_path.is_symlink(),
            "permissions": oct(stat.st_mode)[-3:],
            "owner": stat.st_uid,
            "group": stat.st_gid,
        }
    except OSError:
        return {}


class FileProgressTracker:
    """Track progress for file operations."""
    
    def __init__(self, total_files: int):
        self.total_files = total_files
        self.processed_files = 0
        self.start_time = datetime.now()
    
    def update(self, increment: int = 1) -> None:
        """Update processed file count."""
        self.processed_files += increment
    
    def get_progress(self) -> Dict[str, Any]:
        """Get current progress information."""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        progress_percent = (self.processed_files / self.total_files) * 100 if self.total_files > 0 else 0
        
        if self.processed_files > 0:
            avg_time_per_file = elapsed / self.processed_files
            remaining_files = self.total_files - self.processed_files
            estimated_remaining = remaining_files * avg_time_per_file
        else:
            estimated_remaining = 0
        
        return {
            "processed": self.processed_files,
            "total": self.total_files,
            "progress_percent": progress_percent,
            "elapsed_seconds": elapsed,
            "estimated_remaining_seconds": estimated_remaining,
            "files_per_second": self.processed_files / elapsed if elapsed > 0 else 0,
        }
