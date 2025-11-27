"""
DNS Blocker - System-Wide Ad & Tracker Blocking
Uses DNS interception to block ads at the source
"""

import socket
from dnslib import DNSRecord, DNSHeader, RR, QTYPE, A
from dnslib.server import DNSServer, BaseResolver
import threading
from colorama import Fore, init

init(autoreset=True)

class BlockingResolver(BaseResolver):
    """DNS resolver that blocks ad/tracker domains"""
    
    def __init__(self, blocklist_file=None):
        # Load blocklist
        self.blocklist = set()
        self.load_blocklist()
        
        # Stats
        self.stats = {
            'total': 0,
            'blocked': 0,
            'allowed': 0
        }
        
        # Upstream DNS (for allowed domains)
        self.upstream_dns = '1.1.1.1'  # Cloudflare DNS
        
        print(f"{Fore.GREEN}✅ DNS Blocker loaded {len(self.blocklist)} domains")
    
    def load_blocklist(self):
        """Load ad/tracker domains to block"""
        # Top ad/tracker domains
        domains = [
            # Google Ads
            'googleadservices.com',
            'googlesyndication.com',
            'doubleclick.net',
            'google-analytics.com',
            'googletagmanager.com',
            
            # Facebook
            'facebook.com',
            'connect.facebook.net',
            'fbcdn.net',
            
            # Microsoft
            'ads.microsoft.com',
            'telemetry.microsoft.com',
            
            # General ads
            'adservice.google.com',
            'pagead2.googlesyndication.com',
            
            # Analytics
            'hotjar.com',
            'clarity.ms',
            'mixpanel.com',
            'segment.com',
            
            # Add more...
        ]
        
        for domain in domains:
            self.blocklist.add(domain.lower())
    
    def is_blocked(self, domain):
        """Check if domain should be blocked"""
        domain = domain.lower().rstrip('.')
        
        # Check exact match
        if domain in self.blocklist:
            return True
        
        # Check subdomains
        parts = domain.split('.')
        for i in range(len(parts)):
            parent = '.'.join(parts[i:])
            if parent in self.blocklist:
                return True
        
        return False
    
    def resolve(self, request, handler):
        """Resolve DNS request (block or forward)"""
        try:
            qname = str(request.q.qname)
            self.stats['total'] += 1
            
            # Check if blocked
            if self.is_blocked(qname):
                self.stats['blocked'] += 1
                print(f"{Fore.RED}🚫 BLOCKED: {qname}")
                
                # Return 0.0.0.0 (blocked)
                reply = request.reply()
                reply.add_answer(RR(qname, QTYPE.A, rdata=A("0.0.0.0"), ttl=60))
                return reply
            
            else:
                self.stats['allowed'] += 1
                
                # Forward to upstream DNS
                upstream_query = request.send(self.upstream_dns, 53, tcp=False)
                reply = DNSRecord.parse(upstream_query)
                
                # Print stats every 50 queries
                if self.stats['total'] % 50 == 0:
                    self.print_stats()
                
                return reply
        
        except Exception as e:
            print(f"{Fore.YELLOW}⚠️ Error: {e}")
            # Return empty response on error
            return request.reply()
    
    def print_stats(self):
        """Print blocking statistics"""
        print(f"\n{Fore.CYAN}📊 Stats: {self.stats['total']} queries | "
              f"{Fore.RED}{self.stats['blocked']} blocked | "
              f"{Fore.GREEN}{self.stats['allowed']} allowed\n")


def start_dns_server():
    """Start DNS server on port 53"""
    resolver = BlockingResolver()
    server = DNSServer(resolver, port=53, address='127.0.0.1')
    
    print(f"{Fore.GREEN}🚀 DNS Server starting on 127.0.0.1:53")
    print(f"{Fore.CYAN}📡 Change your DNS to 127.0.0.1 to use this blocker\n")
    
    try:
        server.start_thread()
        
        # Keep running
        while True:
            import time
            time.sleep(1)
    
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⏹️  Stopping DNS server...")
        resolver.print_stats()
        print(f"{Fore.GREEN}✅ Shutdown complete")


if __name__ == '__main__':
    start_dns_server()
