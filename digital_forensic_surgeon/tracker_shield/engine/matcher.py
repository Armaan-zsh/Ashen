"""
Signature Matcher Engine
Matches HTTP requests against signature database
"""

from typing import List, Dict, Optional, Tuple
from urllib.parse import urlparse, parse_qs
import re
import json

from tracker_shield.core.signature import TrackerSignature, PatternType, EvidenceType

class MatchResult:
    """Result of signature matching"""
    
    def __init__(self, signature: TrackerSignature, confidence: float, evidence: Dict[str, any]):
        self.signature = signature
        self.confidence = confidence  # 0.0 - 1.0
        self.evidence = evidence      # Extracted data
    
    def __repr__(self):
        return f"<MatchResult {self.signature.id} ({self.confidence:.0%})>"

class SignatureMatcher:
    """Matches requests against signature database"""
    
    def __init__(self, signatures: List[TrackerSignature]):
        self.signatures = signatures
        
        # Build fast lookup index by domain
        self.domain_index = {}
        for sig in signatures:
            for pattern in sig.patterns:
                if pattern.type in [PatternType.DOMAIN, PatternType.EXACT_DOMAIN]:
                    domain = pattern.value or pattern.key
                    if domain:
                        if domain not in self.domain_index:
                            self.domain_index[domain] = []
                        self.domain_index[domain].append(sig)
        
        print(f"✅ Matcher loaded with {len(signatures)} signatures")
    
    def match(self, url: str, method: str = 'GET', headers: Dict = None, 
              body: str = None) -> List[MatchResult]:
        """
        Match request against all signatures
        
        Returns:
            List of matches sorted by confidence
        """
        headers = headers or {}
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        
        # Quick filter by domain
        candidates = self._get_candidates(parsed.netloc)
        
        matches = []
        for sig in candidates:
            result = self._match_signature(sig, parsed, params, headers, body)
            if result:
                matches.append(result)
        
        # Sort by confidence (highest first)
        matches.sort(key=lambda m: m.confidence, reverse=True)
        
        return matches
    
    def _get_candidates(self, domain: str) -> List[TrackerSignature]:
        """Get candidate signatures for domain"""
        candidates = []
        seen_ids = set()
        
        # Exact domain match
        if domain in self.domain_index:
            for sig in self.domain_index[domain]:
                if sig.id not in seen_ids:
                    candidates.append(sig)
                    seen_ids.add(sig.id)
        
        # Partial domain match (e.g., "facebook.com" matches "www.facebook.com")
        for indexed_domain, sigs in self.domain_index.items():
            if indexed_domain in domain or domain in indexed_domain:
                for sig in sigs:
                    if sig.id not in seen_ids:
                        candidates.append(sig)
                        seen_ids.add(sig.id)
        
        return candidates
    
    def _match_signature(self, sig: TrackerSignature, parsed, params, 
                        headers, body) -> Optional[MatchResult]:
        """Check if signature matches request"""
        
        matched_patterns = 0
        required_patterns = sum(1 for p in sig.patterns if p.required)
        
        for pattern in sig.patterns:
            if self._match_pattern(pattern, parsed, params, headers, body):
                matched_patterns += 1
            elif pattern.required:
                # Required pattern didn't match
                return None
        
        if matched_patterns == 0:
            return None
        
        # Calculate confidence
        confidence = matched_patterns / len(sig.patterns)
        
        # Extract evidence
        evidence = self._extract_evidence(sig, parsed, params, headers, body)
        
        return MatchResult(sig, confidence, evidence)
    
    def _match_pattern(self, pattern, parsed, params, headers, body) -> bool:
        """Check if single pattern matches"""
        
        if pattern.type == PatternType.DOMAIN:
            return pattern.value in parsed.netloc
        
        elif pattern.type == PatternType.EXACT_DOMAIN:
            return pattern.value == parsed.netloc
        
        elif pattern.type == PatternType.PATH:
            return pattern.value in parsed.path
        
        elif pattern.type == PatternType.PARAM_KEY:
            return pattern.key in params
        
        elif pattern.type == PatternType.PARAM_VALUE:
            if pattern.key not in params:
                return False
            values = params[pattern.key]
            if pattern.regex:
                return any(re.search(pattern.regex, v) for v in values)
            else:
                return pattern.value in values
        
        elif pattern.type == PatternType.HEADER:
            return pattern.key.lower() in {k.lower(): v for k, v in headers.items()}
        
        elif pattern.type == PatternType.BODY_CONTAINS:
            return body and pattern.value in body
        
        return False
    
    def _extract_evidence(self, sig, parsed, params, headers, body) -> Dict:
        """Extract evidence from request"""
        
        evidence = {}
        
        for ev in sig.evidence:
            value = None
            
            if ev.type == EvidenceType.PARAM:
                if ev.key in params:
                    value = params[ev.key][0]  # First value
            
            elif ev.type == EvidenceType.HEADER:
                value = headers.get(ev.key)
            
            elif ev.type == EvidenceType.COOKIE:
                cookie_header = headers.get('Cookie', '')
                # Simple cookie parsing
                for cookie in cookie_header.split(';'):
                    if '=' in cookie:
                        k, v = cookie.strip().split('=', 1)
                        if k == ev.key:
                            value = v
                            break
            
            elif ev.type == EvidenceType.JSON_PATH and body:
                try:
                    data = json.loads(body)
                    # Simple JSON path (e.g., $.fbp)
                    path = ev.path.lstrip('$.')
                    value = data.get(path)
                except:
                    pass
            
            elif ev.type == EvidenceType.REGEX:
                search_text = body or parsed.query
                if search_text and ev.regex:
                    match = re.search(ev.regex, search_text)
                    if match:
                        value = match.group(1) if match.groups() else match.group(0)
            
            if value:
                # Anonymize PII if needed
                if ev.pii:
                    value = self._anonymize(value)
                
                evidence[ev.name] = value
        
        return evidence
    
    def _anonymize(self, value: str) -> str:
        """Anonymize PII for contribution"""
        # Hash sensitive data
        import hashlib
        if len(value) > 10:  # Likely an ID/token
            return f"<REDACTED:{hashlib.md5(value.encode()).hexdigest()[:8]}>"
        return "<REDACTED>"
