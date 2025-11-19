#!/usr/bin/env python3
"""
Test script for Beast Upgrade components
"""

def test_imports():
    """Test if all beast upgrade components can be imported"""
    print("🚀 Testing Beast Upgrade Components...")
    
    try:
        from digital_forensic_surgeon.core.models import EvidenceItem, ScannerType
        print("✅ Core models imported successfully")
    except Exception as e:
        print(f"❌ Core models import failed: {e}")
        return False
    
    components = [
        ("Packet Analyzer", "digital_forensic_surgeon.scanners.packet_analyzer", "PacketDataAnalyzer"),
        ("Content Classifier", "digital_forensic_surgeon.scanners.content_classifier", "DataContentClassifier"),
        ("Destination Intelligence", "digital_forensic_surgeon.scanners.destination_intelligence", "DestinationIntelligence"),
        ("Application Monitor", "digital_forensic_surgeon.scanners.application_monitor", "ApplicationNetworkMonitor"),
        ("Security Auditor", "digital_forensic_surgeon.scanners.security_auditor", "AccountSecurityAuditor"),
        ("Behavioral Intelligence", "digital_forensic_surgeon.scanners.behavioral_intelligence", "BehavioralIntelligenceEngine"),
    ]
    
    success_count = 0
    
    for name, module_path, class_name in components:
        try:
            module = __import__(module_path, fromlist=[class_name])
            scanner_class = getattr(module, class_name)
            
            # Try to instantiate with a simple test
            scanner = scanner_class()
            print(f"✅ {name}: Imported and initialized successfully")
            success_count += 1
            
        except Exception as e:
            print(f"❌ {name}: Error - {str(e)[:100]}...")
    
    print(f"\n📊 Results: {success_count}/{len(components)} components working")
    return success_count == len(components)

def test_dashboard():
    """Test dashboard import"""
    try:
        from digital_forensic_surgeon.dashboard.app import start_dashboard
        print("✅ Dashboard imported successfully")
        return True
    except Exception as e:
        print(f"❌ Dashboard import failed: {str(e)}")
        return False

def test_enhanced_reports():
    """Test enhanced reports import"""
    try:
        from digital_forensic_surgeon.reporting.enhanced_reports import generate_enhanced_report
        print("✅ Enhanced reports imported successfully")
        return True
    except Exception as e:
        print(f"❌ Enhanced reports import failed: {str(e)}")
        return False

def test_cli_commands():
    """Test basic CLI commands"""
    import subprocess
    import sys
    
    commands = [
        ["forensic-surgeon", "--version"],
        ["forensic-surgeon", "--help"],
        ["forensic-surgeon", "--list-services"],
    ]
    
    success_count = 0
    
    for cmd in commands:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"✅ CLI command {' '.join(cmd)}: Success")
                success_count += 1
            else:
                print(f"❌ CLI command {' '.join(cmd)}: Failed with return code {result.returncode}")
        except Exception as e:
            print(f"❌ CLI command {' '.join(cmd)}: Error - {str(e)}")
    
    print(f"📊 CLI Results: {success_count}/{len(commands)} commands working")
    return success_count == len(commands)

def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 DIGITAL FORENSIC SURGEON - BEAST UPGRADE TESTS")
    print("=" * 60)
    
    tests = [
        ("Component Imports", test_imports),
        ("Dashboard", test_dashboard),
        ("Enhanced Reports", test_enhanced_reports),
        ("CLI Commands", test_cli_commands),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n🔍 Running {test_name} Tests...")
        print("-" * 40)
        success = test_func()
        results.append((test_name, success))
    
    print("\n" + "=" * 60)
    print("📋 FINAL TEST RESULTS")
    print("=" * 60)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    total_passed = sum(1 for _, success in results if success)
    total_tests = len(results)
    
    print(f"\n🎯 Overall: {total_passed}/{total_tests} test suites passed")
    
    if total_passed == total_tests:
        print("🎉 ALL TESTS PASSED! Beast upgrade is fully operational!")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
    
    return total_passed == total_tests

if __name__ == "__main__":
    main()
