"""
Comprehensive Account Security Auditor
Analyzes account security configurations, vulnerabilities, and protection mechanisms
"""

import re
import json
import hashlib
import secrets
from typing import Dict, List, Any, Optional, Generator, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import logging

from ..core.models import EvidenceItem, ScannerType, Account, Credential
from ..core.config import ForensicConfig
from .base import BaseScanner

@dataclass
class SecurityVulnerability:
    """Represents a security vulnerability found"""
    vulnerability_type: str
    severity: str
    description: str
    affected_accounts: List[str]
    remediation: str
    cvss_score: float
    cwe_id: Optional[str]

@dataclass
class AccountSecurityScore:
    """Represents security score for an account"""
    account_id: str
    service: str
    username: str
    overall_score: float
    password_strength: float
    mfa_enabled: bool
    security_questions: bool
    recovery_options: int
    last_password_change: Optional[datetime]
    failed_login_attempts: int
    active_sessions: int
    privacy_settings: float

@dataclass
class SecurityRecommendation:
    """Represents security improvement recommendation"""
    priority: str
    category: str
    recommendation: str
    impact: str
    effort: str
    affected_accounts: List[str]

class AccountSecurityAuditor(BaseScanner):
    """Comprehensive account security auditing"""
    
    def __init__(self, config: Optional[ForensicConfig] = None):
        super().__init__(ScannerType.SECURITY_AUDITOR, config)
        self.security_checks = {}
    
    def scan(self) -> Generator[EvidenceItem, None, None]:
        """Main scan method for security auditing."""
        yield EvidenceItem(
            id="security_auditor_test",
            source="security_auditor",
            type="test",
            content="Security auditor initialized successfully",
            metadata={"test": True}
        )
    """Comprehensive account security analysis and auditing"""
    
    def __init__(self, config: Optional[ForensicConfig] = None):
        super().__init__(ScannerType.SECURITY_AUDITOR, config)
        self.password_patterns = self._init_password_patterns()
        self.security_benchmarks = self._init_security_benchmarks()
        self.common_vulnerabilities = self._init_common_vulnerabilities()
        
    def _init_password_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize password analysis patterns"""
        return {
            'weak_patterns': {
                'sequences': ['123456', 'abcdef', 'qwerty', 'password', 'admin'],
                'repeated_chars': r'(.)\1{2,}',  # 3+ repeated characters
                'keyboard_patterns': r'qwerty|asdf|zxcv|1234|abcd',
                'common_words': ['password', 'admin', 'user', 'login', 'welcome'],
                'personal_info': r'\d{4}$|^\d{6}$|birth|name|year',
                'length_short': 8,
                'length_weak': 12
            },
            'strength_criteria': {
                'length_excellent': 16,
                'length_good': 12,
                'length_fair': 8,
                'uppercase_bonus': 2,
                'lowercase_bonus': 2,
                'numbers_bonus': 2,
                'special_bonus': 3,
                'variety_bonus': 3
            },
            'breached_passwords': [
                '123456', 'password', '123456789', '12345678', '12345',
                '1234567', '1234567890', '1234', 'qwerty', 'abc123',
                '111111', '123123', 'admin', 'letmein', 'welcome',
                'monkey', '1234567890', 'password1', 'qwertyuiop'
            ]
        }
    
    def _init_security_benchmarks(self) -> Dict[str, Dict[str, Any]]:
        """Initialize security configuration benchmarks"""
        return {
            'password_policy': {
                'min_length': 12,
                'require_uppercase': True,
                'require_lowercase': True,
                'require_numbers': True,
                'require_special': True,
                'max_age_days': 90,
                'history_count': 12,
                'complexity_score': 8.0
            },
            'mfa_requirements': {
                'preferred_methods': ['totp', 'hardware_key', 'biometric'],
                'acceptable_methods': ['sms', 'email'],
                'minimum_methods': 1,
                'backup_codes_required': True
            },
            'session_security': {
                'max_session_duration_hours': 8,
                'idle_timeout_minutes': 30,
                'concurrent_sessions_limit': 3,
                'require_reauth_sensitive': True
            },
            'privacy_settings': {
                'profile_visibility': 'private',
                'data_sharing': 'limited',
                'third_party_access': 'minimal',
                'location_sharing': 'disabled'
            }
        }
    
    def _init_common_vulnerabilities(self) -> Dict[str, Dict[str, Any]]:
        """Initialize common security vulnerabilities"""
        return {
            'weak_password': {
                'cvss_score': 7.5,
                'cwe_id': 'CWE-521',
                'description': 'Weak password that can be easily guessed or cracked',
                'remediation': 'Use strong, unique passwords with at least 12 characters, including uppercase, lowercase, numbers, and special characters'
            },
            'no_mfa': {
                'cvss_score': 6.5,
                'cwe_id': 'CWE-303',
                'description': 'Multi-factor authentication not enabled',
                'remediation': 'Enable multi-factor authentication using authenticator apps, hardware keys, or biometrics'
            },
            'reused_password': {
                'cvss_score': 8.0,
                'cwe_id': 'CWE-358',
                'description': 'Password reused across multiple services',
                'remediation': 'Use unique passwords for each service. Consider using a password manager'
            },
            'old_password': {
                'cvss_score': 5.0,
                'cwe_id': 'CWE-263',
                'description': 'Password not changed in over 90 days',
                'remediation': 'Change passwords regularly, at least every 90 days'
            },
            'excessive_sessions': {
                'cvss_score': 4.0,
                'cwe_id': 'CWE-613',
                'description': 'Too many active sessions',
                'remediation': 'Limit concurrent sessions and regularly review active logins'
            },
            'weak_recovery': {
                'cvss_score': 5.5,
                'cwe_id': 'CWE-640',
                'description': 'Weak account recovery options',
                'remediation': 'Use strong recovery methods and security questions'
            },
            'public_profile': {
                'cvss_score': 3.0,
                'cwe_id': 'CWE-200',
                'description': 'Public profile exposing personal information',
                'remediation': 'Set profile to private and limit public information sharing'
            }
        }
    
    def audit_account_security(self, accounts: List[Account], credentials: List[Credential]) -> Generator[EvidenceItem, None, None]:
        """Perform comprehensive security audit of accounts"""
        try:
            # Analyze each account
            for account in accounts:
                security_score = self._analyze_account_security(account, credentials)
                
                yield EvidenceItem(
                    id=f"security_score_{account.service}_{account.username}_{int(time.time())}",
                    source="security_auditor",
                    data_type="account_security_score",
                    description=f"Security Score: {account.service} - {account.username} ({security_score.overall_score:.1f}/10)",
                    severity=self._score_to_severity(security_score.overall_score),
                    metadata=asdict(security_score)
                )
            
            # Identify vulnerabilities
            vulnerabilities = self._identify_vulnerabilities(accounts, credentials)
            
            for vulnerability in vulnerabilities:
                yield EvidenceItem(
                    id=f"vulnerability_{vulnerability.vulnerability_type}_{int(time.time())}",
                    source="security_auditor",
                    data_type="security_vulnerability",
                    description=f"Security Vulnerability: {vulnerability.vulnerability_type} - {vulnerability.description}",
                    severity=vulnerability.severity,
                    metadata=asdict(vulnerability)
                )
            
            # Generate recommendations
            recommendations = self._generate_security_recommendations(accounts, credentials, vulnerabilities)
            
            for recommendation in recommendations:
                yield EvidenceItem(
                    id=f"recommendation_{recommendation.category}_{int(time.time())}",
                    source="security_auditor",
                    data_type="security_recommendation",
                    description=f"Security Recommendation: {recommendation.recommendation}",
                    severity=recommendation.priority,
                    metadata=asdict(recommendation)
                )
                
        except Exception as e:
            yield EvidenceItem(
                id="security_audit_error",
                source="security_auditor",
                data_type="error",
                description=f"Error during security audit: {str(e)}",
                severity="medium",
                metadata={"error": str(e)}
            )
    
    def _analyze_account_security(self, account: Account, credentials: List[Credential]) -> AccountSecurityScore:
        """Analyze security for a single account"""
        # Find matching credentials
        account_credentials = [
            cred for cred in credentials
            if cred.service.lower() == account.service.lower() and
            cred.username.lower() == account.username.lower()
        ]
        
        # Password strength analysis
        password_strength = 0.0
        if account_credentials:
            password = account_credentials[0].password
            password_strength = self._analyze_password_strength(password)
        
        # MFA analysis (placeholder - would need service-specific checks)
        mfa_enabled = self._check_mfa_status(account)
        
        # Security questions analysis
        security_questions = self._check_security_questions(account)
        
        # Recovery options analysis
        recovery_options = self._count_recovery_options(account)
        
        # Last password change (placeholder)
        last_password_change = self._get_last_password_change(account)
        
        # Failed login attempts (placeholder)
        failed_login_attempts = self._get_failed_login_attempts(account)
        
        # Active sessions (placeholder)
        active_sessions = self._get_active_sessions(account)
        
        # Privacy settings analysis
        privacy_settings = self._analyze_privacy_settings(account)
        
        # Calculate overall score
        overall_score = self._calculate_overall_security_score(
            password_strength, mfa_enabled, security_questions,
            recovery_options, privacy_settings, active_sessions
        )
        
        return AccountSecurityScore(
            account_id=account.id,
            service=account.service,
            username=account.username,
            overall_score=overall_score,
            password_strength=password_strength,
            mfa_enabled=mfa_enabled,
            security_questions=security_questions,
            recovery_options=recovery_options,
            last_password_change=last_password_change,
            failed_login_attempts=failed_login_attempts,
            active_sessions=active_sessions,
            privacy_settings=privacy_settings
        )
    
    def _analyze_password_strength(self, password: str) -> float:
        """Analyze password strength"""
        if not password:
            return 0.0
        
        score = 0.0
        patterns = self.password_patterns['weak_patterns']
        criteria = self.password_patterns['strength_criteria']
        
        # Length scoring
        length = len(password)
        if length >= criteria['length_excellent']:
            score += 3.0
        elif length >= criteria['length_good']:
            score += 2.5
        elif length >= criteria['length_fair']:
            score += 1.5
        else:
            score += 0.5
        
        # Character variety
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_numbers = any(c.isdigit() for c in password)
        has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password)
        
        variety_count = sum([has_upper, has_lower, has_numbers, has_special])
        score += variety_count * 0.5
        
        # Bonus for character types
        if has_upper:
            score += criteria['uppercase_bonus'] * 0.1
        if has_lower:
            score += criteria['lowercase_bonus'] * 0.1
        if has_numbers:
            score += criteria['numbers_bonus'] * 0.1
        if has_special:
            score += criteria['special_bonus'] * 0.1
        
        # Check for weak patterns (penalties)
        if password.lower() in patterns['common_words']:
            score -= 2.0
        
        if re.search(patterns['repeated_chars'], password):
            score -= 1.5
        
        if re.search(patterns['keyboard_patterns'], password.lower()):
            score -= 1.0
        
        if password.lower() in self.password_patterns['breached_passwords']:
            score -= 3.0
        
        # Entropy calculation (simplified)
        char_set_size = 0
        if has_lower:
            char_set_size += 26
        if has_upper:
            char_set_size += 26
        if has_numbers:
            char_set_size += 10
        if has_special:
            char_set_size += 20
        
        if char_set_size > 0:
            entropy = length * (char_set_size.bit_length())
            score += min(entropy / 20, 2.0)  # Cap at 2.0 points
        
        return max(0.0, min(10.0, score))
    
    def _check_mfa_status(self, account: Account) -> bool:
        """Check if MFA is enabled (placeholder implementation)"""
        # This would typically involve API calls to check service-specific MFA status
        # For now, return based on service heuristics
        
        service_lower = account.service.lower()
        
        # Known services with MFA
        mfa_services = ['google', 'microsoft', 'apple', 'facebook', 'twitter', 'github', 'amazon']
        
        # Assume MFA is enabled for major services (placeholder)
        if any(service in service_lower for service in mfa_services):
            return True
        
        return False
    
    def _check_security_questions(self, account: Account) -> bool:
        """Check if security questions are configured"""
        # Placeholder implementation
        # Would typically check service-specific security question settings
        return False
    
    def _count_recovery_options(self, account: Account) -> int:
        """Count available recovery options"""
        # Placeholder implementation
        # Would typically check email recovery, phone recovery, backup codes, etc.
        return 1
    
    def _get_last_password_change(self, account: Account) -> Optional[datetime]:
        """Get last password change timestamp"""
        # Placeholder implementation
        # Would typically retrieve from service API or logs
        return datetime.now() - timedelta(days=45)
    
    def _get_failed_login_attempts(self, account: Account) -> int:
        """Get count of failed login attempts"""
        # Placeholder implementation
        # Would typically retrieve from service API or logs
        return 2
    
    def _get_active_sessions(self, account: Account) -> int:
        """Get count of active sessions"""
        # Placeholder implementation
        # Would typically retrieve from service API
        return 1
    
    def _analyze_privacy_settings(self, account: Account) -> float:
        """Analyze privacy settings score"""
        # Placeholder implementation
        # Would typically check service-specific privacy settings
        
        service_lower = account.service.lower()
        
        # Default privacy score based on service type
        if 'social' in service_lower or 'facebook' in service_lower:
            return 6.0  # Social media often have default public settings
        elif 'bank' in service_lower or 'financial' in service_lower:
            return 8.0  # Financial services usually have better privacy
        elif 'email' in service_lower:
            return 7.0  # Email services moderate privacy
        else:
            return 7.5  # Default moderate privacy
    
    def _calculate_overall_security_score(self, password_strength: float, mfa_enabled: bool,
                                        security_questions: bool, recovery_options: int,
                                        privacy_settings: float, active_sessions: int) -> float:
        """Calculate overall security score"""
        score = 0.0
        
        # Password strength (30% weight)
        score += password_strength * 0.3
        
        # MFA (25% weight)
        score += (10.0 if mfa_enabled else 0.0) * 0.25
        
        # Security questions (10% weight)
        score += (10.0 if security_questions else 0.0) * 0.1
        
        # Recovery options (10% weight)
        recovery_score = min(recovery_options * 2.5, 10.0)
        score += recovery_score * 0.1
        
        # Privacy settings (15% weight)
        score += privacy_settings * 0.15
        
        # Active sessions (10% weight)
        session_score = max(0.0, 10.0 - active_sessions * 2.0)
        score += session_score * 0.1
        
        return max(0.0, min(10.0, score))
    
    def _identify_vulnerabilities(self, accounts: List[Account], credentials: List[Credential]) -> List[SecurityVulnerability]:
        """Identify security vulnerabilities"""
        vulnerabilities = []
        
        # Group accounts by service for analysis
        service_accounts = {}
        for account in accounts:
            if account.service not in service_accounts:
                service_accounts[account.service] = []
            service_accounts[account.service].append(account)
        
        # Check each account for vulnerabilities
        for account in accounts:
            account_vulns = self._check_account_vulnerabilities(account, credentials)
            vulnerabilities.extend(account_vulns)
        
        # Check for cross-account vulnerabilities
        cross_vulns = self._check_cross_account_vulnerabilities(accounts, credentials)
        vulnerabilities.extend(cross_vulns)
        
        return vulnerabilities
    
    def _check_account_vulnerabilities(self, account: Account, credentials: List[Credential]) -> List[SecurityVulnerability]:
        """Check individual account for vulnerabilities"""
        vulnerabilities = []
        
        # Find matching credentials
        account_credentials = [
            cred for cred in credentials
            if cred.service.lower() == account.service.lower() and
            cred.username.lower() == account.username.lower()
        ]
        
        # Check password strength
        if account_credentials:
            password = account_credentials[0].password
            password_strength = self._analyze_password_strength(password)
            
            if password_strength < 5.0:
                vuln_info = self.common_vulnerabilities['weak_password']
                vulnerabilities.append(SecurityVulnerability(
                    vulnerability_type='weak_password',
                    severity='high' if password_strength < 3.0 else 'medium',
                    description=vuln_info['description'],
                    affected_accounts=[f"{account.service}:{account.username}"],
                    remediation=vuln_info['remediation'],
                    cvss_score=vuln_info['cvss_score'],
                    cwe_id=vuln_info['cwe_id']
                ))
        
        # Check MFA
        mfa_enabled = self._check_mfa_status(account)
        if not mfa_enabled:
            vuln_info = self.common_vulnerabilities['no_mfa']
            vulnerabilities.append(SecurityVulnerability(
                vulnerability_type='no_mfa',
                severity='high',
                description=vuln_info['description'],
                affected_accounts=[f"{account.service}:{account.username}"],
                remediation=vuln_info['remediation'],
                cvss_score=vuln_info['cvss_score'],
                cwe_id=vuln_info['cwe_id']
            ))
        
        # Check active sessions
        active_sessions = self._get_active_sessions(account)
        if active_sessions > 3:
            vuln_info = self.common_vulnerabilities['excessive_sessions']
            vulnerabilities.append(SecurityVulnerability(
                vulnerability_type='excessive_sessions',
                severity='medium',
                description=vuln_info['description'],
                affected_accounts=[f"{account.service}:{account.username}"],
                remediation=vuln_info['remediation'],
                cvss_score=vuln_info['cvss_score'],
                cwe_id=vuln_info['cwe_id']
            ))
        
        # Check password age
        last_change = self._get_last_password_change(account)
        if last_change and (datetime.now() - last_change).days > 90:
            vuln_info = self.common_vulnerabilities['old_password']
            vulnerabilities.append(SecurityVulnerability(
                vulnerability_type='old_password',
                severity='medium',
                description=vuln_info['description'],
                affected_accounts=[f"{account.service}:{account.username}"],
                remediation=vuln_info['remediation'],
                cvss_score=vuln_info['cvss_score'],
                cwe_id=vuln_info['cwe_id']
            ))
        
        return vulnerabilities
    
    def _check_cross_account_vulnerabilities(self, accounts: List[Account], credentials: List[Credential]) -> List[SecurityVulnerability]:
        """Check for cross-account security issues"""
        vulnerabilities = []
        
        # Check for reused passwords
        password_usage = {}
        for cred in credentials:
            password_hash = hashlib.sha256(cred.password.encode()).hexdigest()
            if password_hash not in password_usage:
                password_usage[password_hash] = []
            password_usage[password_hash].append(f"{cred.service}:{cred.username}")
        
        for password_hash, accounts_list in password_usage.items():
            if len(accounts_list) > 1:
                vuln_info = self.common_vulnerabilities['reused_password']
                vulnerabilities.append(SecurityVulnerability(
                    vulnerability_type='reused_password',
                    severity='critical',
                    description=vuln_info['description'],
                    affected_accounts=accounts_list,
                    remediation=vuln_info['remediation'],
                    cvss_score=vuln_info['cvss_score'],
                    cwe_id=vuln_info['cwe_id']
                ))
        
        return vulnerabilities
    
    def _generate_security_recommendations(self, accounts: List[Account], credentials: List[Credential],
                                         vulnerabilities: List[SecurityVulnerability]) -> List[SecurityRecommendation]:
        """Generate security improvement recommendations"""
        recommendations = []
        
        # Analyze vulnerability patterns
        vuln_types = [v.vulnerability_type for v in vulnerabilities]
        vuln_counts = {}
        for vuln_type in vuln_types:
            vuln_counts[vuln_type] = vuln_counts.get(vuln_type, 0) + 1
        
        # Password recommendations
        if 'weak_password' in vuln_counts:
            recommendations.append(SecurityRecommendation(
                priority='high',
                category='password_security',
                recommendation='Strengthen weak passwords using a combination of uppercase, lowercase, numbers, and special characters',
                impact='Significantly reduces risk of password guessing and brute force attacks',
                effort='medium',
                affected_accounts=[v.affected_accounts for v in vulnerabilities if v.vulnerability_type == 'weak_password'][0]
            ))
        
        if 'reused_password' in vuln_counts:
            recommendations.append(SecurityRecommendation(
                priority='critical',
                category='password_security',
                recommendation='Use unique passwords for each service. Consider using a password manager',
                impact='Prevents credential stuffing attacks and limits breach impact',
                effort='high',
                affected_accounts=[v.affected_accounts for v in vulnerabilities if v.vulnerability_type == 'reused_password'][0]
            ))
        
        # MFA recommendations
        if 'no_mfa' in vuln_counts:
            recommendations.append(SecurityRecommendation(
                priority='high',
                category='authentication',
                recommendation='Enable multi-factor authentication on all accounts that support it',
                impact='Adds strong protection against unauthorized access even if passwords are compromised',
                effort='low',
                affected_accounts=[v.affected_accounts for v in vulnerabilities if v.vulnerability_type == 'no_mfa'][0]
            ))
        
        # Session management recommendations
        if 'excessive_sessions' in vuln_counts:
            recommendations.append(SecurityRecommendation(
                priority='medium',
                category='session_management',
                recommendation='Review and close unnecessary active sessions regularly',
                impact='Reduces risk of session hijacking and unauthorized access',
                effort='low',
                affected_accounts=[v.affected_accounts for v in vulnerabilities if v.vulnerability_type == 'excessive_sessions'][0]
            ))
        
        # Password rotation recommendations
        if 'old_password' in vuln_counts:
            recommendations.append(SecurityRecommendation(
                priority='medium',
                category='password_management',
                recommendation='Establish regular password rotation schedule (every 90 days)',
                impact='Limits exposure from potential password compromises',
                effort='medium',
                affected_accounts=[v.affected_accounts for v in vulnerabilities if v.vulnerability_type == 'old_password'][0]
            ))
        
        # General security recommendations
        if len(accounts) > 20:
            recommendations.append(SecurityRecommendation(
                priority='medium',
                category='account_management',
                recommendation='Consider consolidating or removing unused accounts to reduce attack surface',
                impact='Reduces number of potential entry points for attackers',
                effort='medium',
                affected_accounts=[]
            ))
        
        # Privacy recommendations
        privacy_scores = []
        for account in accounts:
            score = self._analyze_privacy_settings(account)
            privacy_scores.append(score)
        
        if privacy_scores and sum(privacy_scores) / len(privacy_scores) < 7.0:
            recommendations.append(SecurityRecommendation(
                priority='medium',
                category='privacy',
                recommendation='Review and strengthen privacy settings across all accounts',
                impact='Reduces exposure of personal information and data collection',
                effort='medium',
                affected_accounts=[]
            ))
        
        return recommendations
    
    def _score_to_severity(self, score: float) -> str:
        """Convert security score to severity level"""
        if score >= 8.0:
            return 'low'
        elif score >= 6.0:
            return 'medium'
        elif score >= 4.0:
            return 'high'
        else:
            return 'critical'
    
    def generate_security_report(self, accounts: List[Account], credentials: List[Credential]) -> Dict[str, Any]:
        """Generate comprehensive security report"""
        # Analyze all accounts
        security_scores = []
        for account in accounts:
            score = self._analyze_account_security(account, credentials)
            security_scores.append(score)
        
        # Identify vulnerabilities
        vulnerabilities = self._identify_vulnerabilities(accounts, credentials)
        
        # Generate recommendations
        recommendations = self._generate_security_recommendations(accounts, credentials, vulnerabilities)
        
        # Calculate statistics
        avg_security_score = sum(s.overall_score for s in security_scores) / len(security_scores) if security_scores else 0
        
        vulnerability_counts = {}
        for vuln in vulnerabilities:
            vuln_type = vuln.vulnerability_type
            vulnerability_counts[vuln_type] = vulnerability_counts.get(vuln_type, 0) + 1
        
        severity_distribution = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        for vuln in vulnerabilities:
            severity_distribution[vuln.severity] += 1
        
        return {
            'summary': {
                'total_accounts': len(accounts),
                'total_credentials': len(credentials),
                'average_security_score': avg_security_score,
                'total_vulnerabilities': len(vulnerabilities),
                'critical_vulnerabilities': severity_distribution['critical'],
                'high_vulnerabilities': severity_distribution['high'],
                'recommendations_count': len(recommendations)
            },
            'security_scores': [asdict(score) for score in security_scores],
            'vulnerabilities': [asdict(vuln) for vuln in vulnerabilities],
            'vulnerability_analysis': {
                'by_type': vulnerability_counts,
                'by_severity': severity_distribution,
                'most_common': max(vulnerability_counts.items(), key=lambda x: x[1])[0] if vulnerability_counts else None
            },
            'recommendations': [asdict(rec) for rec in recommendations],
            'security_trends': self._analyze_security_trends(security_scores),
            'compliance_status': self._check_compliance_status(security_scores, vulnerabilities),
            'report_timestamp': datetime.now().isoformat()
        }
    
    def _analyze_security_trends(self, security_scores: List[AccountSecurityScore]) -> Dict[str, Any]:
        """Analyze security trends and patterns"""
        if not security_scores:
            return {}
        
        # Score distribution
        score_ranges = {'0-2': 0, '2-4': 0, '4-6': 0, '6-8': 0, '8-10': 0}
        for score in security_scores:
            if score.overall_score < 2:
                score_ranges['0-2'] += 1
            elif score.overall_score < 4:
                score_ranges['2-4'] += 1
            elif score.overall_score < 6:
                score_ranges['4-6'] += 1
            elif score.overall_score < 8:
                score_ranges['6-8'] += 1
            else:
                score_ranges['8-10'] += 1
        
        # Service-specific analysis
        service_scores = {}
        for score in security_scores:
            if score.service not in service_scores:
                service_scores[score.service] = []
            service_scores[score.service].append(score.overall_score)
        
        service_averages = {}
        for service, scores in service_scores.items():
            service_averages[service] = sum(scores) / len(scores)
        
        # Factor analysis
        factor_averages = {
            'password_strength': sum(s.password_strength for s in security_scores) / len(security_scores),
            'mfa_enabled': sum(1 for s in security_scores if s.mfa_enabled) / len(security_scores) * 10,
            'privacy_settings': sum(s.privacy_settings for s in security_scores) / len(security_scores)
        }
        
        return {
            'score_distribution': score_ranges,
            'service_averages': service_averages,
            'factor_analysis': factor_averages,
            'weakest_factor': min(factor_averages.items(), key=lambda x: x[1])[0],
            'strongest_factor': max(factor_averages.items(), key=lambda x: x[1])[0]
        }
    
    def _check_compliance_status(self, security_scores: List[AccountSecurityScore],
                                vulnerabilities: List[SecurityVulnerability]) -> Dict[str, Any]:
        """Check compliance against security standards"""
        compliance_status = {
            'overall_compliant': True,
            'standards': {
                'password_policy': {'compliant': True, 'issues': []},
                'mfa_policy': {'compliant': True, 'issues': []},
                'session_management': {'compliant': True, 'issues': []},
                'privacy_standards': {'compliant': True, 'issues': []}
            }
        }
        
        benchmarks = self.security_benchmarks
        
        # Check password policy compliance
        weak_passwords = sum(1 for s in security_scores if s.password_strength < benchmarks['password_policy']['complexity_score'])
        if weak_passwords > 0:
            compliance_status['standards']['password_policy']['compliant'] = False
            compliance_status['standards']['password_policy']['issues'].append(f"{weak_passwords} accounts with weak passwords")
            compliance_status['overall_compliant'] = False
        
        # Check MFA compliance
        no_mfa_count = sum(1 for s in security_scores if not s.mfa_enabled)
        if no_mfa_count > 0:
            compliance_status['standards']['mfa_policy']['compliant'] = False
            compliance_status['standards']['mfa_policy']['issues'].append(f"{no_mfa_count} accounts without MFA")
            compliance_status['overall_compliant'] = False
        
        # Check session management
        excessive_sessions = sum(1 for s in security_scores if s.active_sessions > benchmarks['session_security']['concurrent_sessions_limit'])
        if excessive_sessions > 0:
            compliance_status['standards']['session_management']['compliant'] = False
            compliance_status['standards']['session_management']['issues'].append(f"{excessive_sessions} accounts with excessive sessions")
            compliance_status['overall_compliant'] = False
        
        # Check privacy standards
        low_privacy = sum(1 for s in security_scores if s.privacy_settings < 6.0)
        if low_privacy > 0:
            compliance_status['standards']['privacy_standards']['compliant'] = False
            compliance_status['standards']['privacy_standards']['issues'].append(f"{low_privacy} accounts with weak privacy settings")
            compliance_status['overall_compliant'] = False
        
        return compliance_status

def scan_security_audit(accounts: List[Account], credentials: List[Credential], config: Optional[ForensicConfig] = None) -> Dict[str, Any]:
    """Perform comprehensive security audit"""
    auditor = AccountSecurityAuditor(config)
    
    results = {
        'security_scores': [],
        'vulnerabilities': [],
        'recommendations': [],
        'report': {}
    }
    
    # Generate evidence items
    evidence_items = list(auditor.audit_account_security(accounts, credentials))
    
    # Categorize evidence items
    for evidence in evidence_items:
        if evidence.data_type == 'account_security_score':
            results['security_scores'].append(asdict(evidence))
        elif evidence.data_type == 'security_vulnerability':
            results['vulnerabilities'].append(asdict(evidence))
        elif evidence.data_type == 'security_recommendation':
            results['recommendations'].append(asdict(evidence))
    
    # Generate comprehensive report
    results['report'] = auditor.generate_security_report(accounts, credentials)
    
    return results
