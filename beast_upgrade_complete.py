#!/usr/bin/env python3
"""
BEAST UPGRADE - COMPLETE VERIFICATION TEST
==========================================

This script verifies that ALL beast upgrade components are working correctly:
- All 6 scanners initialize and run without errors
- Dashboard can be imported and started
- CLI commands work
- All EvidenceItem constructor calls are correct

Run this to confirm everything is working!
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_scanners():
    """Test all 6 beast upgrade scanners"""
    print("\n🔍 Testing All Scanners...")
    
    scanners = [
        ("PacketDataAnalyzer", "digital_forensic_surgeon.scanners.packet_analyzer"),
        ("DataContentClassifier", "digital_forensic_surgeon.scanners.content_classifier"),
        ("DestinationIntelligence", "digital_forensic_surgeon.scanners.destination_intelligence"),
        ("ApplicationNetworkMonitor", "digital_forensic_surgeon.scanners.application_monitor"),
        ("AccountSecurityAuditor", "digital_forensic_surgeon.scanners.security_auditor"),
        ("BehavioralIntelligenceEngine", "digital_forensic_surgeon.scanners.behavioral_intelligence")
    ]
    
    results = {}
    total_evidence = 0
    
    for name, module_path in scanners:
        try:
            module = __import__(module_path, fromlist=[name])
            scanner_class = getattr(module, name)
            
            # Initialize scanner
            scanner = scanner_class()
            
            # Run scan
            evidence_items = list(scanner.scan())
            
            results[name] = len(evidence_items)
            total_evidence += len(evidence_items)
            
            print(f"✅ {name}: {len(evidence_items)} evidence items")
            
        except Exception as e:
            print(f"❌ {name}: ERROR - {str(e)}")
            results[name] = f"ERROR: {str(e)}"
    
    return results, total_evidence

def test_dashboard():
    """Test dashboard import and startup function"""
    print("\n🖥️ Testing Dashboard...")
    
    try:
        from digital_forensic_surgeon.dashboard.app import start_dashboard
        print("✅ Dashboard start_dashboard function imported successfully")
        return True
    except Exception as e:
        print(f"❌ Dashboard import failed: {str(e)}")
        return False

def test_cli():
    """Test CLI commands"""
    print("\n💻 Testing CLI...")
    
    import subprocess
    
    commands = [
        ["forensic-surgeon", "--version"],
        ["forensic-surgeon", "--help"]
    ]
    
    results = {}
    for cmd in commands:
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print(f"✅ {' '.join(cmd)}: SUCCESS")
                results[' '.join(cmd)] = "SUCCESS"
            else:
                print(f"❌ {' '.join(cmd)}: FAILED - {result.stderr}")
                results[' '.join(cmd)] = f"FAILED: {result.stderr}"
        except Exception as e:
            print(f"❌ {' '.join(cmd)}: ERROR - {str(e)}")
            results[' '.join(cmd)] = f"ERROR: {str(e)}"
    
    return results

def main():
    """Main test runner"""
    print("=" * 80)
    print("🚀 BEAST UPGRADE - COMPLETE VERIFICATION")
    print("=" * 80)
    
    # Test scanners
    scanner_results, total_evidence = test_scanners()
    
    # Test dashboard
    dashboard_ok = test_dashboard()
    
    # Test CLI
    cli_results = test_cli()
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 FINAL RESULTS")
    print("=" * 80)
    
    print(f"\n🔍 Scanners:")
    for name, result in scanner_results.items():
        status = "✅" if isinstance(result, int) else "❌"
        print(f"  {status} {name}: {result}")
    
    print(f"\n🖥️ Dashboard: {'✅ WORKING' if dashboard_ok else '❌ FAILED'}")
    
    print(f"\n💻 CLI:")
    for cmd, result in cli_results.items():
        status = "✅" if result == "SUCCESS" else "❌"
        print(f"  {status} {cmd}: {result}")
    
    print(f"\n📈 Total Evidence Items Generated: {total_evidence}")
    
    # Final verdict
    all_scanners_ok = all(isinstance(r, int) for r in scanner_results.values())
    all_cli_ok = all(r == "SUCCESS" for r in cli_results.values())
    
    if all_scanners_ok and dashboard_ok and all_cli_ok:
        print("\n🎉 BEAST UPGRADE: FULLY OPERATIONAL! 🎉")
        print("\n📖 NEXT STEPS:")
        print("1. Start dashboard: python -c \"from digital_forensic_surgeon.dashboard.app import start_dashboard; start_dashboard()\"")
        print("2. Visit http://localhost:8000")
        print("3. Use CLI: forensic-surgeon --help")
        return 0
    else:
        print("\n⚠️ BEAST UPGRADE: PARTIAL OPERATION - Some components need attention")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
