"""Core data models for Digital Forensic Surgeon."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from pathlib import Path
from enum import Enum
import uuid
import hashlib


class ScannerType(Enum):
    """Enumeration of different scanner types."""
    FILESYSTEM = "filesystem"
    BROWSER = "browser"
    NETWORK = "network"
    CREDENTIAL = "credential"
    OSINT = "osint"
    PACKET_ANALYZER = "packet_analyzer"
    CONTENT_CLASSIFIER = "content_classifier"
    DESTINATION_INTELLIGENCE = "destination_intelligence"
    APPLICATION_MONITOR = "application_monitor"
    SECURITY_AUDITOR = "security_auditor"
    BEHAVIORAL_INTELLIGENCE = "behavioral_intelligence"


@dataclass
class Credential:
    """Represents a discovered credential."""
    
    username: str
    password_hash: str | None = None  # Never store plain text
    password_plain: str | None = None  # Only if user explicitly provides
    salt: str | None = None
    algorithm: str = "scrypt"  # scrypt, bcrypt, pbkdf2, argon2
    service_name: str = ""
    domain: str = ""
    credential_type: str = "password"  # password, api_key, token, certificate
    confidence: float = 1.0  # 0.0 to 1.0
    last_modified: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self) -> None:
        """Validate and secure credential data."""
        if self.password_plain and not self.password_hash:
            self.password_hash = self._hash_password(self.password_plain)
            self.password_plain = None  # Clear plain text immediately
    
    def _hash_password(self, password: str) -> str:
        """Hash password using scrypt."""
        salt = os.urandom(16)
        hashed = hashlib.scrypt(
            password.encode(), 
            salt=salt, 
            n=16384, 
            r=8, 
            p=1
        )
        return f"scrypt${salt.hex()}${hashed.hex()}"
    
    @property
    def is_hashed(self) -> bool:
        """Check if password is properly hashed."""
        return self.password_hash is not None and self.password_plain is None
    
    def verify_password(self, password: str) -> bool:
        """Verify password against hash (if available)."""
        if not self.password_hash:
            return False
            
        try:
            algorithm, salt_hex, hash_hex = self.password_hash.split('$')
            if algorithm != self.algorithm:
                return False
                
            salt = bytes.fromhex(salt_hex)
            expected_hash = hashlib.scrypt(
                password.encode(),
                salt=salt,
                n=16384,
                r=8, 
                p=1
            )
            
            return expected_hash.hex() == hash_hex
        except Exception:
            return False


@dataclass 
class Account:
    """Represents a discovered online account."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    service_name: str = ""
    domain: str = ""
    username: str = ""
    email: str = ""
    account_type: str = "user"  # user, admin, business, organization
    registration_date: Optional[datetime] = None
    last_login: Optional[datetime] = None
    is_verified: bool = False
    risk_score: float = 0.0  # 0.0 to 10.0
    data_classification: str = "personal"  # personal, financial, medical, sensitive
    known_breaches: List[str] = field(default_factory=list)
    deletion_status: str = "unknown"  # unknown, pending, completed, failed
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    
    def to_credential(self) -> Credential:
        """Convert to credential object."""
        return Credential(
            username=self.username or self.email,
            service_name=self.service_name,
            domain=self.domain,
            credential_type="account"
        )


@dataclass
class Service:
    """Represents an online service/platform."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    domain: str = ""
    category: str = ""  # social, email, cloud, shopping, etc.
    deletion_url: str = ""
    privacy_policy_url: str = ""
    terms_url: str = ""
    contact_email: str = ""
    gdpr_template: str = ""
    difficulty: int = 1  # 1-5 (5 = very difficult)
    time_required: str = ""  # "2 minutes", "24 hours", etc.
    requires_identity_verification: bool = False
    requires_phone_verification: bool = False
    breach_count: int = 0
    privacy_rating: int = 3  # 1-5 (1 = worst)
    alternative_services: List[str] = field(default_factory=list)
    legal_basis: str = ""  # GDPR article cited for deletion rights
    api_available: bool = False
    requires_payment_history_check: bool = False
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """Validate service data."""
        if not self.domain and self.name:
            # Attempt to extract domain from common service names
            self.domain = self._extract_domain_from_name()
    
    def _extract_domain_from_name(self) -> str:
        """Extract domain from service name."""
        name_to_domain = {
            "google": "google.com",
            "facebook": "facebook.com", 
            "twitter": "twitter.com",
            "linkedin": "linkedin.com",
            "instagram": "instagram.com",
            "amazon": "amazon.com",
            "netflix": "netflix.com",
            "spotify": "spotify.com",
            "microsoft": "microsoft.com",
            "apple": "apple.com",
        }
        
        return name_to_domain.get(self.name.lower(), self.name.lower().replace(" ", "") + ".com")


@dataclass
class EvidenceItem:
    """Represents a piece of forensic evidence."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    type: str = ""  # file, registry, cookie, session, network, etc.
    source: str = ""  # filesystem, browser, network, etc.
    path: str = ""  # file path, registry key, URL, etc.
    content: str = ""  # extracted data
    hash: str = ""  # SHA-256 hash for integrity
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    is_sensitive: bool = False
    confidence: float = 1.0
    
    def __post_init__(self) -> None:
        """Calculate hash if not provided."""
        if not self.hash:
            self.hash = hashlib.sha256(self.content.encode()).hexdigest()


@dataclass
class RiskAssessment:
    """Represents a risk assessment result."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    assessment_type: str = ""  # overall, service, credential, etc.
    entity_id: str = ""  # ID of assessed entity
    risk_score: float = 0.0  # 0.0 to 10.0
    risk_level: str = "low"  # low, medium, high, critical
    factors: Dict[str, float] = field(default_factory=dict)  # risk factor breakdown
    recommendations: List[str] = field(default_factory=list)
    mitigation_steps: List[str] = field(default_factory=list)
    assessment_date: datetime = field(default_factory=datetime.now)
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """Calculate risk level based on score."""
        if self.risk_score >= 8.0:
            self.risk_level = "critical"
        elif self.risk_score >= 6.0:
            self.risk_level = "high"
        elif self.risk_score >= 3.0:
            self.risk_level = "medium"
        else:
            self.risk_level = "low"


@dataclass
class SystemInfo:
    """Represents system information."""
    
    platform: str = ""
    architecture: str = ""
    hostname: str = ""
    username: str = ""
    home_directory: str = ""
    temp_directory: str = ""
    python_version: str = ""
    installed_packages: List[str] = field(default_factory=list)
    network_interfaces: List[Dict[str, Any]] = field(default_factory=list)
    disk_usage: Dict[str, float] = field(default_factory=dict)
    memory_info: Dict[str, Any] = field(default_factory=dict)
    running_processes: List[Dict[str, Any]] = field(default_factory=list)
    browser_profiles: List[str] = field(default_factory=list)
    
    def __post_init__(self) -> None:
        """Populate system information."""
        import platform
        import os
        import sys
        
        self.platform = platform.system()
        self.architecture = platform.machine()
        self.hostname = platform.node()
        self.username = os.getenv('USER', os.getenv('USERNAME', 'unknown'))
        self.home_directory = str(Path.home())
        self.temp_directory = tempfile.gettempdir()
        self.python_version = sys.version


@dataclass
class ForensicResult:
    """Represents a complete forensic investigation result."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    scan_type: str = "full"  # full, quick, targeted
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    duration: Optional[float] = None  # seconds
    evidence_items: List[EvidenceItem] = field(default_factory=list)
    discovered_accounts: List[Account] = field(default_factory=list)
    discovered_credentials: List[Credential] = field(default_factory=list)
    risk_assessments: List[RiskAssessment] = field(default_factory=list)
    system_info: Optional[SystemInfo] = None
    reports_generated: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    success: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_evidence(self, evidence: EvidenceItem) -> None:
        """Add evidence item to results."""
        self.evidence_items.append(evidence)
    
    def add_account(self, account: Account) -> None:
        """Add discovered account."""
        self.discovered_accounts.append(account)
    
    def add_credential(self, credential: Credential) -> None:
        """Add discovered credential."""
        self.discovered_credentials.append(credential)
    
    def add_risk_assessment(self, assessment: RiskAssessment) -> None:
        """Add risk assessment."""
        self.risk_assessments.append(assessment)
    
    def add_error(self, error: str) -> None:
        """Add error message."""
        self.errors.append(error)
        self.success = False
    
    def add_warning(self, warning: str) -> None:
        """Add warning message."""
        self.warnings.append(warning)
    
    def finalize(self) -> None:
        """Finalize the forensic result."""
        self.end_time = datetime.now()
        if self.start_time:
            self.duration = (self.end_time - self.start_time).total_seconds()
    
    @property
    def total_evidence_items(self) -> int:
        """Get total number of evidence items."""
        return len(self.evidence_items)
    
    @property
    def total_accounts(self) -> int:
        """Get total number of discovered accounts."""
        return len(self.discovered_accounts)
    
    @property
    def total_credentials(self) -> int:
        """Get total number of discovered credentials."""
        return len(self.discovered_credentials)
    
    @property
    def average_risk_score(self) -> float:
        """Get average risk score across all assessments."""
        if not self.risk_assessments:
            return 0.0
        return sum(r.risk_score for r in self.risk_assessments) / len(self.risk_assessments)
    
    def get_high_risk_items(self, threshold: float = 6.0) -> List[RiskAssessment]:
        """Get high-risk items above threshold."""
        return [r for r in self.risk_assessments if r.risk_score >= threshold]
