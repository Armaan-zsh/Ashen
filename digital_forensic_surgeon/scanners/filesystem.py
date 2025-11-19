"""Filesystem scanner for Digital Forensic Surgeon."""

from __future__ import annotations

import os
import sys
import re
import json
import time
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional, Generator, Iterator
from datetime import datetime
from dataclasses import dataclass

from digital_forensic_surgeon.core.models import EvidenceItem, ForensicResult, Account
from digital_forensic_surgeon.core.exceptions import ScannerError
from digital_forensic_surgeon.core.config import get_config


@dataclass
class FileMetadata:
    """Represents file metadata."""
    path: str
    name: str
    size: int
    modified_time: datetime
    created_time: datetime
    extension: str
    mime_type: str | None = None
    hash_sha256: str = ""
    permissions: str = ""
    owner: str = ""
    group: str = ""
    is_hidden: bool = False
    is_system: bool = False


class FileSystemScanner:
    """Perform filesystem forensic analysis."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or get_config()
        self.max_file_size = 100 * 1024 * 1024  # 100MB
        self.ignore_patterns = [
            r'.*\.tmp$',
            r'.*\.temp$',
            r'.*\.cache$',
            r'.*/node_modules/.*',
            r'.*/venv/.*',
            r'.*/env/.*',
            r'.*/__pycache__/.*',
            r'.*/.*\.log$',
            r'.*/Thumbs\.db$',
            r'.*/desktop\.ini$',
        ]
        
        self.sensitive_extensions = [
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
            '.txt', '.rtf', '.odt', '.ods', '.odp',
            '.csv', '.json', '.xml', '.yaml', '.yml',
            '.sql', '.db', '.sqlite', '.mdb',
            '.key', '.p12', '.pfx', '.pem', '.crt', '.cer',
            '.zip', '.rar', '.7z', '.tar', '.gz',
            '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff',
            '.mp3', '.mp4', '.avi', '.mov', '.wmv',
        ]
    
    def scan_directory(self, directory: str | Path, 
                      recursive: bool = True,
                      max_depth: int = 10) -> Generator[EvidenceItem, None, None]:
        """Scan directory for forensic evidence.
        
        Args:
            directory: Directory to scan
            recursive: Whether to scan subdirectories
            max_depth: Maximum recursion depth
            
        Yields:
            EvidenceItem objects for discovered files
        """
        directory = Path(directory)
        
        if not directory.exists():
            raise ScannerError(f"Directory does not exist: {directory}")
        
        if not directory.is_dir():
            raise ScannerError(f"Path is not a directory: {directory}")
        
        current_depth = 0
        
        def scan_path(path: Path, depth: int) -> Iterator[EvidenceItem]:
            """Recursively scan a path."""
            nonlocal current_depth
            
            if depth > max_depth:
                return
            
            try:
                for item in path.iterdir():
                    # Check if we should skip this item
                    if self._should_skip_path(item):
                        continue
                    
                    if item.is_file():
                        # Process file
                        evidence = self._process_file(item)
                        if evidence:
                            yield evidence
                    
                    elif item.is_dir() and recursive:
                        # Process directory recursively
                        current_depth = depth
                        yield from scan_path(item, depth + 1)
                        
            except (PermissionError, OSError) as e:
                # Log access errors but don't stop scanning
                error_evidence = EvidenceItem(
                    type="access_error",
                    source="filesystem",
                    path=str(item),
                    content=f"Access error: {e}",
                    metadata={"error_type": str(type(e).__name__)}
                )
                yield error_evidence
        
        yield from scan_path(directory, 0)
    
    def _should_skip_path(self, path: Path) -> bool:
        """Check if a path should be skipped."""
        # Check ignore patterns
        for pattern in self.ignore_patterns:
            if re.match(pattern, str(path), re.IGNORECASE):
                return True
        
        # Check if it's a system/hidden file
        if path.name.startswith('.'):
            return True
        
        # Check if parent directories should be skipped
        parts = path.parts
        skip_dirs = {'.git', '.svn', '.hg', 'node_modules', '__pycache__', '.tox', '.pytest_cache'}
        if any(part in skip_dirs for part in parts):
            return True
        
        return False
    
    def _process_file(self, file_path: Path) -> Optional[EvidenceItem]:
        """Process a single file."""
        try:
            # Get file stats
            stat = file_path.stat()
            
            # Skip very large files
            if stat.st_size > self.max_file_size:
                return None
            
            # Extract metadata
            metadata = self._extract_file_metadata(file_path, stat)
            
            # Determine if file contains sensitive data
            is_sensitive = self._is_sensitive_file(file_path, metadata)
            
            # Create evidence item
            evidence = EvidenceItem(
                type="file",
                source="filesystem",
                path=str(file_path),
                content=self._extract_relevant_content(file_path, metadata),
                metadata=metadata,
                is_sensitive=is_sensitive,
                confidence=self._calculate_confidence(file_path, metadata)
            )
            
            return evidence
            
        except (PermissionError, OSError, UnicodeDecodeError) as e:
            # Return error evidence instead of failing
            return EvidenceItem(
                type="file_error",
                source="filesystem", 
                path=str(file_path),
                content=f"Error processing file: {e}",
                metadata={"error_type": str(type(e).__name__)},
                is_sensitive=False,
                confidence=0.1
            )
    
    def _extract_file_metadata(self, file_path: Path, stat) -> Dict[str, Any]:
        """Extract comprehensive file metadata."""
        metadata = {
            "size": stat.st_size,
            "modified_time": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "created_time": datetime.fromtimestamp(stat.st_ctime).isoformat() if hasattr(stat, 'st_ctime') else None,
            "extension": file_path.suffix.lower(),
            "permissions": oct(stat.st_mode)[-3:],
            "inode": stat.st_ino,
            "device": stat.st_dev,
            "hard_links": stat.st_nlink,
        }
        
        # Calculate hash
        try:
            metadata["hash_sha256"] = self._calculate_file_hash(file_path)
        except (PermissionError, OSError):
            metadata["hash_sha256"] = None
        
        # Get owner/group (Unix systems)
        try:
            import pwd
            import grp
            metadata["owner"] = pwd.getpwuid(stat.st_uid).pw_name
            metadata["group"] = grp.getgrgid(stat.st_gid).gr_name
        except (ImportError, KeyError):
            metadata["owner"] = str(stat.st_uid)
            metadata["group"] = str(stat.st_gid)
        
        # Detect MIME type
        metadata["mime_type"] = self._detect_mime_type(file_path)
        
        # Security flags
        metadata["is_hidden"] = file_path.name.startswith('.')
        metadata["is_executable"] = os.access(file_path, os.X_OK)
        
        # Extract EXIF GPS data for images
        if metadata["extension"].lower() in ['.jpg', '.jpeg', '.png', '.heic', '.tiff', '.tif']:
            try:
                exif_data = self._extract_exif_data(file_path)
                if exif_data:
                    metadata.update(exif_data)
            except Exception as e:
                metadata["exif_error"] = str(e)
        
        return metadata
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file."""
        sha256 = hashlib.sha256()
        
        try:
            with open(file_path, 'rb') as f:
                # Read file in chunks to handle large files
                for chunk in iter(lambda: f.read(8192), b""):
                    sha256.update(chunk)
            return sha256.hexdigest()
        except (PermissionError, OSError):
            return ""
    
    def _extract_exif_data(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Extract GPS and metadata from image EXIF data."""
        try:
            # Lazy import to avoid dependency issues
            from PIL import Image
            from PIL.ExifTags import TAGS, GPSTAGS
            
            with Image.open(file_path) as img:
                exif = img.getexif()
                if not exif:
                    return None
                
                exif_data = {}
                
                # Process EXIF tags
                for tag_id, value in exif.items():
                    tag = TAGS.get(tag_id, tag_id)
                    
                    # Handle GPS data specially
                    if tag == "GPSInfo":
                        gps_data = {}
                        for gps_tag_id, gps_value in value.items():
                            gps_tag = GPSTAGS.get(gps_tag_id, gps_tag_id)
                            gps_data[gps_tag] = gps_value
                        
                        # Convert GPS data to coordinates
                        if gps_data:
                            coords = self._gps_to_coordinates(gps_data)
                            if coords:
                                exif_data["gps_latitude"] = coords[0]
                                exif_data["gps_longitude"] = coords[1]
                                exif_data["gps_coordinates"] = f"{coords[0]:.6f}, {coords[1]:.6f}"
                                exif_data["has_gps"] = True
                    
                    # Store other useful metadata
                    elif tag in ["DateTime", "DateTimeOriginal", "DateTimeDigitized"]:
                        try:
                            # Try to parse EXIF date format
                            exif_data[tag.lower()] = datetime.strptime(str(value), "%Y:%m:%d %H:%M:%S")
                        except (ValueError, TypeError):
                            exif_data[tag.lower()] = str(value)
                    elif isinstance(value, str) and len(value) < 200:  # Avoid huge values
                        exif_data[tag.lower()] = value
                
                # Add image dimensions
                exif_data["image_width"] = img.width
                exif_data["image_height"] = img.height
                exif_data["image_format"] = img.format
                
                return exif_data if exif_data else None
                
        except ImportError:
            # Pillow not installed, return None
            return None
        except Exception as e:
            # Return None for any other errors to avoid crashing
            return None
    
    def _gps_to_coordinates(self, gps_data: Dict[str, Any]) -> Optional[tuple[float, float]]:
        """Convert GPS data to decimal coordinates."""
        try:
            def _convert_to_degrees(value):
                """Convert GPS coordinate format to degrees."""
                d, m, s = value
                return float(d) + float(m) / 60 + float(s) / 3600
            
            # Handle different GPS coordinate formats
            if "GPSLatitude" in gps_data and "GPSLongitude" in gps_data:
                lat = _convert_to_degrees(gps_data["GPSLatitude"])
                lon = _convert_to_degrees(gps_data["GPSLongitude"])
                
                # Apply hemisphere correction
                if gps_data.get("GPSLatitudeRef") == "S":
                    lat = -lat
                if gps_data.get("GPSLongitudeRef") == "W":
                    lon = -lon
                
                return (lat, lon)
            
            return None
            
        except Exception:
            return None
    
    def _detect_mime_type(self, file_path: Path) -> str:
        """Detect MIME type of file."""
        # Use file extension as primary method
        extension_mime_map = {
            '.txt': 'text/plain',
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xls': 'application/vnd.ms-excel',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.ppt': 'application/vnd.ms-powerpoint',
            '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            '.json': 'application/json',
            '.xml': 'application/xml',
            '.html': 'text/html',
            '.htm': 'text/html',
            '.css': 'text/css',
            '.js': 'text/javascript',
            '.py': 'text/x-python',
            '.sql': 'application/sql',
            '.csv': 'text/csv',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.tiff': 'image/tiff',
            '.mp3': 'audio/mpeg',
            '.mp4': 'video/mp4',
            '.avi': 'video/x-msvideo',
            '.zip': 'application/zip',
            '.tar': 'application/x-tar',
            '.gz': 'application/gzip',
        }
        
        return extension_mime_map.get(file_path.suffix.lower(), 'application/octet-stream')
    
    def _is_sensitive_file(self, file_path: Path, metadata: Dict[str, Any]) -> bool:
        """Determine if file likely contains sensitive information."""
        # Check extension
        if metadata.get("extension") in self.sensitive_extensions:
            return True
        
        # Check file name patterns
        sensitive_names = [
            'password', 'passwd', 'pwd', 'secret', 'key', 'token',
            'credential', 'auth', 'login', 'account', 'finance',
            'bank', 'credit', 'card', 'ssn', 'social_security',
            'medical', 'health', 'insurance', 'tax', 'income',
            'resume', 'cv', 'passport', 'driver_license'
        ]
        
        file_name_lower = file_path.name.lower()
        if any(name in file_name_lower for name in sensitive_names):
            return True
        
        # Check location patterns
        path_lower = str(file_path).lower()
        sensitive_locations = [
            'desktop', 'downloads', 'documents', ' Pictures', 'photos',
            'browser', 'chrome', 'firefox', 'edge', 'safari',
            'wallet', 'bitcoin', 'crypto', 'mining',
        ]
        
        if any(location in path_lower for location in sensitive_locations):
            return True
        
        return False
    
    def _extract_relevant_content(self, file_path: Path, metadata: Dict[str, Any]) -> str:
        """Extract relevant content from file for forensic analysis."""
        try:
            file_size = metadata.get("size", 0)
            
            # Only extract content from small files to avoid memory issues
            if file_size > 1024 * 1024:  # 1MB
                return f"[Large file - {file_size} bytes - content not extracted for forensic analysis]"
            
            # Try to read as text first
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read(8192)  # Read first 8KB
                    
                    # Clean up content
                    content = content.replace('\x00', '')  # Remove null bytes
                    content = content.replace('\r\n', '\n')  # Normalize line endings
                    
                    # Truncate if too long
                    if len(content) > 4096:
                        content = content[:4096] + "\n...[truncated]"
                    
                    return content
                    
            except UnicodeDecodeError:
                # File is binary - extract basic info
                return f"[Binary file - {metadata.get('mime_type', 'unknown')} - {file_size} bytes]"
                
        except (PermissionError, OSError) as e:
            return f"[Error reading file: {e}]"
    
    def _calculate_confidence(self, file_path: Path, metadata: Dict[str, Any]) -> float:
        """Calculate confidence score for file analysis."""
        confidence = 1.0
        
        # Lower confidence for files we couldn't read
        if not metadata.get("hash_sha256"):
            confidence -= 0.3
        
        # Lower confidence for very small files
        if metadata.get("size", 0) < 100:
            confidence -= 0.2
        
        # Higher confidence for sensitive files
        if metadata.get("is_sensitive", False):
            confidence += 0.2
        
        # Lower confidence for system files
        if metadata.get("is_system", False):
            confidence -= 0.1
        
        return max(0.0, min(1.0, confidence))
    
    def scan_user_directories(self) -> Generator[EvidenceItem, None, None]:
        """Scan common user directories."""
        home_dir = Path.home()
        
        # Common user directories to scan
        directories = [
            home_dir / "Documents",
            home_dir / "Desktop", 
            home_dir / "Downloads",
            home_dir / "Pictures",
            home_dir / "Music",
            home_dir / "Videos",
            home_dir / ".ssh",
            home_dir / ".aws",
            home_dir / ".docker",
        ]
        
        for directory in directories:
            if directory.exists():
                try:
                    yield from self.scan_directory(directory, recursive=True)
                except Exception as e:
                    yield EvidenceItem(
                        type="scan_error",
                        source="filesystem",
                        path=str(directory),
                        content=f"Failed to scan directory: {e}",
                        is_sensitive=False,
                        confidence=0.1
                    )
    
    def search_files_by_pattern(self, pattern: str, 
                              base_path: str | Path = None) -> Generator[EvidenceItem, None, None]:
        """Search for files matching a regex pattern."""
        if base_path is None:
            base_path = Path.home()
        else:
            base_path = Path(base_path)
        
        try:
            regex = re.compile(pattern, re.IGNORECASE)
            
            for item in self.scan_directory(base_path, recursive=True):
                if item.path and regex.search(item.path):
                    yield item
                    
        except re.error as e:
            raise ScannerError(f"Invalid regex pattern: {e}")
    
    def find_password_files(self) -> Generator[EvidenceItem, None, None]:
        """Find files likely containing passwords or credentials."""
        patterns = [
            r'.*[Pp]assword.*',
            r'.*[Pp]asswd.*', 
            r'.*[Pp]wd.*',
            r'.*[Kk]ey.*',
            r'.*[Ss]ecret.*',
            r'.*[Cc]redential.*',
            r'.*\.key$',
            r'.*\.p12$',
            r'.*\.pfx$',
            r'.*\.pem$',
            r'.*\.csv$',
            r'.*\.xlsx?$',
            r'.*\.json$',
        ]
        
        for pattern in patterns:
            yield from self.search_files_by_pattern(pattern)
    
    def analyze_disk_usage(self, directory: str | Path) -> Dict[str, Any]:
        """Analyze disk usage by file type."""
        directory = Path(directory)
        usage_by_type = {}
        total_files = 0
        total_size = 0
        
        for evidence in self.scan_directory(directory):
            if evidence.type == "file":
                ext = evidence.metadata.get("extension", "unknown")
                size = evidence.metadata.get("size", 0)
                
                if ext not in usage_by_type:
                    usage_by_type[ext] = {"count": 0, "size": 0}
                
                usage_by_type[ext]["count"] += 1
                usage_by_type[ext]["size"] += size
                
                total_files += 1
                total_size += size
        
        return {
            "total_files": total_files,
            "total_size": total_size,
            "by_extension": usage_by_type
        }


def scan_filesystem_forensic(
    paths: List[str] = None,
    search_patterns: List[str] = None,
    find_credentials: bool = True
) -> ForensicResult:
    """Convenience function to perform complete filesystem forensic scan."""
    if paths is None:
        paths = [str(Path.home())]
    
    scanner = FileSystemScanner()
    result = ForensicResult(scan_type="filesystem")
    
    start_time = datetime.now()
    
    try:
        for path in paths:
            # Scan directory
            for evidence in scanner.scan_directory(path):
                result.add_evidence(evidence)
            
            # Find credentials if requested
            if find_credentials:
                for evidence in scanner.find_password_files():
                    result.add_evidence(evidence)
            
            # Search patterns if provided
            if search_patterns:
                for pattern in search_patterns:
                    for evidence in scanner.search_files_by_pattern(pattern, path):
                        result.add_evidence(evidence)
        
        # Analyze discovered accounts (simplified)
        for evidence in result.evidence_items:
            if evidence.is_sensitive and evidence.type == "file":
                # Simple heuristic for account detection
                if "email" in evidence.content.lower() or "@" in evidence.content:
                    account = Account(
                        service_name="File-based account",
                        domain="unknown",
                        username=evidence.content.split("@")[0] if "@" in evidence.content else "unknown",
                        email=evidence.content.split("@")[0] if "@" in evidence.content else "",
                        risk_score=4.0,
                        data_classification="sensitive"
                    )
                    result.add_account(account)
        
        result.finalize()
        
    except Exception as e:
        result.add_error(f"Filesystem scan failed: {e}")
        result.finalize()
    
    return result
