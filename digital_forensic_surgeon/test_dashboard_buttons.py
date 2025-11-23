#!/usr/bin/env python3
"""Test dashboard API endpoints to verify buttons work"""

import asyncio
import aiohttp
import json

async def test_dashboard_endpoints():
    """Test all dashboard API endpoints"""
    base_url = "http://127.0.0.1:8001"
    
    async with aiohttp.ClientSession() as session:
        print("Testing Dashboard API Endpoints\n" + "="*50)
        
        # Test 1: Get status
        try:
            async with session.get(f"{base_url}/api/status") as resp:
                status = await resp.json()
                print(f"✓ Status endpoint: {status}")
        except Exception as e:
            print(f"✗ Status endpoint failed: {e}")
        
        # Test 2: Get evidence
        try:
            async with session.get(f"{base_url}/api/evidence") as resp:
                evidence = await resp.json()
                print(f"✓ Evidence endpoint: {evidence}")
        except Exception as e:
            print(f"✗ Evidence endpoint failed: {e}")
        
        # Test 3: Test each scan type
        scan_types = ['packet', 'content', 'destination', 'application', 'security', 'behavioral']
        
        for scan_type in scan_types:
            try:
                async with session.post(
                    f"{base_url}/api/run_scan/{scan_type}",
                    json={}
                ) as resp:
                    result = await resp.json()
                    if resp.status == 200:
                        print(f"✓ {scan_type} scan: {result.get('count', 0)} items found")
                    else:
                        print(f"✗ {scan_type} scan failed: {result}")
            except Exception as e:
                print(f"✗ {scan_type} scan error: {e}")
        
        # Test 4: Start/Stop monitoring
        try:
            async with session.post(f"{base_url}/api/start_monitoring") as resp:
                result = await resp.json()
                print(f"✓ Start monitoring: {result}")
            
            async with session.post(f"{base_url}/api/stop_monitoring") as resp:
                result = await resp.json()
                print(f"✓ Stop monitoring: {result}")
        except Exception as e:
            print(f"✗ Monitoring test failed: {e}")
        
        print("\n" + "="*50)
        print("Dashboard API test complete!")

if __name__ == "__main__":
    asyncio.run(test_dashboard_endpoints())
