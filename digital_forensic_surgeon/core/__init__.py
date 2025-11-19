"""Core module for Digital Forensic Surgeon."""

from __future__ import annotations

from .models import (
    Credential,
    Account, 
    Service,
    ForensicResult,
    RiskAssessment,
    EvidenceItem,
    SystemInfo,
)

from .exceptions import (
    ForensicError,
    DatabaseError,
    ScannerError,
    ReportError,
    ConfigurationError,
    NetworkError,
    AuthenticationError,
    ValidationError,
    SecurityError,
)

from .config import (
    ForensicConfig,
    get_config,
    set_config,
    load_config,
)

__all__ = [
    # Models
    "Credential",
    "Account",
    "Service", 
    "ForensicResult",
    "RiskAssessment",
    "EvidenceItem",
    "SystemInfo",
    
    # Exceptions
    "ForensicError",
    "DatabaseError",
    "ScannerError",
    "ReportError", 
    "ConfigurationError",
    "NetworkError",
    "AuthenticationError",
    "ValidationError",
    "SecurityError",
    
    # Config
    "ForensicConfig",
    "get_config",
    "set_config", 
    "load_config",
]
