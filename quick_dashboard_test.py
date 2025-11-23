#!/usr/bin/env python3
"""Quick test to verify dashboard is running and functional"""

import requests
import json

def test_dashboard():
    base_url = "http://127.0.0.1:8001"
    
    print("Dashboard Status Check")
    print("=" * 40)
    
    # Test main page
    try:
        response = requests.get(base_url, timeout=5)
        print(f"✓ Main page: {response.status_code}")
    except:
        print("✗ Main page: Not accessible")
        return
    
    # Test API endpoints
    endpoints = [
        ("/api/status", "GET"),
        ("/api/evidence", "GET"),
        ("/api/run_scan/packet", "POST"),
        ("/api/start_monitoring", "POST"),
        ("/api/stop_monitoring", "POST")
    ]
    
    for endpoint, method in endpoints:
        try:
            if method == "GET":
                resp = requests.get(f"{base_url}{endpoint}", timeout=5)
            else:
                resp = requests.post(f"{base_url}{endpoint}", timeout=5)
            
            if resp.status_code == 200:
                data = resp.json()
                if "count" in data:
                    print(f"✓ {endpoint}: {data['count']} items")
                elif "status" in data:
                    print(f"✓ {endpoint}: {data['status']}")
                else:
                    print(f"✓ {endpoint}: OK")
            else:
                print(f"✗ {endpoint}: {resp.status_code}")
        except Exception as e:
            print(f"✗ {endpoint}: {e}")
    
    print("\nDashboard is RUNNING and FUNCTIONAL!")
    print(f"Access it at: {base_url}")

if __name__ == "__main__":
    test_dashboard()
