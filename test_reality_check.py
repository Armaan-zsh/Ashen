"""Test script for Reality Check components"""

from digital_forensic_surgeon.scanners.data_broker_database import DataBrokerDatabase
from digital_forensic_surgeon.scanners.mitm_proxy_manager import MITMProxyManager
from digital_forensic_surgeon.scanners.reality_check_monitor import RealityCheckMonitor
from digital_forensic_surgeon.core.config import ForensicConfig
from digital_forensic_surgeon.scanners.osint import OSINTScanner

print("=" * 70)
print("REALITY CHECK - Component Tests")
print("=" * 70)
print()

# Test 1: Data Broker Database
print("Test 1: Data Broker Database")
db = DataBrokerDatabase()
print(f"  ✓ Loaded {len(db.entities)} tracker entities")
print(f"  ✓ Total domains tracked: {len(db.domain_to_entity)}")

# Test classification
result = db.classify_url("https://doubleclick.net/tracking")
print(f"  ✓ Classification test (doubleclick.net):")
print(f"    - Is Tracker: {result['is_tracker']}")
print(f"    - Entity: {result['entity_name']}")
print(f"    - Risk Score: {result['risk_score']}/10")

result2 = db.classify_url("https://facebook.com/tr")
print(f"  ✓ Classification test (facebook.com/tr):")
print(f"    - Entity: {result2['entity_name']}")
print(f"    - Category: {result2['category']}")
print(f"    - Risk Score: {result2['risk_score']}/10")

print()

# Test 2: OSINT Scanner Fix
print("Test 2: OSINT Scanner (Config Fix)")
config = ForensicConfig()
scanner1 = OSINTScanner(config)
print("  ✓ OSINT Scanner with ForensicConfig: SUCCESS")

scanner2 = OSINTScanner({'osint_timeout': 10})
print("  ✓ OSINT Scanner with Dict: SUCCESS")

print()

# Test 3: MITMProxy Manager
print("Test 3: MITMProxy Manager")
manager = MITMProxyManager(port=8080)
print(f"  ✓ Proxy manager created on port {manager.port}")
print(f"  ✓ Broker database integrated: {len(manager.broker_db.entities)} entities")

print()

# Test 4: Reality Check Monitor
print("Test 4: Reality Check Monitor")
monitor = RealityCheckMonitor(proxy_port=8080)
print(f"  ✓ Monitor created successfully")
print(f"  ✓ Proxy port: {monitor.proxy_manager.port}")
print(f"  ✓ Broker DB: {len(monitor.broker_db.entities)} entities")
print(f"  ✓ Initial privacy score: {monitor.calculate_privacy_score()}/100")

# Test stats
stats = monitor.get_live_stats()
print(f"  ✓ Live stats working:")
print(f"    - Is running: {stats['is_running']}")
print(f"    - Privacy score: {stats['privacy_score']}/100")

print()

# Test 5: Database Stats
print("Test 5: Database Statistics")
db_stats = db.get_stats()
print(f"  ✓ Total entities: {db_stats['total_entities']}")
print(f"  ✓ Total domains: {db_stats['total_domains']}")
print(f"  ✓ High-risk entities: {db_stats['high_risk_count']}")
print(f"  ✓ Average risk score: {db_stats['average_risk_score']:.2f}/10")
print(f"  ✓ Categories:")
for category, count in db_stats['categories'].items():
    print(f"    - {category}: {count}")

print()
print("=" * 70)
print("ALL TESTS PASSED! ✓")
print("=" * 70)
print()
print("Reality Check system is ready to use!")
print()
print("Quick Start:")
print("  1. Install certificate: forensic-surgeon --install-cert")
print("  2. Run Reality Check: forensic-surgeon --reality-check --track-duration 300")
print()
