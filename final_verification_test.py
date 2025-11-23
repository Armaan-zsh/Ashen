#!/usr/bin/env python3
"""
Final Verification Test - Tests all major components
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all major modules can be imported"""
    print("\n[1] Testing Module Imports...")
    print("-" * 40)
    
    try:
        from digital_forensic_surgeon.dashboard.app import ForensicDashboard, start_dashboard
        print("✓ Dashboard module imported")
    except Exception as e:
        print(f"✗ Dashboard import failed: {e}")
        return False
    
    try:
        from digital_forensic_surgeon.scanners.packet_analyzer import PacketDataAnalyzer
        from digital_forensic_surgeon.scanners.content_classifier import DataContentClassifier
        print("✓ Scanner modules imported")
    except Exception as e:
        print(f"✗ Scanner import failed: {e}")
        return False
    
    try:
        from digital_forensic_surgeon.core.models import EvidenceItem, ForensicResult
        print("✓ Core models imported")
    except Exception as e:
        print(f"✗ Core models import failed: {e}")
        return False
    
    return True

def test_dashboard_initialization():
    """Test dashboard initialization"""
    print("\n[2] Testing Dashboard Initialization...")
    print("-" * 40)
    
    try:
        from digital_forensic_surgeon.dashboard.app import ForensicDashboard
        dashboard = ForensicDashboard()
        print(f"✓ Dashboard initialized")
        print(f"✓ Scanners: {len(dashboard.scanners)} scanners loaded")
        print(f"✓ Scanner types: {', '.join(dashboard.scanners.keys())}")
        return True
    except Exception as e:
        print(f"✗ Dashboard initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_scanners():
    """Test scanner functionality"""
    print("\n[3] Testing Scanners...")
    print("-" * 40)
    
    results = []
    
    try:
        from digital_forensic_surgeon.scanners.packet_analyzer import PacketDataAnalyzer
        pa = PacketDataAnalyzer()
        items = list(pa.scan())[:5]
        print(f"✓ Packet Analyzer: {len(items)} items")
        results.append(True)
    except Exception as e:
        print(f"✗ Packet Analyzer failed: {e}")
        results.append(False)
    
    try:
        from digital_forensic_surgeon.scanners.content_classifier import DataContentClassifier
        cc = DataContentClassifier()
        items = list(cc.scan())[:5]
        print(f"✓ Content Classifier: {len(items)} items")
        results.append(True)
    except Exception as e:
        print(f"✗ Content Classifier failed: {e}")
        results.append(False)
    
    return all(results)

def test_static_files():
    """Test that static files exist"""
    print("\n[4] Testing Static Files...")
    print("-" * 40)
    
    static_dir = project_root / "digital_forensic_surgeon" / "dashboard" / "static"
    script_js = static_dir / "script.js"
    
    if script_js.exists():
        content = script_js.read_text(encoding='utf-8')
        if 'runScan' in content and 'toggleMonitoring' in content:
            print("✓ script.js exists and contains required functions")
            return True
        else:
            print("✗ script.js missing required functions")
            return False
    else:
        print("✗ script.js not found")
        return False

def main():
    print("\n" + "="*60)
    print("FINAL VERIFICATION TEST")
    print("="*60)
    
    results = []
    
    results.append(test_imports())
    results.append(test_dashboard_initialization())
    results.append(test_scanners())
    results.append(test_static_files())
    
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)
    
    passed = sum(results)
    total = len(results)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"\nTests Passed: {passed}/{total} ({percentage:.1f}%)")
    
    if passed == total:
        print("✓ ALL VERIFICATION TESTS PASSED!")
        print("\n✓ Dashboard is ready to use!")
        print("✓ All components are working correctly!")
        return True
    else:
        print(f"✗ {total - passed} test(s) failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

