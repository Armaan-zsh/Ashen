"""
PrivacyShield OS - Main Entry Point
Network-level tracker blocker
"""

import sys
import os
from colorama import Fore, Style, init

# Add network_filter to path
sys.path.insert(0, os.path.dirname(__file__))

from network_filter.tracker_db import TrackerDB
from network_filter.packet_interceptor import PacketInterceptor

init(autoreset=True)

def print_banner():
    banner = f"""
{Fore.RED}╔════════════════════════════════════════╗
║  {Fore.WHITE}🛡️  PRIVACYSHIELD OS - WEEK 1{Fore.RED}      ║
║  {Fore.CYAN}Network-Level Tracker Blocker{Fore.RED}       ║
╚════════════════════════════════════════╝{Style.RESET_ALL}
"""
    print(banner)

def check_admin():
    """Check if running as administrator"""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def main():
    print_banner()
    
    # Check admin privileges
    if not check_admin():
        print(f"{Fore.RED}❌ ERROR: Administrator privileges required!")
        print(f"{Fore.YELLOW}   Right-click and 'Run as Administrator'\n")
        input("Press Enter to exit...")
        sys.exit(1)
    
    print(f"{Fore.GREEN}✅ Running as Administrator")
    
    # Load tracker database
    print(f"{Fore.CYAN}📚 Loading tracker database...")
    tracker_db = TrackerDB()
    
    # Create packet interceptor
    interceptor = PacketInterceptor(tracker_db)
    
    # Start filtering
    print(f"{Fore.GREEN}🚀 Starting network filter...\n")
    
    try:
        interceptor.start()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}⏹️  Stopping PrivacyShield...")
        print(f"{Fore.CYAN}Final Stats:")
        interceptor.print_stats()
        print(f"{Fore.GREEN}✅ Shutdown complete\n")

if __name__ == '__main__':
    main()
