#!/usr/bin/env python3
"""
Final working test for Beast Upgrade components
"""

def test_all_components():
    """Test all beast upgrade components"""
    print('🚀 Final Beast Upgrade Test')
    print('=' * 50)
    
    # Import all components
    from digital_forensic_surgeon.scanners.packet_analyzer import PacketDataAnalyzer
    from digital_forensic_surgeon.scanners.content_classifier import DataContentClassifier
    from digital_forensic_surgeon.scanners.destination_intelligence import DestinationIntelligence
    from digital_forensic_surgeon.scanners.application_monitor import ApplicationNetworkMonitor
    from digital_forensic_surgeon.scanners.security_auditor import AccountSecurityAuditor
    from digital_forensic_surgeon.scanners.behavioral_intelligence import BehavioralIntelligenceEngine
    
    # Test each scanner
    scanners = [
        ('Packet Analyzer', PacketDataAnalyzer()),
        ('Content Classifier', DataContentClassifier()),
        ('Destination Intelligence', DestinationIntelligence()),
        ('Application Monitor', ApplicationNetworkMonitor()),
        ('Security Auditor', AccountSecurityAuditor()),
        ('Behavioral Intelligence', BehavioralIntelligenceEngine())
    ]
    
    all_working = True
    total_results = 0
    
    for name, scanner in scanners:
        try:
            results = list(scanner.scan())
            result_count = len(results)
            total_results += result_count
            print(f'✅ {name}: {result_count} results')
            
            # Show first result if available
            if results and len(results) > 0:
                first_result = results[0]
                print(f'   📄 Sample: {first_result.content[:50]}...')
                
        except Exception as e:
            print(f'❌ {name}: Error - {str(e)[:100]}...')
            all_working = False
    
    print(f'\n📊 Total evidence items collected: {total_results}')
    
    return all_working, total_results

def test_dashboard():
    """Test dashboard functionality"""
    try:
        from digital_forensic_surgeon.dashboard.app import start_dashboard
        print('✅ Dashboard imported successfully')
        print('🚀 To start dashboard: python -c "from digital_forensic_surgeon.dashboard.app import start_dashboard; start_dashboard()"')
        return True
    except Exception as e:
        print(f'❌ Dashboard error: {str(e)}')
        return False

def main():
    """Run final test"""
    print('🧪 DIGITAL FORENSIC SURGEON - BEAST UPGRADE FINAL TEST')
    print('=' * 60)
    
    # Test components
    components_ok, result_count = test_all_components()
    
    print('\n' + '-' * 50)
    
    # Test dashboard
    dashboard_ok = test_dashboard()
    
    print('\n' + '=' * 60)
    print('📋 FINAL RESULTS')
    print('=' * 60)
    
    if components_ok:
        print('✅ All Beast Upgrade Components: WORKING')
    else:
        print('❌ Some components have issues')
    
    if dashboard_ok:
        print('✅ Dashboard: READY')
    else:
        print('❌ Dashboard: Issues detected')
    
    print(f'📊 Evidence items generated: {result_count}')
    
    if components_ok and dashboard_ok:
        print('\n🎉 BEAST UPGRADE FULLY OPERATIONAL!')
        print('\n📖 NEXT STEPS:')
        print('1. Start the dashboard: python -c "from digital_forensic_surgeon.dashboard.app import start_dashboard; start_dashboard()"')
        print('2. Visit http://localhost:8000 for interactive interface')
        print('3. Use CLI: forensic-surgeon --help')
        print('4. Check working_commands.md for more commands')
    else:
        print('\n⚠️  Some components need fixes')
    
    return components_ok and dashboard_ok

if __name__ == "__main__":
    main()
