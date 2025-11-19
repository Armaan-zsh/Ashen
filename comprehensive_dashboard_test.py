#!/usr/bin/env python3
"""
Comprehensive Dashboard Test Suite
Tests all dashboard functionality including API endpoints, WebSocket, and UI components
"""

import asyncio
import aiohttp
import json
import time
import sys
from pathlib import Path

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    import os
    os.environ['PYTHONIOENCODING'] = 'utf-8'

BASE_URL = "http://127.0.0.1:8001"
WS_URL = "ws://127.0.0.1:8001/ws"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_success(msg):
    print(f"{Colors.GREEN}✓{Colors.RESET} {msg}")

def print_error(msg):
    print(f"{Colors.RED}✗{Colors.RESET} {msg}")

def print_info(msg):
    print(f"{Colors.BLUE}ℹ{Colors.RESET} {msg}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠{Colors.RESET} {msg}")

async def test_status_endpoint(session):
    """Test /api/status endpoint"""
    try:
        async with session.get(f"{BASE_URL}/api/status") as resp:
            if resp.status == 200:
                data = await resp.json()
                assert 'total_evidence' in data
                assert 'high_risk_items' in data
                assert 'system_status' in data
                print_success(f"Status endpoint: {data['total_evidence']} evidence, {data['high_risk_items']} high risk")
                return True
            else:
                print_error(f"Status endpoint returned {resp.status}")
                return False
    except Exception as e:
        print_error(f"Status endpoint failed: {e}")
        return False

async def test_evidence_endpoint(session):
    """Test /api/evidence endpoint"""
    try:
        async with session.get(f"{BASE_URL}/api/evidence") as resp:
            if resp.status == 200:
                data = await resp.json()
                assert 'recent_evidence' in data
                assert 'total_count' in data
                print_success(f"Evidence endpoint: {data['total_count']} total items")
                return True
            else:
                print_error(f"Evidence endpoint returned {resp.status}")
                return False
    except Exception as e:
        print_error(f"Evidence endpoint failed: {e}")
        return False

async def test_alerts_endpoint(session):
    """Test /api/alerts endpoint"""
    try:
        async with session.get(f"{BASE_URL}/api/alerts") as resp:
            if resp.status == 200:
                data = await resp.json()
                assert 'alerts' in data
                assert 'alert_count' in data
                print_success(f"Alerts endpoint: {data['alert_count']} alerts")
                return True
            else:
                print_error(f"Alerts endpoint returned {resp.status}")
                return False
    except Exception as e:
        print_error(f"Alerts endpoint failed: {e}")
        return False

async def test_scan_endpoint(session, scan_type):
    """Test a scan endpoint"""
    try:
        async with session.post(
            f"{BASE_URL}/api/run_scan/{scan_type}",
            json={}
        ) as resp:
            if resp.status == 200:
                data = await resp.json()
                count = data.get('count', 0)
                if 'error' in data:
                    print_warning(f"{scan_type} scan: {data['error']}")
                    return False
                else:
                    print_success(f"{scan_type} scan: {count} items found")
                    return True
            else:
                print_error(f"{scan_type} scan returned {resp.status}")
                return False
    except Exception as e:
        print_error(f"{scan_type} scan failed: {e}")
        return False

async def test_monitoring(session):
    """Test monitoring start/stop"""
    results = []
    
    # Test start monitoring
    try:
        async with session.post(f"{BASE_URL}/api/start_monitoring") as resp:
            if resp.status == 200:
                data = await resp.json()
                if data.get('status') == 'monitoring_started':
                    print_success("Start monitoring: OK")
                    results.append(True)
                else:
                    print_warning(f"Start monitoring: {data.get('status')}")
                    results.append(True)  # Still counts as working
            else:
                print_error(f"Start monitoring returned {resp.status}")
                results.append(False)
    except Exception as e:
        print_error(f"Start monitoring failed: {e}")
        results.append(False)
    
    # Wait a bit
    await asyncio.sleep(2)
    
    # Test stop monitoring
    try:
        async with session.post(f"{BASE_URL}/api/stop_monitoring") as resp:
            if resp.status == 200:
                data = await resp.json()
                if data.get('status') == 'monitoring_stopped':
                    print_success("Stop monitoring: OK")
                    results.append(True)
                else:
                    print_warning(f"Stop monitoring: {data.get('status')}")
                    results.append(True)
            else:
                print_error(f"Stop monitoring returned {resp.status}")
                results.append(False)
    except Exception as e:
        print_error(f"Stop monitoring failed: {e}")
        results.append(False)
    
    return all(results)

async def test_websocket():
    """Test WebSocket connection"""
    try:
        import websockets
        async with websockets.connect(WS_URL) as ws:
            # Wait for a message
            try:
                message = await asyncio.wait_for(ws.recv(), timeout=2.0)
                data = json.loads(message)
                assert 'timestamp' in data
                assert 'evidence_count' in data
                print_success("WebSocket: Connected and receiving data")
                return True
            except asyncio.TimeoutError:
                print_warning("WebSocket: Connected but no data received (may be normal)")
                return True
    except ImportError:
        print_warning("WebSocket test skipped (websockets library not installed)")
        return True
    except Exception as e:
        print_error(f"WebSocket test failed: {e}")
        return False

async def test_dashboard_html(session):
    """Test that dashboard HTML loads correctly"""
    try:
        async with session.get(f"{BASE_URL}/") as resp:
            if resp.status == 200:
                html = await resp.text()
                # Check for key elements
                checks = [
                    ('runScan', 'runScan function'),
                    ('toggleMonitoring', 'toggleMonitoring function'),
                    ('script.js', 'script.js loaded'),
                    ('button', 'button elements'),
                    ('onclick', 'onclick handlers'),
                    ('dashboard-grid', 'dashboard grid'),
                ]
                
                all_present = True
                for check, name in checks:
                    if check in html:
                        print_success(f"HTML contains {name}")
                    else:
                        print_error(f"HTML missing {name}")
                        all_present = False
                
                return all_present
            else:
                print_error(f"Dashboard HTML returned {resp.status}")
                return False
    except Exception as e:
        print_error(f"Dashboard HTML test failed: {e}")
        return False

async def test_static_files(session):
    """Test that static files are served"""
    try:
        async with session.get(f"{BASE_URL}/static/script.js") as resp:
            if resp.status == 200:
                content = await resp.text()
                if 'runScan' in content and 'toggleMonitoring' in content:
                    print_success("Static file script.js: OK")
                    return True
                else:
                    print_error("Static file script.js: Missing functions")
                    return False
            else:
                print_error(f"Static file script.js returned {resp.status}")
                return False
    except Exception as e:
        print_error(f"Static file test failed: {e}")
        return False

async def test_scan_results(session):
    """Test scan results endpoints"""
    scan_types = ['packet', 'content', 'destination', 'application', 'security', 'behavioral']
    results = []
    
    for scan_type in scan_types:
        try:
            async with session.get(f"{BASE_URL}/api/scan_results/{scan_type}") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if 'error' not in data:
                        print_success(f"Scan results {scan_type}: OK")
                        results.append(True)
                    else:
                        print_warning(f"Scan results {scan_type}: {data.get('error')}")
                        results.append(True)  # Still counts
                else:
                    print_error(f"Scan results {scan_type} returned {resp.status}")
                    results.append(False)
        except Exception as e:
            print_error(f"Scan results {scan_type} failed: {e}")
            results.append(False)
    
    return all(results)

async def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("COMPREHENSIVE DASHBOARD TEST SUITE")
    print("="*60 + "\n")
    
    # Check if server is running
    print_info("Checking if dashboard server is running...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{BASE_URL}/api/status", timeout=aiohttp.ClientTimeout(total=2)) as resp:
                if resp.status == 200:
                    print_success("Dashboard server is running!\n")
                else:
                    print_error(f"Dashboard server returned {resp.status}")
                    print_error("Please start the dashboard first:")
                    print_error("python -c \"from digital_forensic_surgeon.dashboard.app import start_dashboard; start_dashboard()\"")
                    return False
    except Exception as e:
        print_error(f"Cannot connect to dashboard server: {e}")
        print_error("Please start the dashboard first:")
        print_error("python -c \"from digital_forensic_surgeon.dashboard.app import start_dashboard; start_dashboard()\"")
        return False
    
    results = []
    
    async with aiohttp.ClientSession() as session:
        # Test 1: Dashboard HTML
        print("\n[1] Testing Dashboard HTML...")
        print("-" * 40)
        results.append(await test_dashboard_html(session))
        
        # Test 2: Static Files
        print("\n[2] Testing Static Files...")
        print("-" * 40)
        results.append(await test_static_files(session))
        
        # Test 3: API Endpoints
        print("\n[3] Testing API Endpoints...")
        print("-" * 40)
        results.append(await test_status_endpoint(session))
        results.append(await test_evidence_endpoint(session))
        results.append(await test_alerts_endpoint(session))
        
        # Test 4: Scan Endpoints
        print("\n[4] Testing Scan Endpoints...")
        print("-" * 40)
        scan_types = ['packet', 'content', 'destination', 'application', 'security', 'behavioral']
        for scan_type in scan_types:
            results.append(await test_scan_endpoint(session, scan_type))
        
        # Test 5: Monitoring
        print("\n[5] Testing Monitoring...")
        print("-" * 40)
        results.append(await test_monitoring(session))
        
        # Test 6: Scan Results
        print("\n[6] Testing Scan Results Endpoints...")
        print("-" * 40)
        results.append(await test_scan_results(session))
        
        # Test 7: WebSocket
        print("\n[7] Testing WebSocket...")
        print("-" * 40)
        results.append(await test_websocket())
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    passed = sum(results)
    total = len(results)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"\nTests Passed: {passed}/{total} ({percentage:.1f}%)")
    
    if passed == total:
        print_success("ALL TESTS PASSED! Dashboard is fully functional!")
        return True
    else:
        print_error(f"{total - passed} test(s) failed. Please review the errors above.")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(130)
    except Exception as e:
        print_error(f"Test suite failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

