"""
Advanced Data Content Classification and PII Detection
Classifies and categorizes data being transmitted for deep intelligence analysis
"""

import re
import json
import hashlib
from typing import Dict, List, Any, Optional, Tuple, Set, Generator
from datetime import datetime
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

from ..core.models import EvidenceItem, ScannerType
from ..core.config import ForensicConfig
from .base import BaseScanner

@dataclass
class PIIEntity:
    """Represents a detected PII entity with metadata"""
    entity_type: str
    value: str
    confidence: float
    context: str
    position: int
    risk_level: str

@dataclass
class ContentCategory:
    """Represents content classification with confidence scores"""
    category: str
    subcategory: str
    confidence: float
    keywords: List[str]
    risk_impact: str

@dataclass
class BehavioralPattern:
    """Represents detected behavioral patterns"""
    pattern_type: str
    frequency: int
    contexts: List[str]
    risk_assessment: str
    privacy_impact: str

class DataContentClassifier(BaseScanner):
    """Advanced data content classification and PII detection."""
    
    def __init__(self, config: Optional[ForensicConfig] = None):
        super().__init__(ScannerType.CONTENT_CLASSIFIER, config)
        self.pii_patterns = self._init_pii_patterns()
        self.content_categories = self._init_content_categories()
    
    def scan(self) -> Generator[EvidenceItem, None, None]:
        """Main scan method for content classification."""
        # For demo, yield a test evidence item
        yield EvidenceItem(
            id="content_classifier_test",
            source="content_classifier",
            type="test",
            content="Content classifier initialized successfully"
        )
    """Advanced content classification and PII detection system"""
    
    def __init__(self, config: Optional[ForensicConfig] = None):
        super().__init__(ScannerType.OSINT, config)
        self.pii_patterns = self._init_advanced_pii_patterns()
        self.content_categories = self._init_content_categories()
        self.behavioral_patterns = self._init_behavioral_patterns()
        self.sensitivity_keywords = self._init_sensitivity_keywords()
        
    def _init_advanced_pii_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize advanced PII detection patterns with context"""
        return {
            'email': {
                'pattern': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
                'confidence': 0.95,
                'risk_level': 'medium',
                'context_patterns': [
                    re.compile(r'(email|e-mail|mail|address).*?([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})', re.IGNORECASE),
                    re.compile(r'([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}).*?(email|e-mail|mail)', re.IGNORECASE)
                ]
            },
            'phone': {
                'pattern': re.compile(r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b'),
                'confidence': 0.90,
                'risk_level': 'high',
                'context_patterns': [
                    re.compile(r'(phone|mobile|cell|tel|telephone).*?(\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4})', re.IGNORECASE),
                    re.compile(r'(\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}).*?(phone|mobile|cell)', re.IGNORECASE)
                ]
            },
            'ssn': {
                'pattern': re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
                'confidence': 0.98,
                'risk_level': 'critical',
                'context_patterns': [
                    re.compile(r'(ssn|social.security|social.security.number).*?(\d{3}-\d{2}-\d{4})', re.IGNORECASE),
                    re.compile(r'(\d{3}-\d{2}-\d{4}).*?(ssn|social.security)', re.IGNORECASE)
                ]
            },
            'credit_card': {
                'pattern': re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b'),
                'confidence': 0.85,
                'risk_level': 'critical',
                'luhn_check': True,
                'context_patterns': [
                    re.compile(r'(card|credit.card|debit.card|payment).*?((?:\d{4}[-\s]?){3}\d{4})', re.IGNORECASE),
                    re.compile(r'((?:\d{4}[-\s]?){3}\d{4}).*?(card|credit|debit)', re.IGNORECASE)
                ]
            },
            'bank_account': {
                'pattern': re.compile(r'\b(?:account|acct)\s*(?:number|#)?\s*:?\s*(\d{8,17})\b', re.IGNORECASE),
                'confidence': 0.80,
                'risk_level': 'critical',
                'context_patterns': [
                    re.compile(r'(bank|account|routing|aba).*?(\d{8,17})', re.IGNORECASE),
                    re.compile(r'(\d{8,17}).*?(bank|account|routing)', re.IGNORECASE)
                ]
            },
            'passport': {
                'pattern': re.compile(r'\b[A-Z]{1,2}\d{7,9}\b'),
                'confidence': 0.75,
                'risk_level': 'high',
                'context_patterns': [
                    re.compile(r'(passport|travel.document).*?([A-Z]{1,2}\d{7,9})', re.IGNORECASE),
                    re.compile(r'([A-Z]{1,2}\d{7,9}).*?(passport|travel)', re.IGNORECASE)
                ]
            },
            'driver_license': {
                'pattern': re.compile(r'\b[A-Z]{1,2}-?\d{4,8}\b'),
                'confidence': 0.70,
                'risk_level': 'high',
                'context_patterns': [
                    re.compile(r'(driver|license|dl|identification).*?([A-Z]{1,2}-?\d{4,8})', re.IGNORECASE),
                    re.compile(r'([A-Z]{1,2}-?\d{4,8}).*?(driver|license)', re.IGNORECASE)
                ]
            },
            'ip_address': {
                'pattern': re.compile(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b'),
                'confidence': 0.60,
                'risk_level': 'low',
                'context_patterns': [
                    re.compile(r'(ip|address|host|server).*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', re.IGNORECASE),
                    re.compile(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}).*?(ip|address)', re.IGNORECASE)
                ]
            },
            'address': {
                'pattern': re.compile(r'\b\d+\s+[A-Za-z\s]+\s+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd|Court|Ct|Way|Place|Pl|Square|Sq|Terrace|Ter|Trail|Trl|Parkway|Pkwy|Circle|Cir)\b', re.IGNORECASE),
                'confidence': 0.85,
                'risk_level': 'medium',
                'context_patterns': [
                    re.compile(r'(address|location|home|live|residence).*?(\d+\s+[A-Za-z\s]+\s+(?:Street|St|Avenue|Ave))', re.IGNORECASE),
                    re.compile(r'(\d+\s+[A-Za-z\s]+\s+(?:Street|St|Avenue|Ave)).*?(address|location)', re.IGNORECASE)
                ]
            },
            'name': {
                'pattern': re.compile(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b'),
                'confidence': 0.65,
                'risk_level': 'medium',
                'context_patterns': [
                    re.compile(r'(name|full.name|first.name|last.name).*?([A-Z][a-z]+\s+[A-Z][a-z]+)', re.IGNORECASE),
                    re.compile(r'([A-Z][a-z]+\s+[A-Z][a-z]+).*(name|is|called)', re.IGNORECASE)
                ]
            },
            'birthdate': {
                'pattern': re.compile(r'\b(?:0[1-9]|1[0-2])[-/](?:0[1-9]|[12][0-9]|3[01])[-/]\d{4}\b|\b\d{4}[-/](?:0[1-9]|1[0-2])[-/](?:0[1-9]|[12][0-9]|3[01])\b'),
                'confidence': 0.75,
                'risk_level': 'medium',
                'context_patterns': [
                    re.compile(r'(birth|birthday|dob|date.of.birth).*?((?:0[1-9]|1[0-2])[-/](?:0[1-9]|[12][0-9]|3[01])[-/]\d{4})', re.IGNORECASE),
                    re.compile(r'((?:0[1-9]|1[0-2])[-/](?:0[1-9]|[12][0-9]|3[01])[-/]\d{4}).*?(birth|birthday)', re.IGNORECASE)
                ]
            },
            'url': {
                'pattern': re.compile(r'https?://[^\s<>"{}|\\^`\[\]]+'),
                'confidence': 0.90,
                'risk_level': 'low',
                'context_patterns': [
                    re.compile(r'(url|link|website|site|href).*?(https?://[^\s<>"{}|\\^`\[\]]+)', re.IGNORECASE),
                    re.compile(r'(https?://[^\s<>"{}|\\^`\[\]]+).*(url|link|website)', re.IGNORECASE)
                ]
            },
            'username': {
                'pattern': re.compile(r'\b[a-zA-Z0-9_]{3,20}\b'),
                'confidence': 0.50,
                'risk_level': 'low',
                'context_patterns': [
                    re.compile(r'(username|user|login|id).*?([a-zA-Z0-9_]{3,20})', re.IGNORECASE),
                    re.compile(r'([a-zA-Z0-9_]{3,20}).*(username|user|login)', re.IGNORECASE)
                ]
            },
            'password': {
                'pattern': re.compile(r'password\s*[:=]\s*[^\s]+', re.IGNORECASE),
                'confidence': 0.95,
                'risk_level': 'critical',
                'context_patterns': [
                    re.compile(r'(password|pass|pwd)\s*[:=]\s*([^\s]+)', re.IGNORECASE),
                    re.compile(r'([^\s]+)\s*[:=]\s*(password|pass)', re.IGNORECASE)
                ]
            }
        }
    
    def _init_content_categories(self) -> Dict[str, Dict[str, Any]]:
        """Initialize content classification categories"""
        return {
            'personal_identification': {
                'keywords': ['name', 'email', 'phone', 'address', 'ssn', 'passport', 'license', 'id', 'identification'],
                'risk_impact': 'high',
                'subcategories': {
                    'contact_info': ['email', 'phone', 'address'],
                    'government_id': ['ssn', 'passport', 'license', 'id'],
                    'demographic': ['age', 'gender', 'race', 'ethnicity', 'nationality']
                }
            },
            'financial_information': {
                'keywords': ['credit', 'card', 'bank', 'account', 'payment', 'transaction', 'purchase', 'invoice', 'billing'],
                'risk_impact': 'critical',
                'subcategories': {
                    'payment_cards': ['credit', 'card', 'debit', 'visa', 'mastercard', 'amex'],
                    'bank_accounts': ['bank', 'account', 'routing', 'aba', 'swift'],
                    'transactions': ['payment', 'purchase', 'transaction', 'invoice', 'billing']
                }
            },
            'health_information': {
                'keywords': ['health', 'medical', 'doctor', 'hospital', 'medicine', 'prescription', 'diagnosis', 'treatment'],
                'risk_impact': 'critical',
                'subcategories': {
                    'medical_history': ['diagnosis', 'condition', 'treatment', 'therapy'],
                    'medications': ['prescription', 'medicine', 'drug', 'dosage'],
                    'healthcare_providers': ['doctor', 'hospital', 'clinic', 'pharmacy']
                }
            },
            'behavioral_data': {
                'keywords': ['search', 'browse', 'click', 'view', 'like', 'share', 'comment', 'post', 'activity', 'behavior'],
                'risk_impact': 'medium',
                'subcategories': {
                    'browsing_behavior': ['search', 'browse', 'click', 'view', 'visit'],
                    'social_activity': ['like', 'share', 'comment', 'post', 'tweet'],
                    'interaction_patterns': ['engage', 'interact', 'respond', 'react']
                }
            },
            'location_data': {
                'keywords': ['location', 'gps', 'coordinate', 'latitude', 'longitude', 'address', 'city', 'state', 'country'],
                'risk_impact': 'medium',
                'subcategories': {
                    'precise_location': ['gps', 'coordinate', 'latitude', 'longitude'],
                    'general_location': ['city', 'state', 'country', 'region'],
                    'movement_patterns': ['route', 'path', 'trajectory', 'travel']
                }
            },
            'device_information': {
                'keywords': ['device', 'browser', 'os', 'system', 'hardware', 'software', 'version', 'model'],
                'risk_impact': 'low',
                'subcategories': {
                    'hardware': ['cpu', 'ram', 'memory', 'disk', 'graphics'],
                    'software': ['browser', 'application', 'version', 'update'],
                    'network': ['ip', 'mac', 'connection', 'bandwidth']
                }
            },
            'preferences_interests': {
                'keywords': ['interest', 'preference', 'like', 'enjoy', 'favorite', 'hobby', 'category'],
                'risk_impact': 'medium',
                'subcategories': {
                    'commercial_interests': ['buy', 'purchase', 'shop', 'product'],
                    'entertainment': ['movie', 'music', 'game', 'book', 'show'],
                    'lifestyle': ['food', 'travel', 'sport', 'fitness']
                }
            },
            'communications': {
                'keywords': ['message', 'chat', 'email', 'call', 'conversation', 'talk', 'discuss'],
                'risk_impact': 'medium',
                'subcategories': {
                    'messaging': ['message', 'chat', 'text', 'sms'],
                    'email': ['email', 'mail', 'message'],
                    'voice': ['call', 'talk', 'conversation']
                }
            }
        }
    
    def _init_behavioral_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize behavioral pattern detection"""
        return {
            'frequent_searches': {
                'indicators': ['search', 'query', 'look for', 'find'],
                'frequency_threshold': 5,
                'risk_impact': 'medium',
                'privacy_concern': 'interest_profiling'
            },
            'repeat_visits': {
                'indicators': ['visit', 'go to', 'navigate', 'browse'],
                'frequency_threshold': 10,
                'risk_impact': 'low',
                'privacy_concern': 'tracking'
            },
            'social_engagement': {
                'indicators': ['like', 'share', 'comment', 'post', 'interact'],
                'frequency_threshold': 15,
                'risk_impact': 'medium',
                'privacy_concern': 'social_graph_analysis'
            },
            'purchase_behavior': {
                'indicators': ['buy', 'purchase', 'order', 'cart', 'checkout'],
                'frequency_threshold': 3,
                'risk_impact': 'high',
                'privacy_concern': 'commercial_profiling'
            },
            'location_tracking': {
                'indicators': ['location', 'gps', 'nearby', 'around', 'close'],
                'frequency_threshold': 5,
                'risk_impact': 'high',
                'privacy_concern': 'location_surveillance'
            },
            'content_consumption': {
                'indicators': ['watch', 'view', 'read', 'listen', 'stream'],
                'frequency_threshold': 20,
                'risk_impact': 'medium',
                'privacy_concern': 'content_profiling'
            }
        }
    
    def _init_sensitivity_keywords(self) -> Dict[str, List[str]]:
        """Initialize sensitivity-based keyword classification"""
        return {
            'critical': [
                'password', 'ssn', 'social security', 'credit card', 'bank account',
                'routing number', 'swift code', 'passport', 'driver license',
                'medical record', 'health information', 'diagnosis', 'prescription'
            ],
            'high': [
                'phone number', 'home address', 'email address', 'birth date',
                'mother\'s maiden name', 'security question', 'pin code',
                'transaction', 'payment', 'billing', 'invoice'
            ],
            'medium': [
                'name', 'username', 'location', 'gps', 'coordinates',
                'interest', 'preference', 'behavior', 'activity',
                'search', 'browse', 'visit', 'click'
            ],
            'low': [
                'device', 'browser', 'system', 'version', 'model',
                'ip address', 'user agent', 'screen resolution', 'timezone'
            ]
        }
    
    def classify_content(self, text: str, context: str = "") -> Generator[EvidenceItem, None, None]:
        """Classify content and detect PII with context analysis"""
        try:
            # Detect PII entities
            pii_entities = self._detect_pii_entities(text, context)
            
            # Classify content categories
            content_categories = self._classify_text_categories(text)
            
            # Detect behavioral patterns
            behavioral_patterns = self._detect_behavioral_patterns(text)
            
            # Assess overall sensitivity
            sensitivity_score = self._calculate_sensitivity_score(pii_entities, content_categories)
            
            # Generate evidence items
            for entity in pii_entities:
                yield EvidenceItem(
                    id=f"pii_{entity.entity_type}_{hash(entity.value)}",
                    source="content_classifier",
                    type="pii_entity",
                    content=f"PII Detected: {entity.entity_type} - {entity.value[:20]}...",
                    metadata=asdict(entity)
                )
            
            for category in content_categories:
                yield EvidenceItem(
                    id=f"category_{category.category}_{hash(text)}",
                    source="content_classifier",
                    type="content_category",
                    content=f"Content Category: {category.category} - {category.subcategory}",
                    metadata=asdict(category)
                )
            
            for pattern in behavioral_patterns:
                yield EvidenceItem(
                    id=f"pattern_{pattern.pattern_type}_{hash(text)}",
                    source="content_classifier",
                    type="behavioral_pattern",
                    content=f"Behavioral Pattern: {pattern.pattern_type} (frequency: {pattern.frequency})",
                    metadata=asdict(pattern)
                )
            
            # Overall classification summary
            yield EvidenceItem(
                id=f"content_summary_{hash(text)}",
                source="content_classifier",
                type="content_summary",
                content=f"Content Analysis: {len(pii_entities)} PII items, {len(content_categories)} categories, sensitivity: {sensitivity_score}",
                metadata={
                    'pii_count': len(pii_entities),
                    'category_count': len(content_categories),
                    'pattern_count': len(behavioral_patterns),
                    'sensitivity_score': sensitivity_score,
                    'text_length': len(text),
                    'analysis_timestamp': datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            yield EvidenceItem(
                id="content_classification_error",
                source="content_classifier",
                type="error",
                content=f"Error classifying content: {str(e)}",
                metadata={"error": str(e)}
            )
    
    def _detect_pii_entities(self, text: str, context: str) -> List[PIIEntity]:
        """Detect PII entities with context validation"""
        entities = []
        
        for pii_type, pii_config in self.pii_patterns.items():
            pattern = pii_config['pattern']
            matches = pattern.finditer(text)
            
            for match in matches:
                value = match.group()
                position = match.start()
                
                # Validate with context patterns
                confidence = pii_config['confidence']
                context_match = False
                
                for context_pattern in pii_config.get('context_patterns', []):
                    if context_pattern.search(text[max(0, position-100):position+len(value)+100]):
                        context_match = True
                        confidence += 0.1
                        break
                
                # Additional validation for specific types
                if pii_type == 'credit_card' and pii_config.get('luhn_check'):
                    if self._luhn_check(value.replace('-', '').replace(' ', '')):
                        confidence += 0.1
                    else:
                        continue  # Skip invalid credit card numbers
                
                if pii_type == 'phone':
                    # Validate phone number format
                    digits = re.sub(r'\D', '', value)
                    if len(digits) == 10:
                        confidence += 0.05
                    elif len(digits) == 11 and digits[0] == '1':
                        confidence += 0.05
                
                # Extract surrounding context
                start_context = max(0, position - 50)
                end_context = min(len(text), position + len(value) + 50)
                surrounding_context = text[start_context:end_context]
                
                entity = PIIEntity(
                    entity_type=pii_type,
                    value=value,
                    confidence=min(confidence, 1.0),
                    context=surrounding_context,
                    position=position,
                    risk_level=pii_config['risk_level']
                )
                
                entities.append(entity)
        
        return entities
    
    def _classify_text_categories(self, text: str) -> List[ContentCategory]:
        """Classify text into content categories"""
        categories = []
        text_lower = text.lower()
        
        for category, config in self.content_categories.items():
            keywords_found = []
            subcategory_match = None
            
            # Check main keywords
            for keyword in config['keywords']:
                if keyword in text_lower:
                    keywords_found.append(keyword)
            
            # Check subcategories
            for subcategory, subkeywords in config['subcategories'].items():
                subkeyword_count = sum(1 for subkw in subkeywords if subkw in text_lower)
                if subkeyword_count > 0:
                    subcategory_match = subcategory
                    keywords_found.extend([subkw for subkw in subkeywords if subkw in text_lower])
            
            if keywords_found:
                confidence = min(len(keywords_found) / len(config['keywords']), 1.0)
                
                category_obj = ContentCategory(
                    category=category,
                    subcategory=subcategory_match or 'general',
                    confidence=confidence,
                    keywords=keywords_found,
                    risk_impact=config['risk_impact']
                )
                
                categories.append(category_obj)
        
        return categories
    
    def _detect_behavioral_patterns(self, text: str) -> List[BehavioralPattern]:
        """Detect behavioral patterns in text"""
        patterns = []
        text_lower = text.lower()
        
        for pattern_type, config in self.behavioral_patterns.items():
            frequency = 0
            contexts = []
            
            for indicator in config['indicators']:
                if indicator in text_lower:
                    frequency += text_lower.count(indicator)
                    
                    # Extract contexts around indicators
                    words = text_lower.split()
                    for i, word in enumerate(words):
                        if indicator in word:
                            start = max(0, i-3)
                            end = min(len(words), i+4)
                            context = ' '.join(words[start:end])
                            contexts.append(context)
            
            if frequency >= config['frequency_threshold']:
                pattern = BehavioralPattern(
                    pattern_type=pattern_type,
                    frequency=frequency,
                    contexts=contexts[:5],  # Limit to 5 contexts
                    risk_assessment='high' if frequency > config['frequency_threshold'] * 2 else 'medium',
                    privacy_concern=config['privacy_concern']
                )
                
                patterns.append(pattern)
        
        return patterns
    
    def _calculate_sensitivity_score(self, pii_entities: List[PIIEntity], content_categories: List[ContentCategory]) -> float:
        """Calculate overall sensitivity score (0-100)"""
        score = 0.0
        
        # PII contribution
        for entity in pii_entities:
            if entity.risk_level == 'critical':
                score += 25
            elif entity.risk_level == 'high':
                score += 15
            elif entity.risk_level == 'medium':
                score += 10
            elif entity.risk_level == 'low':
                score += 5
            
            # Add confidence factor
            score += entity.confidence * 5
        
        # Content category contribution
        for category in content_categories:
            if category.risk_impact == 'critical':
                score += 20 * category.confidence
            elif category.risk_impact == 'high':
                score += 15 * category.confidence
            elif category.risk_impact == 'medium':
                score += 10 * category.confidence
            elif category.risk_impact == 'low':
                score += 5 * category.confidence
        
        return min(score, 100.0)
    
    def _score_to_severity(self, score: float) -> str:
        """Convert sensitivity score to severity level"""
        if score >= 75:
            return 'critical'
        elif score >= 50:
            return 'high'
        elif score >= 25:
            return 'medium'
        else:
            return 'low'
    
    def _luhn_check(self, card_number: str) -> bool:
        """Validate credit card number using Luhn algorithm"""
        try:
            digits = [int(d) for d in card_number]
            checksum = digits[-1]
            digits = digits[:-1]
            
            # Double every second digit from right
            for i in range(len(digits)-2, -1, -2):
                digits[i] *= 2
                if digits[i] > 9:
                    digits[i] -= 9
            
            total = sum(digits) + checksum
            return total % 10 == 0
        except:
            return False
    
    def analyze_data_flow_content(self, data_packets: List[Dict[str, Any]]) -> Generator[EvidenceItem, None, None]:
        """Analyze content of data flow packets"""
        try:
            content_summary = {
                'total_packets': len(data_packets),
                'pii_packets': 0,
                'behavioral_packets': 0,
                'sensitive_categories': set(),
                'risk_distribution': {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
            }
            
            for packet in data_packets:
                payload = packet.get('payload', b'').decode('utf-8', errors='ignore')
                if payload:
                    # Classify packet content
                    for evidence in self.classify_content(payload, f"Packet from {packet.get('source_ip', 'unknown')}"):
                        if evidence.type == 'pii_entity':
                            content_summary['pii_packets'] += 1
                        elif evidence.type == 'behavioral_pattern':
                            content_summary['behavioral_packets'] += 1
                        
                        # Count evidence types
                        yield evidence
            
            # Generate summary
            yield EvidenceItem(
                id="data_flow_content_summary",
                source="content_classifier",
                type="content_analysis_summary",
                content=f"Data Flow Analysis: {content_summary['pii_packets']} PII packets, {content_summary['behavioral_packets']} behavioral packets",
                metadata={
                    **content_summary,
                    'sensitive_categories': list(content_summary['sensitive_categories']),
                    'analysis_timestamp': datetime.now().isoformat()
                }
            )
            
        except Exception as e:
            yield EvidenceItem(
                id="data_flow_analysis_error",
                source="content_classifier",
                type="error",
                content=f"Error analyzing data flow content: {str(e)}",
                metadata={"error": str(e)}
            )

def scan_content_classification(text_content: str = None, config: Optional[ForensicConfig] = None) -> Dict[str, Any]:
    """Perform comprehensive content classification and PII detection"""
    classifier = DataContentClassifier(config)
    
    results = {
        'pii_entities': [],
        'content_categories': [],
        'behavioral_patterns': [],
        'summary': {}
    }
    
    if text_content:
        # Classify the provided text
        for evidence in classifier.classify_content(text_content):
            if evidence.type == 'pii_entity':
                results['pii_entities'].append(asdict(evidence))
            elif evidence.type == 'content_category':
                results['content_categories'].append(asdict(evidence))
            elif evidence.type == 'behavioral_pattern':
                results['behavioral_patterns'].append(asdict(evidence))
            elif evidence.type == 'content_summary':
                results['summary'] = evidence.metadata
    
    return results
