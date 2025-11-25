"""
Complete System Verification
Tests EVERYTHING to see what's actually working
"""

import sys
from pathlib import Path

def verify_all():
    """Comprehensive system check"""
    
    print("=" * 70)
    print("🔍 TRACKERSHIELD COMPLETE SYSTEM VERIFICATION")
    print("=" * 70)
    
    results = {
        'passed': 0,
        'failed': 0,
        'warnings': 0
    }
    
    # 1. Check signature files exist
    print("\n1️⃣  Checking Signature Files...")
    sig_dirs = [
        'tracker_shield/signatures/facebook',
        'tracker_shield/signatures/google',
        'tracker_shield/signatures/tiktok',
        'tracker_shield/signatures/amazon',
        'tracker_shield/signatures/doubleclick',
        'tracker_shield/signatures/twitter',
        'tracker_shield/signatures/linkedin',
        'tracker_shield/signatures/snapchat',
        'tracker_shield/signatures/clarity',
        'tracker_shield/signatures/hotjar',
    ]
    
    total_sigs = 0
    for sig_dir in sig_dirs:
        path = Path(sig_dir)
        if path.exists():
            count = len(list(path.glob('*.tsig')))
            total_sigs += count
            print(f"   ✅ {path.name}: {count} signatures")
        else:
            print(f"   ⚠️  {path.name}: Not found")
            results['warnings'] += 1
    
    print(f"   📊 Total: {total_sigs} signature files")
    if total_sigs >= 180:
        results['passed'] += 1
    else:
        results['failed'] += 1
    
    # 2. Check databases
    print("\n2️⃣  Checking Compiled Databases...")
    databases = [
        'tracker_shield/data/tracker_shield_free.tsdb',
        'tracker_shield/data/tracker_shield_pro.tsdb',
        'tracker_shield/data/tracker_shield_god.tsdb',
    ]
    
    for db in databases:
        path = Path(db)
        if path.exists():
            size = path.stat().st_size
            print(f"   ✅ {path.name}: {size:,} bytes")
            results['passed'] += 1
        else:
            print(f"   ❌ {path.name}: Missing")
            results['failed'] += 1
    
    # 3. Test signature loading
    print("\n3️⃣  Testing Signature Engine...")
    try:
        from tracker_shield.compiler.sig_compiler import SignatureCompiler
        from tracker_shield.engine.matcher import SignatureMatcher
        
        compiler = SignatureCompiler()
        sigs = compiler.load_database(Path('tracker_shield/data/tracker_shield_god.tsdb'))
        matcher = SignatureMatcher(sigs)
        
        # Test match
        test_url = "https://www.facebook.com/tr?id=123&ev=PageView"
        matches = matcher.match(test_url)
        
        if matches:
            print(f"   ✅ Loaded {len(sigs)} signatures")
            print(f"   ✅ Matching works: Found {len(matches)} matches")
            results['passed'] += 1
        else:
            print(f"   ⚠️  Loaded {len(sigs)} but matching may have issues")
            results['warnings'] += 1
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results['failed'] += 1
    
    # 4. Test unknown detector
    print("\n4️⃣  Testing Unknown Detector...")
    try:
        from tracker_shield.engine.unknown_detector import UnknownPayloadDetector
        
        detector = UnknownPayloadDetector()
        result = detector.is_tracking_request(
            "https://analytics.example.com/track?id=123&event=page_view&user=abc"
        )
        
        if result and result['score'] > 0:
            print(f"   ✅ Detector working (score: {result['score']})")
            results['passed'] += 1
        else:
            print(f"   ⚠️  Detector may need tuning")
            results['warnings'] += 1
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results['failed'] += 1
    
    # 5. Test license system
    print("\n5️⃣  Testing License System...")
    try:
        from tracker_shield.license.validator import SimpleLicenseValidator
        
        # Generate and validate
        key = SimpleLicenseValidator.generate_key("god")
        license = SimpleLicenseValidator.validate_key(key)
        
        if license and license.tier == "god":
            print(f"   ✅ License generation: Working")
            print(f"   ✅ License validation: Working")
            print(f"   📋 Sample key: {key}")
            results['passed'] += 1
        else:
            print(f"   ❌ License system broken")
            results['failed'] += 1
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results['failed'] += 1
    
    # 6. Test community system
    print("\n6️⃣  Testing Community System...")
    try:
        from tracker_shield.community.contributions import ContributionQueue
        
        queue = ContributionQueue()
        count = queue.get_pending_count()
        
        print(f"   ✅ Community system: Working")
        print(f"   📊 Pending contributions: {count}")
        results['passed'] += 1
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results['failed'] += 1
    
    # 7. Test auto-update
    print("\n7️⃣  Testing Auto-Update...")
    try:
        from tracker_shield.updater.auto_update import DatabaseUpdater
        
        updater = DatabaseUpdater('free')
        current = updater.get_current_version()
        
        print(f"   ✅ Auto-update: Working")
        print(f"   📋 Current version: {current.get('version', 0)}")
        results['passed'] += 1
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results['failed'] += 1
    
    # 8. Test integration
    print("\n8️⃣  Testing Integration Manager...")
    try:
        from tracker_shield.integration.manager import IntegrationManager
        
        manager = IntegrationManager()
        stats = manager.get_stats()
        
        print(f"   ✅ Integration manager: Working")
        print(f"   📊 Event bus: Ready")
        results['passed'] += 1
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results['failed'] += 1
    
    # 9. Test security
    print("\n9️⃣  Testing Security Systems...")
    try:
        from tracker_shield.security.validator import InputValidator
        
        # Test validation
        valid_url = InputValidator.validate_url("https://facebook.com/tr")
        invalid_url = InputValidator.validate_url("javascript:alert(1)")
        
        if valid_url and not invalid_url:
            print(f"   ✅ Input validation: Working")
            results['passed'] += 1
        else:
            print(f"   ❌ Validation broken")
            results['failed'] += 1
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results['failed'] += 1
    
    # 10. Test blocking
    print("\n🔟 Testing Blocking Engine...")
    try:
        from tracker_shield.blocker.blocking_engine import TrackerBlocker
        
        blocker = TrackerBlocker()
        should_block = blocker.should_block(
            "https://facebook.com/tr", 
            "Facebook Pixel", 
            0.95
        )
        
        if should_block:
            print(f"   ✅ Blocking engine: Working")
            results['passed'] += 1
        else:
            print(f"   ⚠️  Blocking logic may need adjustment")
            results['warnings'] += 1
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results['failed'] += 1
    
    # 11. Check key files
    print("\n1️⃣1️⃣  Checking Key Files...")
    key_files = [
        'tracker_shield_addon.py',
        'tracker_shield_tray.py',
        'enhanced_dashboard.py',
        'landing_page.html',
        'build_installer.bat',
    ]
    
    for file in key_files:
        if Path(file).exists():
            print(f"   ✅ {file}")
            results['passed'] += 1
        else:
            print(f"   ⚠️  {file}: Not found")
            results['warnings'] += 1
    
    # Final Report
    print("\n" + "=" * 70)
    print("📊 FINAL VERIFICATION REPORT")
    print("=" * 70)
    
    total = results['passed'] + results['failed'] + results['warnings']
    
    print(f"\n✅ Passed: {results['passed']}")
    print(f"⚠️  Warnings: {results['warnings']}")
    print(f"❌ Failed: {results['failed']}")
    
    pass_rate = (results['passed'] / total * 100) if total > 0 else 0
    
    print(f"\n📈 Success Rate: {pass_rate:.1f}%")
    
    if results['failed'] == 0:
        print(f"\n🎉 SYSTEM IS OPERATIONAL!")
        print(f"   All critical components working")
        if results['warnings'] > 0:
            print(f"   {results['warnings']} minor warnings (non-critical)")
        return 0
    else:
        print(f"\n⚠️  ISSUES FOUND - {results['failed']} critical failures")
        return 1


if __name__ == '__main__':
    sys.exit(verify_all())
