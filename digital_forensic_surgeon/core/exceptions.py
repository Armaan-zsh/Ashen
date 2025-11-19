"""Custom exceptions for Digital Forensic Surgeon."""

from __future__ import annotations


class ForensicError(Exception):
    """Base exception for all forensic-related errors."""
    
    def __init__(self, message: str, original_error: Exception | None = None):
        super().__init__(message)
        self.original_error = original_error


class DatabaseError(ForensicError):
    """Raised when database operations fail."""
    pass


class ScannerError(ForensicError):
    """Raised when scanner operations fail."""
    pass


class ReportError(ForensicError):
    """Raised when report generation fails."""
    pass


class ConfigurationError(ForensicError):
    """Raised when configuration is invalid or missing."""
    pass


class NetworkError(ForensicError):
    """Raised when network operations fail."""
    pass


class AuthenticationError(ForensicError):
    """Raised when authentication operations fail."""
    pass


class ValidationError(ForensicError):
    """Raised when data validation fails."""
    pass


class SecurityError(ForensicError):
    """Raised when security constraints are violated."""
    pass
