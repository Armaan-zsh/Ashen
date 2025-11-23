import asyncio
import os
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.append(str(Path.cwd()))

from digital_forensic_surgeon.core.config import get_config
from digital_forensic_surgeon.db.manager import DatabaseManager
from digital_forensic_surgeon.scanners.packet_analyzer import PacketDataAnalyzer
from digital_forensic_surgeon.scanners.osint import OSINTScanner
from digital_forensic_surgeon.scanners.network.wifi import WiFiScanner

async def verify_db_persistence():
    print("\n--- Verifying Database Persistence ---")
    config = get_config()
    db = DatabaseManager(config.db_path)
    
    # Check if evidence table exists
    try:
        with db.get_connection() as conn:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='evidence'")
            if cursor.fetchone():
                print("[OK] Evidence table exists.")
            else:
                print("[FAIL] Evidence table MISSING.")
                
        # Add test evidence
        test_evidence = {
            'id': f"test_{int(datetime.now().timestamp())}",
            'source': 'verification_script',
            'type': 'test',
            'content': 'Test evidence persistence',
            'metadata': {'test': True},
            'severity': 'info'
        }
        db.add_evidence(test_evidence)
        print("[OK] Added test evidence.")
        
        # Retrieve evidence
        recent = db.get_recent_evidence(limit=10)
        found = any(e['id'] == test_evidence['id'] for e in recent)
        if found:
            print("[OK] Retrieved test evidence from DB.")
        else:
            print("[FAIL] Failed to retrieve test evidence.")
            
    except Exception as e:
        print(f"[FAIL] Database verification failed: {e}")

async def verify_packet_analyzer():
    print("\n--- Verifying Packet Analyzer (Background Daemon) ---")
    config = get_config()
    analyzer = PacketDataAnalyzer(config)
    
    try:
        analyzer.start_monitoring()
        print("[OK] Started packet monitoring daemon.")
        
        # Wait a bit
        await asyncio.sleep(2)
        
        if analyzer.is_monitoring:
            print("[OK] Monitoring is active.")
        else:
            print("[FAIL] Monitoring is NOT active.")
            
        analyzer.stop_monitoring()
        print("[OK] Stopped packet monitoring.")
        
    except Exception as e:
        print(f"[FAIL] Packet analyzer verification failed: {e}")

async def verify_osint_async():
    print("\n--- Verifying OSINT Scanner (Async) ---")
    config = get_config()
    scanner = OSINTScanner(config)
    
    try:
        # Test with a dummy username
        username = "test_user_123_xyz"
        print(f"Scanning for {username}...")
        
        # This should be fast and non-blocking
        start_time = datetime.now()
        results = await scanner.scan_username_async(username)
        duration = (datetime.now() - start_time).total_seconds()
        
        print(f"[OK] Scan completed in {duration:.2f} seconds.")
        print(f"Found {len(results)} results (expected 0 or few for dummy user).")
        
    except Exception as e:
        print(f"[FAIL] OSINT verification failed: {e}")

async def verify_wifi_geolocation():
    print("\n--- Verifying WiFi Geolocation ---")
    config = get_config()
    scanner = WiFiScanner(config)
    
    try:
        # Mock resolve_geolocation since we might not have a real API key or WiFi
        # But we can check if the method exists and runs without error
        results = scanner.resolve_geolocation(wigle_api_key="dummy_key")
        print(f"[OK] resolve_geolocation executed. Result count: {len(results)}")
        
    except Exception as e:
        print(f"[FAIL] WiFi verification failed: {e}")

async def main():
    await verify_db_persistence()
    await verify_packet_analyzer()
    await verify_osint_async()
    await verify_wifi_geolocation()

if __name__ == "__main__":
    asyncio.run(main())
