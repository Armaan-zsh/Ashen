"""
Comprehensive End-to-End Test Suite
Tests all TrackerShield components together
"""

import sys
import time
from pathlib import Path

def test_full_system():
    """Test complete TrackerShield system"""
    
    print("=" * 70)
    print("TRACKERSHIELD COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    # Test 1: Signature Loading & Matching
    print("\n1️⃣  Testing Signature System...")
    try:
        from tracker_shield.compiler.sig_compiler import SignatureCompiler
        from tracker_shield.engine.matcher import SignatureMatcher
        
        compiler = SignatureCompiler()
        sigs = compiler.load_database(Path('tracker_shield/data/tracker_shield_god.tsdb'))
        matcher = SignatureMatcher(sigs)
        
        # Test match
        matches = matcher.match("https://www.facebook.com/tr?id=123&ev=PageView")
        
        if matches and len(sigs) >= 180:
            print(f"   ✅ PASS - {len(sigs)} signatures loaded, matching works")
            passed += 1
        else:
            print(f"   ❌ FAIL - Expected 180+ signatures, got {len(sigs)}")
            failed += 1
    except Exception as e:
        print(f"   ❌ FAIL - {e}")
        failed += 1
    
    # Test 2: Unknown Detector
    print("\n2️⃣  Testing Unknown Payload Detector...")
    try:
        from tracker_shield.engine.unknown_detector import UnknownPayloadDetector
        
        detector = UnknownPayloadDetector()
        result = detector.is_tracking_request(
            "https://tracking.newsite.com/pixel?id=123&event=pageview"
        )
        
        if result and result['score'] >= 40:
            print(f"   ✅ PASS - Unknown detector working (score: {result['score']})")
            passed += 1
        else:
            print(f"   ❌ FAIL - Detector didn't catch obvious tracker")
            failed += 1
    except Exception as e:
        print(f"   ❌ FAIL - {e}")
        failed += 1
    
    # Test 3: Community Contributions
    print("\n3️⃣  Testing Community System...")
    try:
        from tracker_shield.community.contributions import ContributionQueue
        
        queue = ContributionQueue()
        hash_id = queue.add_unknown({
            'domain': 'test.com',
            'path': '/track',
            'param_count': 5,
            'score': 65,
            'confidence': 65,
            'reasons': ['test']
        })
        
        if hash_id and queue.get_pending_count() >= 0:
            print(f"   ✅ PASS - Contribution system working")
            passed += 1
        else:
            print(f"   ❌ FAIL - Contribution queue broken")
            failed += 1
    except Exception as e:
        print(f"   ❌ FAIL - {e}")
        failed += 1
    
    # Test 4: Auto-Update
    print("\n4️⃣  Testing Auto-Update System...")
    try:
        from tracker_shield.updater.auto_update import DatabaseUpdater
        
        updater = DatabaseUpdater('god')
        current = updater.get_current_version()
        
        print(f"   ✅ PASS - Update system functional")
        passed += 1
    except Exception as e:
        print(f"   ❌ FAIL - {e}")
        failed += 1
    
    # Test 5: License Validation
    print("\n5️⃣  Testing License System...")
    try:
        from tracker_shield.license.validator import SimpleLicenseValidator
        
        god_key = SimpleLicenseValidator.generate_key("god")
        license = SimpleLicenseValidator.validate_key(god_key)
        
        if license and license.tier == "god":
            print(f"   ✅ PASS - License system working")
            passed += 1
        else:
            print(f"   ❌ FAIL - License validation broken")
            failed += 1
    except Exception as e:
        print(f"   ❌ FAIL - {e}")
        failed += 1
    
    # Test 6: Integration Manager
    print("\n6️⃣  Testing Integration Manager...")
    try:
        from tracker_shield.integration.manager import IntegrationManager
        
        manager = IntegrationManager()
        manager.start()
        
        # Simulate event
        manager.event_bus.publish('tracker_detected', {
            'name': 'Test Tracker',
            'confidence': 100
        })
        
        time.sleep(0.3)
        
        stats = manager.get_stats()
        if stats['trackers_detected'] > 0:
            print(f"   ✅ PASS - Integration manager working")
            passed += 1
        else:
            print(f"   ❌ FAIL - Event bus not working")
            failed += 1
    except Exception as e:
        print(f"   ❌ FAIL - {e}")
        failed += 1
    
    # Test 7: Stress Test (1000 URLs)
    print("\n7️⃣  Stress Testing Matcher (1,000 URLs)...")
    try:
        test_urls = [
            f"https://www.facebook.com/tr?id={i}&ev=PageView" for i in range(500)
        ] + [
            f"https://www.google-analytics.com/g/collect?v=2&en=page_view&tid=G-{i}" for i in range(500)
        ]
        
        start = time.time()
        total_matches = 0
        
        for url in test_urls:
            matches = matcher.match(url)
            total_matches += len(matches)
        
        elapsed = time.time() - start
        throughput = 1000 / elapsed
        
        if elapsed < 1:  # Should process 1000 URLs in under 1 second
            print(f"   ✅ PASS - {throughput:.0f} URLs/sec, {total_matches} matches")
            passed += 1
        else:
            print(f"   ❌ FAIL - Too slow: {elapsed:.2f}s for 1000 URLs")
            failed += 1
    except Exception as e:
        print(f"   ❌ FAIL - {e}")
        failed += 1
    
    # Final Report
    print("\n" + "=" * 70)
    print("FINAL TEST REPORT")
    print("=" * 70)
    print(f"\n✅ Passed: {passed}/7")
    print(f"❌ Failed: {failed}/7")
    
    if failed == 0:
        print(f"\n🎉 ALL SYSTEMS OPERATIONAL - INTEGRATION COMPLETE!")
        return 0
    else:
        print(f"\n⚠️  {failed} tests failed - fix before continuing")
        return 1


if __name__ == '__main__':
    sys.exit(test_full_system())
