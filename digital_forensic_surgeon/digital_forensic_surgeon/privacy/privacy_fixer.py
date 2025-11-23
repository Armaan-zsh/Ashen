"""
Privacy Fixer - Auto-Generate Blocking Rules
Generates blocking rules in multiple formats to block tracked domains
"""

from typing import List, Dict, Set
from datetime import datetime


class PrivacyFixer:
    """Generates blocking rules for various ad blockers and DNS blockers"""
    
    def __init__(self):
        self.blocked_domains = set()
        self.high_risk_domains = set()
        self.all_domains = set()
    
    def analyze_tracking_data(self, tracking_events: List[Dict]) -> Dict[str, Set[str]]:
        """
        Analyze tracking events and categorize domains
        
        Args:
            tracking_events: List of dicts with 'domain', 'risk_score', 'company'
        
        Returns:
            Dict with categorized domain sets
        """
        
        all_domains = set()
        high_risk = set()  # Risk >= 8.0
        medium_risk = set()  # Risk >= 5.0
        low_risk = set()
        
        for event in tracking_events:
            domain = event.get('domain', '').strip()
            risk = event.get('risk_score', 0)
            
            if not domain or domain == 'localhost':
                continue
            
            # Clean domain (remove www., http://, etc.)
            domain = self._clean_domain(domain)
            all_domains.add(domain)
            
            if risk >= 8.0:
                high_risk.add(domain)
            elif risk >= 5.0:
                medium_risk.add(domain)
            else:
                low_risk.add(domain)
        
        self.all_domains = all_domains
        self.high_risk_domains = high_risk
        self.blocked_domains = all_domains  # Default: block everything
        
        return {
            'all': all_domains,
            'high_risk': high_risk,
            'medium_risk': medium_risk,
            'low_risk': low_risk
        }
    
    def _clean_domain(self, domain: str) -> str:
        """Clean and normalize domain"""
        # Remove protocol
        domain = domain.replace('http://', '').replace('https://', '')
        # Remove www.
        if domain.startswith('www.'):
            domain = domain[4:]
        # Remove trailing slash
        domain = domain.rstrip('/')
        # Take only domain part (before /)
        if '/' in domain:
            domain = domain.split('/')[0]
        return domain.lower()
    
    def generate_ublock_origin_rules(self, domains: Set[str] = None) -> str:
        """
        Generate uBlock Origin filter rules
        
        Format: domain.com^$third-party
        """
        if domains is None:
            domains = self.blocked_domains
        
        rules = []
        rules.append("! Digital Forensic Surgeon - Generated Blocking Rules")
        rules.append(f"! Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        rules.append(f"! Total domains: {len(domains)}")
        rules.append("!")
        
        for domain in sorted(domains):
            rules.append(f"||{domain}^$third-party")
        
        return "\n".join(rules)
    
    def generate_adguard_rules(self, domains: Set[str] = None) -> str:
        """
        Generate AdGuard filter rules
        
        Format similar to uBlock but with AdGuard syntax
        """
        if domains is None:
            domains = self.blocked_domains
        
        rules = []
        rules.append("! Digital Forensic Surgeon - AdGuard Rules")
        rules.append(f"! Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        rules.append(f"! Total domains: {len(domains)}")
        rules.append("!")
        
        for domain in sorted(domains):
            rules.append(f"||{domain}^")
        
        return "\n".join(rules)
    
    def generate_dns_blocklist(self, domains: Set[str] = None) -> str:
        """
        Generate DNS blocklist (Pi-hole, AdGuard Home, etc.)
        
        Format: domain.com
        """
        if domains is None:
            domains = self.blocked_domains
        
        rules = []
        rules.append("# Digital Forensic Surgeon - DNS Blocklist")
        rules.append(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        rules.append(f"# Total domains: {len(domains)}")
        rules.append("#")
        
        for domain in sorted(domains):
            rules.append(domain)
        
        return "\n".join(rules)
    
    def generate_hosts_file(self, domains: Set[str] = None) -> str:
        """
        Generate hosts file entries
        
        Format: 0.0.0.0 domain.com
        """
        if domains is None:
            domains = self.blocked_domains
        
        rules = []
        rules.append("# Digital Forensic Surgeon - Hosts File")
        rules.append(f"# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        rules.append(f"# Total domains: {len(domains)}")
        rules.append("#")
        rules.append("# Add these lines to your hosts file:")
        rules.append("# Windows: C:\\Windows\\System32\\drivers\\etc\\hosts")
        rules.append("# Linux/Mac: /etc/hosts")
        rules.append("#")
        
        for domain in sorted(domains):
            rules.append(f"0.0.0.0 {domain}")
            rules.append(f"0.0.0.0 www.{domain}")  # Also block www variant
        
        return "\n".join(rules)
    
    def generate_all_formats(self, risk_level: str = 'all') -> Dict[str, str]:
        """
        Generate blocking rules in all formats
        
        Args:
            risk_level: 'all', 'high', 'medium'
        
        Returns:
            Dict with format name and rules content
        """
        
        # Select domains based on risk level
        if risk_level == 'high':
            domains = self.high_risk_domains
        elif risk_level == 'medium':
            domains = self.high_risk_domains.union(
                {d for d in self.all_domains 
                 if d not in self.high_risk_domains}  # Medium + high
            )
        else:
            domains = self.all_domains
        
        return {
            'ublock_origin': self.generate_ublock_origin_rules(domains),
            'adguard': self.generate_adguard_rules(domains),
            'dns_blocklist': self.generate_dns_blocklist(domains),
            'hosts_file': self.generate_hosts_file(domains)
        }
    
    def get_stats(self) -> Dict[str, int]:
        """Get statistics about blocking"""
        return {
            'total_domains': len(self.all_domains),
            'high_risk': len(self.high_risk_domains),
            'would_block': len(self.blocked_domains)
        }
    
    def generate_summary_report(self) -> str:
        """Generate a summary report"""
        stats = self.get_stats()
        
        report = "\n" + "="*70 + "\n"
        report += "🛡️ PRIVACY FIXER - BLOCKING SUMMARY\n"
        report += "="*70 + "\n\n"
        
        report += f"📊 Total Tracking Domains Found: {stats['total_domains']}\n"
        report += f"⚠️  High-Risk Domains: {stats['high_risk']}\n"
        report += f"🚫 Domains to Block: {stats['would_block']}\n\n"
        
        report += "✅ Generated Blocking Rules:\n"
        report += "  • uBlock Origin filter list\n"
        report += "  • AdGuard filter list\n"
        report += "  • DNS blocklist (Pi-hole/AdGuard Home)\n"
        report += "  • Hosts file entries\n\n"
        
        report += "💡 To use:\n"
        report += "  1. Download the format you need\n"
        report += "  2. Import into your blocker\n"
        report += "  3. Enjoy tracker-free browsing!\n\n"
        
        report += "="*70 + "\n"
        
        return report


def generate_from_database(db_connection, risk_level: str = 'all') -> Dict[str, str]:
    """
    Generate blocking rules from tracking database
    
    Args:
        db_connection: Database connection
        risk_level: 'all', 'high', 'medium'
    
    Returns:
        Dict with all blocking rule formats
    """
    
    fixer = PrivacyFixer()
    
    # Query tracking events
    cursor = db_connection.cursor()
    cursor.execute("""
        SELECT DISTINCT domain, risk_score, company_name
        FROM tracking_events
        WHERE domain IS NOT NULL
    """)
    
    events = []
    for row in cursor.fetchall():
        events.append({
            'domain': row[0],
            'risk_score': row[1],
            'company': row[2]
        })
    
    # Analyze and generate
    fixer.analyze_tracking_data(events)
    rules = fixer.generate_all_formats(risk_level)
    
    # Add summary
    rules['summary'] = fixer.generate_summary_report()
    rules['stats'] = fixer.get_stats()
    
    return rules
