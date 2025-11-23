"""Base scanner class for Digital Forensic Surgeon."""

from abc import ABC, abstractmethod
from typing import Generator, Optional, Dict, Any
from digital_forensic_surgeon.core.models import EvidenceItem, ScannerType
from digital_forensic_surgeon.core.config import ForensicConfig


class BaseScanner(ABC):
    """Base class for all forensic scanners."""
    
    def __init__(self, scanner_type: ScannerType, config: Optional[ForensicConfig] = None):
        self.scanner_type = scanner_type
        self.config = config or ForensicConfig()
    
    @abstractmethod
    def scan(self) -> Generator[EvidenceItem, None, None]:
        """Perform the scan and yield evidence items."""
        pass
    
    def get_scanner_info(self) -> Dict[str, Any]:
        """Get information about this scanner."""
        return {
            "type": self.scanner_type.value,
            "name": self.__class__.__name__,
            "description": self.__doc__ or "No description available"
        }
