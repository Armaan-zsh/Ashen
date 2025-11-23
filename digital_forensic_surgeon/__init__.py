"""Digital Forensic Surgeon - Core package for digital forensics and privacy audit tools."""

from __future__ import annotations

__version__ = "1.0.0"
__author__ = "MiniMax Agent"

from .core.models import (
    Credential,
    Account,
    Service,
    ForensicResult,
    RiskAssessment,
    EvidenceItem,
    SystemInfo,
)

from .core.exceptions import (
    ForensicError,
    DatabaseError,
    ScannerError,
    ReportError,
    ConfigurationError,
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
]
