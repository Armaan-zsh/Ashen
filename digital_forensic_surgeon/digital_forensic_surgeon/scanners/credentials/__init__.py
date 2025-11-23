"""Credential scanner for Digital Forensic Surgeon."""

from __future__ import annotations

import re
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Any, Optional, Generator, Set
from datetime import datetime

from digital_forensic_surgeon.core.models import EvidenceItem, ForensicResult, Credential
from digital_forensic_surgeon.core.exceptions import ScannerError


class CredentialScanner:
    """Scanner for credentials and authentication artifacts."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Common password/credential patterns
        self.credential_patterns = [
            r'(?i)(password|passwd|pwd)\s*[=:]\s*["\']([^"\']+)["\']',
            r'(?i)(username|user|login)\s*[=:]\s*["\']([^"\']+)["\']',
            r'(?i)(api[_-]?key|apikey)\s*[=:]\s*["\']([^"\']+)["\']',
            r'(?i)(secret|token|auth)\s*[=:]\s*["\']([^"\']+)["\']',
            r'(?i)(access[_-]?key|secret[_-]?key)\s*[=:]\s*["\']([^"\']+)["\']',
        ]
        
        # File patterns that often contain credentials
        self.credential_files = [
            r'.*\.env$',
            r'.*\.ini$',
            r'.*\.cfg$',
            r'.*config\.json$',
            r'.*settings\.json$',
            r'.*credentials\.json$',
            r'.*\.key$',
            r'.*\.pem$',
            r'.*\.p12$',
            r'.*\.pfx$',
            r'.*\.keystore$',
            r'.*\.jks$',
        ]
    
    def scan_credential_files(self, base_path: Path) -> Generator[EvidenceItem, None, None]:
        """Scan for files likely containing credentials."""
        credential_regex = re.compile('|'.join(self.credential_files), re.IGNORECASE)
        
        try:
            for file_path in base_path.rglob('*'):
                if file_path.is_file() and credential_regex.match(file_path.name):
                    try:
                        content = self._safe_read_file(file_path)
                        
                        evidence = EvidenceItem(
                            type="credential_file",
                            source="credentials",
                            path=str(file_path),
                            content=content,
                            is_sensitive=True,
                            confidence=0.9
                        )
                        
                        yield evidence
                        
                    except Exception as e:
                        yield EvidenceItem(
                            type="credential_file_error",
                            source="credentials",
                            path=str(file_path),
                            content=f"Error reading credential file: {e}",
                            is_sensitive=True,
                            confidence=0.1
                        )
                        
        except Exception as e:
            yield EvidenceItem(
                type="credential_scan_error",
                source="credentials",
                path=str(base_path),
                content=f"Failed to scan for credential files: {e}",
                is_sensitive=False,
                confidence=0.1
            )
    
    def scan_content_for_credentials(self, content: str, source_path: str = "") -> Generator[EvidenceItem, None, None]:
        """Scan text content for credential patterns."""
        matches_found = 0
        
        for pattern in self.credential_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                matches_found += 1
                
                yield EvidenceItem(
                    type="credential_match",
                    source="credentials",
                    path=source_path,
                    content=f"Found credential: {match.group(0)}",
                    metadata={
                        "pattern": pattern,
                        "matched_text": match.group(0),
                        "key": match.group(1) if match.groups() else "",
                        "value": match.group(2) if len(match.groups()) >= 2 else ""
                    },
                    is_sensitive=True,
                    confidence=0.8
                )
        
        if matches_found > 0:
            yield EvidenceItem(
                type="credential_scan_summary",
                source="credentials",
                path=source_path,
                content=f"Found {matches_found} credential patterns",
                metadata={"matches": matches_found},
                is_sensitive=True,
                confidence=0.9
            )
    
    def scan_config_files(self, base_path: Path) -> Generator[EvidenceItem, None, None]:
        """Scan configuration files for embedded credentials."""
        config_extensions = {'.json', '.xml', '.ini', '.cfg', '.conf', '.yaml', '.yml'}
        
        try:
            for file_path in base_path.rglob('*'):
                if (file_path.is_file() and 
                    file_path.suffix.lower() in config_extensions):
                    
                    try:
                        content = self._safe_read_file(file_path)
                        
                        # Parse based on file type
                        if file_path.suffix.lower() == '.json':
                            credentials = self._scan_json_credentials(content, str(file_path))
                        elif file_path.suffix.lower() == '.xml':
                            credentials = self._scan_xml_credentials(content, str(file_path))
                        else:
                            credentials = self._scan_text_credentials(content, str(file_path))
                        
                        for cred_info in credentials:
                            yield EvidenceItem(
                                type="config_credential",
                                source="credentials",
                                path=str(file_path),
                                content=f"Found credential in config: {cred_info['type']}",
                                metadata=cred_info,
                                is_sensitive=True,
                                confidence=0.85
                            )
                            
                    except Exception as e:
                        yield EvidenceItem(
                            type="config_parse_error",
                            source="credentials",
                            path=str(file_path),
                            content=f"Error parsing config file: {e}",
                            is_sensitive=False,
                            confidence=0.1
                        )
                        
        except Exception as e:
            yield EvidenceItem(
                type="config_scan_error",
                source="credentials",
                path=str(base_path),
                content=f"Failed to scan config files: {e}",
                is_sensitive=False,
                confidence=0.1
            )
    
    def _safe_read_file(self, file_path: Path, max_size: int = 1024 * 1024) -> str:
        """Safely read file content with size limit."""
        if file_path.stat().st_size > max_size:
            return f"[Large file - {file_path.stat().st_size} bytes - not read for security]"
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            return f"[Error reading file: {e}]"
    
    def _scan_json_credentials(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Scan JSON content for credentials."""
        credentials = []
        
        try:
            data = json.loads(content)
            
            def scan_dict(obj, path=""):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        current_path = f"{path}.{key}" if path else key
                        
                        # Check for credential keys
                        if any(cred_key in key.lower() for cred_key in 
                               ['password', 'passwd', 'pwd', 'secret', 'token', 'key', 'api', 'auth']):
                            credentials.append({
                                "type": "json_credential",
                                "key": key,
                                "path": current_path,
                                "value": str(value)[:100] + "..." if len(str(value)) > 100 else str(value),
                                "file_path": file_path
                            })
                        
                        # Recursively scan nested structures
                        if isinstance(value, (dict, list)):
                            scan_dict(value, current_path)
                
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        if isinstance(item, (dict, list)):
                            scan_dict(item, f"{path}[{i}]")
            
            scan_dict(data)
            
        except json.JSONDecodeError:
            pass
        
        return credentials
    
    def _scan_xml_credentials(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Scan XML content for credentials."""
        credentials = []
        
        try:
            root = ET.fromstring(content)
            
            # Find elements with credential-related names
            for elem in root.iter():
                tag_name = elem.tag.lower()
                if any(cred_key in tag_name for cred_key in 
                       ['password', 'passwd', 'pwd', 'secret', 'token', 'key', 'api', 'auth']):
                    credentials.append({
                        "type": "xml_credential",
                        "tag": elem.tag,
                        "text": elem.text if elem.text else "",
                        "file_path": file_path
                    })
                    
        except ET.ParseError:
            pass
        
        return credentials
    
    def _scan_text_credentials(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Scan plain text content for credentials."""
        credentials = []
        
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            for pattern in self.credential_patterns:
                match = re.search(pattern, line)
                if match:
                    credentials.append({
                        "type": "text_credential",
                        "line_number": i + 1,
                        "line": line.strip(),
                        "matched_pattern": pattern,
                        "file_path": file_path
                    })
        
        return credentials
    
    def extract_discovered_credentials(self, evidence_items: List[EvidenceItem]) -> List[Credential]:
        """Extract credential objects from evidence items."""
        credentials = []
        
        for evidence in evidence_items:
            if evidence.type in ["credential_match", "config_credential", "credential_file"]:
                try:
                    metadata = evidence.metadata or {}
                    
                    # Create Credential object
                    credential = Credential(
                        username=metadata.get("username", metadata.get("user", "")),
                        password_hash=None,  # Would need to extract/format
                        service_name=metadata.get("service", ""),
                        domain=metadata.get("domain", ""),
                        credential_type=self._determine_credential_type(evidence),
                        confidence=evidence.confidence
                    )
                    
                    credentials.append(credential)
                    
                except Exception as e:
                    # Skip malformed credentials
                    continue
        
        return credentials
    
    def _determine_credential_type(self, evidence: EvidenceItem) -> str:
        """Determine credential type from evidence."""
        if "password" in evidence.path.lower() or "passwd" in evidence.path.lower():
            return "password"
        elif "api" in evidence.path.lower():
            return "api_key"
        elif "token" in evidence.path.lower():
            return "token"
        elif "cert" in evidence.path.lower() or "pem" in evidence.path.lower():
            return "certificate"
        else:
            return "credential"


def scan_credentials_forensic(base_path: Path = None) -> ForensicResult:
    """Perform credential forensic scan."""
    if base_path is None:
        base_path = Path.home()
    
    scanner = CredentialScanner()
    result = ForensicResult(scan_type="credentials")
    
    start_time = datetime.now()
    
    try:
        # Scan for credential files
        for evidence in scanner.scan_credential_files(base_path):
            result.add_evidence(evidence)
        
        # Scan configuration files
        for evidence in scanner.scan_config_files(base_path):
            result.add_evidence(evidence)
        
        # Extract credentials from discovered evidence
        credentials = scanner.extract_discovered_credentials(result.evidence_items)
        for credential in credentials:
            result.add_credential(credential)
        
        result.finalize()
        
    except Exception as e:
        result.add_error(f"Credential scan failed: {e}")
        result.finalize()
    
    return result
