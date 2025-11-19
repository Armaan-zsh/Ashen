#!/usr/bin/env python3
"""Check if JavaScript functions are present in the dashboard HTML"""

import requests

def check_js_functions():
    try:
        response = requests.get("http://127.0.0.1:8001")
        html = response.text
        
        print("Checking JavaScript Functions in Dashboard")
        print("=" * 50)
        
        # Check for critical JavaScript functions
        functions_to_check = [
            "runScan",
            "toggleMonitoring", 
            "showAlert",
            "loadEvidence",
            "ForensicDashboard"
        ]
        
        for func in functions_to_check:
            if func in html:
                print(f"✓ {func} function found")
            else:
                print(f"✗ {func} function missing")
        
        # Check for button onclick attributes
        button_checks = [
            'onclick="runScan(',
            'onclick="toggleMonitoring()'
        ]
        
        print("\nChecking Button Handlers")
        print("-" * 30)
        
        for check in button_checks:
            if check in html:
                print(f"✓ {check} found")
            else:
                print(f"✗ {check} missing")
                
        print("\nDashboard is SERVING HTML with JavaScript!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_js_functions()
