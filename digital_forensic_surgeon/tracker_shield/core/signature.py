"""
TrackerShield Signature Format (.tsig)
YAML-based signature for tracker detection
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum

class PatternType(Enum):
    """Types of patterns to match"""
    DOMAIN = "domain"           # URL domain contains
    EXACT_DOMAIN = "exact_domain"  # URL domain equals
    PATH = "path"               # URL path contains
    PARAM_KEY = "param_key"     # URL param key exists
    PARAM_VALUE = "param_value" # URL param value matches
    HEADER = "header"           # HTTP header exists
    BODY_CONTAINS = "body"      # POST body contains

class EvidenceType(Enum):
    """Types of evidence to extract"""
    PARAM = "param"             # URL parameter
    COOKIE = "cookie"           # Cookie value
    JSON_PATH = "json_path"     # JSON path extraction
    REGEX = "regex"             # Regex capture group
    HEADER = "header"           # HTTP header

@dataclass
class Pattern:
    """A matching pattern"""
    type: PatternType
    key: Optional[str] = None      # Param/header key
    value: Optional[str] = None    # Expected value
    regex: Optional[str] = None    # Regex pattern
    required: bool = True          # Must match?

@dataclass
class Evidence:
    """Evidence to extract from request"""
    type: EvidenceType
    name: str                      # Human readable name
    key: Optional[str] = None      # Param/cookie/header key
    path: Optional[str] = None     # JSON path ($.fbp)
    regex: Optional[str] = None    # Regex pattern
    pii: bool = False              # Contains PII?

@dataclass
class TrackerSignature:
    """Complete tracker signature"""
    
    # Metadata
    id: str                        # FB_PIXEL_001
    version: int                   # Signature version
    name: str                      # Facebook Pixel - Page View
    company: str                   # Meta/Facebook
    category: str                  # advertising, analytics, etc.
    risk_score: float             # 0-10
    tier: str                      # free, pro, god
    
    # Matching
    patterns: List[Pattern]        # List of patterns to match
    
    # Evidence extraction
    evidence: List[Evidence]       # What to extract
    
    # Documentation
    description: Optional[str] = None
    references: List[str] = None   # URLs to docs
    tags: List[str] = None         # Additional tags

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for YAML"""
        return {
            'id': self.id,
            'version': self.version,
            'name': self.name,
            'company': self.company,
            'category': self.category,
            'risk_score': self.risk_score,
            'tier': self.tier,
            'patterns': [
                {
                    'type': p.type.value,
                    'key': p.key,
                    'value': p.value,
                    'regex': p.regex,
                    'required': p.required
                } for p in self.patterns
            ],
            'evidence': [
                {
                    'type': e.type.value,
                    'name': e.name,
                    'key': e.key,
                    'path': e.path,
                    'regex': e.regex,
                    'pii': e.pii
                } for e in self.evidence
            ],
            'description': self.description,
            'references': self.references or [],
            'tags': self.tags or []
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TrackerSignature':
        """Load from dictionary"""
        return cls(
            id=data['id'],
            version=data.get('version', 1),
            name=data['name'],
            company=data['company'],
            category=data['category'],
            risk_score=data['risk_score'],
            tier=data.get('tier', 'free'),
            patterns=[
                Pattern(
                    type=PatternType(p['type']),
                    key=p.get('key'),
                    value=p.get('value'),
                    regex=p.get('regex'),
                    required=p.get('required', True)
                ) for p in data.get('patterns', [])
            ],
            evidence=[
                Evidence(
                    type=EvidenceType(e['type']),
                    name=e['name'],
                    key=e.get('key'),
                    path=e.get('path'),
                    regex=e.get('regex'),
                    pii=e.get('pii', False)
                ) for e in data.get('evidence', [])
            ],
            description=data.get('description'),
            references=data.get('references', []),
            tags=data.get('tags', [])
        )
