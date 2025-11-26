"""
Network Packet Interceptor
Uses WinDivert to intercept ALL network traffic
"""

import socket
import struct
from colorama import Fore, Style, init

# Initialize colorama for colored output
init(autoreset=True)

try:
    from pydivert import WinDivert
    WINDIVERT_AVAILABLE = True
except ImportError:
    WINDIVERT_AVAILABLE = False
    print(f"{Fore.RED}⚠️ WinDivert not installed. Run: pip install pydivert")

class PacketInterceptor:
    def __init__(self, tracker_db):
        self.tracker_db = tracker_db
        self.stats = {
            'total': 0,
            'blocked': 0,
            'allowed': 0
        }
    
    def get_domain_from_ip(self, ip):
        """Try to get domain from IP (reverse DNS)"""
        try:
            domain = socket.gethostbyaddr(ip)[0]
            return domain
        except:
            return ip
    
    def should_block(self, dst_ip):
        """Determine if packet should be blocked"""
        # Get domain from IP
        domain = self.get_domain_from_ip(dst_ip)
        
        # Check if it's a tracker
        return self.tracker_db.is_tracker(domain), domain
    
    def start(self):
        """Start intercepting packets"""
        if not WINDIVERT_AVAILABLE:
            print(f"{Fore.RED}❌ Cannot start: WinDivert not available")
            return
        
        print(f"{Fore.GREEN}🛡️ PrivacyShield Network Filter Starting...")
        print(f"{Fore.YELLOW}⚠️ Running as Administrator required!")
        print(f"{Fore.CYAN}📡 Intercepting ALL network traffic...\n")
        
        # Filter: TCP traffic on ports 80 and 443 (HTTP/HTTPS)
        # We can expand this to all traffic later
        filter_str = "tcp.DstPort == 80 or tcp.DstPort == 443"
        
        try:
            with WinDivert(filter_str) as w:
                print(f"{Fore.GREEN}✅ WinDivert started successfully!")
                print(f"{Fore.CYAN}Monitoring HTTP/HTTPS traffic...\n")
                
                for packet in w:
                    self.stats['total'] += 1
                    
                    # Extract destination IP
                    if hasattr(packet, 'dst_addr'):
                        dst_ip = packet.dst_addr
                        
                        # Check if should block
                        should_block, domain = self.should_block(dst_ip)
                        
                        if should_block:
                            self.stats['blocked'] += 1
                            print(f"{Fore.RED}🚫 BLOCKED: {domain} ({dst_ip})")
                            # Don't forward packet (DROP it)
                            continue
                        else:
                            self.stats['allowed'] += 1
                            # Allow packet
                            w.send(packet)
                            
                        # Print stats every 100 packets
                        if self.stats['total'] % 100 == 0:
                            self.print_stats()
                    else:
                        # Forward packet if no dst_addr
                        w.send(packet)
        
        except PermissionError:
            print(f"{Fore.RED}❌ ERROR: Administrator privileges required!")
            print(f"{Fore.YELLOW}   Run as Administrator to use network filtering")
        except Exception as e:
            print(f"{Fore.RED}❌ ERROR: {e}")
            print(f"{Fore.YELLOW}   Make sure WinDivert is properly installed")
    
    def print_stats(self):
        """Print statistics"""
        print(f"\n{Fore.CYAN}📊 Stats: {self.stats['total']} total | "
              f"{Fore.RED}{self.stats['blocked']} blocked | "
              f"{Fore.GREEN}{self.stats['allowed']} allowed\n")
