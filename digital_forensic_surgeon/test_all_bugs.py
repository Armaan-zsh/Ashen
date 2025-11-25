"""
Complete System Test - Final Bug Check
Tests all components for robustness
"""

import sys
from pathlib import Path

def test_all_components():
    """Test every component for bugs"""
    
    print("=" * 70)
    print("COMPLETE SYSTEM BUG CHECK")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    # Test 1: Signature Loading
    print("\n1️⃣  Testing Signature Loading...")
    try:
        from tracker_shield.compiler.sig_compiler import SignatureCompiler
        compiler = SignatureCompiler()
        
        for tier in ['free', 'pro', 'god']:
            db_path = Path(f'tracker_shield/data/tracker_shield_{tier}.tsdb')
            sigs = compiler.load_database(db_path)
            print(f"   ✅ {tier}: {len(sigs)} signatures loaded")
        passed += 1
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        failed += 1
    
    # Test 2: Matcher Engine
    print("\n2️⃣  Testing Matcher Engine...")
    try:
        from tracker_shield.engine.matcher import SignatureMatcher
        
        sigs = compiler.load_database(Path('tracker_shield/data/tracker_shield_free.tsdb'))
        matcher = SignatureMatcher(sigs)
        
        # Test match
        matches = matcher.match("https://www.facebook.com/tr?id=123&ev=PageView")
        
        if matches:
            print(f"   ✅ Matcher works: {len(matches)} matches found")
            passed += 1
        else:
            print(f"   ❌ FAILED: No matches for known URL")
            failed += 1
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        failed += 1
    
    # Test 3: License System
    print("\n3️⃣  Testing License System...")
    try:
        from tracker_shield.license.validator import LicenseGenerator, License
        
        # Generate keys
        god_key = LicenseGenerator.generate_key("test@test.com", "god", None)
        pro_key = LicenseGenerator.generate_key("test@test.com", "pro", 12)
        
        # Validate
        god_license = LicenseGenerator.validate_key(god_key)
        pro_license = LicenseGenerator.validate_key(pro_key)
        
        if god_license and pro_license:
            print(f"   ✅ License system works")
            print(f"      God: {god_key[:20]}...")
            print(f"      Pro: {pro_key[:20]}...")
            passed += 1
        else:
            print(f"   ❌ FAILED: License validation broken")
            failed += 1
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        failed += 1
    
    # Test 4: TrackerShield Addon
    print("\n4️⃣  Testing TrackerShield Addon...")
    try:
        from tracker_shield_addon import TrackerShieldAddon
        
        addon = TrackerShieldAddon()
        
        print(f"   ✅ Addon initializes: {len(addon.matcher.signatures)} sigs")
        print(f"      Tier: {addon.tier}")
        passed += 1
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        failed += 1
    
    # Test 5: Database Integrity
    print("\n5️⃣  Testing Database Integrity...")
    try:
        from tracker_shield.compiler.sig_compiler import SignatureCompiler
        
        compiler = SignatureCompiler()
        
        all_valid = True
        for tier in ['free', 'pro', 'god']:
            db_path = Path(f'tracker_shield/data/tracker_shield_{tier}.tsdb')
            sigs = compiler.load_database(db_path)
            
            # Validate structure
            for sig in sigs:
                if not sig.id or not sig.name or not sig.company or not sig.patterns:
                    print(f"   ❌ Invalid signature: {sig.id}")
                    all_valid = False
                    break
        
        if all_valid:
            print(f"   ✅ All databases have valid structure")
            passed += 1
        else:
            failed += 1
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        failed += 1
    
    # Test 6: File Paths
    print("\n6️⃣  Testing Critical File Paths...")
    try:
        critical_files = [
            'tracker_shield/data/tracker_shield_free.tsdb',
            'tracker_shield/data/tracker_shield_pro.tsdb',
            'tracker_shield/data/tracker_shield_god.tsdb',
            'tracker_shield_addon.py',
        ]
        
        missing = []
        for file in critical_files:
            if not Path(file).exists():
                missing.append(file)
        
        if not missing:
            print(f"   ✅ All critical files exist")
            passed += 1
        else:
            print(f"   ❌ FAILED: Missing files: {missing}")
            failed += 1
    except Exception as e:
        print(f"   ❌ FAILED: {e}")
        failed += 1
    
    # Final Report
    print("\n" + "=" * 70)
    print("FINAL REPORT")
    print("=" * 70)
    print(f"\n✅ Passed: {passed}/6")
    print(f"❌ Failed: {failed}/6")
    
    if failed == 0:
        print(f"\n🎉 ALL TESTS PASSED - SYSTEM IS ROBUST!")
        return 0
    else:
        print(f"\n⚠️  {failed} TESTS FAILED - FIX BEFORE CONTINUING")
        return 1

if __name__ == '__main__':
    sys.exit(test_all_components())
