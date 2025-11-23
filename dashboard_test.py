#!/usr/bin/env python3
"""
Quick test to verify the dashboard starts without errors
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_dashboard_import():
    """Test that dashboard can be imported"""
    try:
        from digital_forensic_surgeon.dashboard.app import start_dashboard, ForensicDashboard
        print("✅ Dashboard imported successfully")
        
        # Test dashboard initialization
        dashboard = ForensicDashboard()
        print("✅ Dashboard initialized successfully")
        
        # Check if static files are properly configured
        from pathlib import Path
        static_dir = Path(__file__).parent / "digital_forensic_surgeon" / "dashboard" / "static"
        if static_dir.exists():
            print(f"✅ Static directory exists: {static_dir}")
            
            # Check for required files
            css_file = static_dir / "style.css"
            js_file = static_dir / "script.js"
            
            if css_file.exists():
                print("✅ style.css exists")
            else:
                print("❌ style.css missing")
                
            if js_file.exists():
                print("✅ script.js exists")
            else:
                print("❌ script.js missing")
        else:
            print(f"❌ Static directory missing: {static_dir}")
        
        return True
        
    except Exception as e:
        print(f"❌ Dashboard import failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Dashboard Startup...")
    print("=" * 50)
    
    if test_dashboard_import():
        print("\n🎉 Dashboard is ready to start!")
        print("\n📖 To start the dashboard, run:")
        print('python -c "from digital_forensic_surgeon.dashboard.app import start_dashboard; start_dashboard()"')
        print("\nThen visit: http://localhost:8000")
    else:
        print("\n❌ Dashboard has issues that need to be fixed")
        sys.exit(1)
