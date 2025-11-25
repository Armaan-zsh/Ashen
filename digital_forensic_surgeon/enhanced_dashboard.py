"""
Enhanced TrackerShield Dashboard
Shows all features: live stats, community, updates, license
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import json
from datetime import datetime
import time

# Page config
st.set_page_config(
    page_title="TrackerShield",
    page_icon="🛡️",
    layout="wide"
)

# Load integration manager for live stats
from tracker_shield.integration.manager import IntegrationManager

@st.cache_resource
def get_integration_manager():
    """Get singleton integration manager"""
    manager = IntegrationManager()
    manager.start()
    return manager

manager = get_integration_manager()

# Custom CSS
st.markdown("""
<style>
.big-metric {
    font-size: 3rem;
    font-weight: 900;
    color: #ff3b3b;
}
.metric-label {
    font-size: 0.9rem;
    color: #666;
    text-transform: uppercase;
}
.status-badge {
    display: inline-block;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 600;
}
.status-active {
    background: #d4edda;
    color: #155724;
}
.status-inactive {
    background: #f8d7da;
    color: #721c24;
}
</style>
""", unsafe_allow_html=True)

# Header
col1, col2 = st.columns([3, 1])
with col1:
    st.title("🛡️ TrackerShield")
    st.caption("Advanced Tracker Detection & Privacy Protection")

with col2:
    stats = manager.get_stats()
    if stats['trackers_detected'] > 0:
        st.markdown('<div class="status-badge status-active">● Active</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-badge status-inactive">○ Inactive</div>', unsafe_allow_html=True)

st.divider()

# Live Stats
st.header("📊 Live Statistics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Trackers Detected", stats['trackers_detected'], delta="+1" if stats['trackers_detected'] > 0 else None)

with col2:
    st.metric("Trackers Blocked", stats['trackers_blocked'])

with col3:
    st.metric("Unknown Detected", stats['unknowns_detected'])

with col4:
    st.metric("Contributions", stats['contributions_pending'])

st.divider()

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📈 Real-Time Feed", "🤝 Community", "🔄 Updates", "🔑 License"])

with tab1:
    st.subheader("Real-Time Tracker Detection")
    
    # Live feed container
    feed_container = st.empty()
    
    # Show recent detections
    events_file = Path.home() / ".trackershield" / "events.jsonl"
    
    if events_file.exists():
        with open(events_file, 'r') as f:
            lines = f.readlines()
            recent_events = lines[-20:]  # Last 20 events
            
            if recent_events:
                events_data = []
                for line in recent_events:
                    try:
                        event = json.loads(line)
                        if event['type'] == 'tracker_detected':
                            data = event['data']
                            events_data.append({
                                'Time': event['timestamp'][:19],
                                'Tracker': data.get('name', 'Unknown'),
                                'Company': data.get('company', 'Unknown'),
                                'Confidence': f"{data.get('confidence', 0)}%"
                            })
                    except:
                        pass
                
                if events_data:
                    df = pd.DataFrame(events_data)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.info("No trackers detected yet. Browse some websites to see live detection!")
            else:
                st.info("No tracking events recorded yet.")
    else:
        st.info("Start browsing to see real-time tracker detection!")
    
    # Auto-refresh
    if st.button("🔄 Refresh Feed"):
        st.rerun()

with tab2:
    st.subheader("🤝 Community Contributions")
    
    from tracker_shield.community.contributions import ContributionQueue
    queue = ContributionQueue()
    
    pending = queue.get_pending_count()
    
    if pending > 0:
        st.success(f"✅ You have {pending} unknown trackers ready to contribute!")
        
        st.write("**Your contributions help everyone:**")
        st.write("- We analyze your anonymous submissions")
        st.write("- Create new signatures for everyone")
        st.write("- 100% privacy-safe (no personal data)")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📤 Contribute Now", type="primary"):
                bundle = queue.get_upload_bundle()
                if bundle:
                    from tracker_shield.community.contributions import AnonymousUploader
                    uploader = AnonymousUploader()
                    success = uploader.upload(bundle)
                    
                    if success:
                        hashes = [c['hash'] for c in bundle['contributions']]
                        queue.mark_uploaded(hashes)
                        st.success(f"✅ Uploaded {len(bundle['contributions'])} contributions!")
                        st.balloons()
                        time.sleep(2)
                        st.rerun()
        
        with col2:
            if st.button("⏭️ Skip for Now"):
                st.info("We'll ask again when you have 10+ contributions")
    else:
        st.info("Browse the web to detect unknown trackers. We'll prompt you when you have 10+ ready to contribute!")
        
        st.write("**How it works:**")
        st.write("1. TrackerShield detects unknown tracking requests")
        st.write("2. Anonymizes and hashes the data locally")
        st.write("3. When you have 10+, we prompt for contribution")
        st.write("4. We create new signatures for everyone")

with tab3:
    st.subheader("🔄 Software Updates")
    
    from tracker_shield.updater.auto_update import DatabaseUpdater
    from tracker_shield.license.validator import SimpleLicenseValidator
    
    # Get tier from settings
    settings_file = Path.home() / ".trackershield" / "settings.json"
    tier = "free"
    if settings_file.exists():
        try:
            with open(settings_file, 'r') as f:
                settings = json.load(f)
                license_key = settings.get('license_key', '')
                if license_key.startswith('TSGD'):
                    tier = 'god'
                elif license_key.startswith('TSPR'):
                    tier = 'pro'
        except:
            pass
    
    updater = DatabaseUpdater(tier)
    current = updater.get_current_version()
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Current Version", current.get('version', 0))
    with col2:
        st.metric("Signatures", current.get('signatures', 180))
    
    if st.button("🔍 Check for Updates", type="primary"):
        update_info = updater.check_for_updates()
        
        if update_info:
            st.success(f"✨ Update Available: v{update_info['latest_version']}")
            st.write(f"**New signatures:** +{update_info['new_signatures']}")
            st.write(f"**Release date:** {update_info['release_date']}")
            
            if st.button("⬇️ Download Update"):
                with st.spinner("Downloading..."):
                    success = updater.download_update(update_info)
                    if success:
                        st.success("✅ Update installed successfully!")
                        st.balloons()
                    else:
                        st.error("❌ Update failed. Please try again.")
        else:
            st.info("✅ You're on the latest version!")
    
    st.divider()
    
    st.write(f"**Your tier:** {tier.upper()}")
    if tier == "free":
        st.write("📅 Updates: Monthly")
    elif tier == "pro":
        st.write("📅 Updates: Daily")
    else:
        st.write("📅 Updates: Daily + Exclusive")

with tab4:
    st.subheader("🔑 License Activation")
    
    # Load current settings
    if settings_file.exists():
        try:
            with open(settings_file, 'r') as f:
                settings = json.load(f)
        except:
            settings = {}
    else:
        settings = {}
    
    current_key = settings.get('license_key', '')
    
    if current_key:
        # Show current license
        license = SimpleLicenseValidator.validate_key(current_key)
        if license:
            st.success(f"✅ Active License: {license.tier.upper()} Tier")
            
            if license.days_remaining():
                st.write(f"**Expires in:** {license.days_remaining()} days")
            else:
                st.write(f"**Status:** LIFETIME ACCESS")
            
            if st.button("❌ Deactivate License"):
                settings['license_key'] = ''
                settings_file.parent.mkdir(parents=True, exist_ok=True)
                with open(settings_file, 'w') as f:
                    json.dump(settings, f)
                st.success("License deactivated. Switched to Free tier.")
                time.sleep(1)
                st.rerun()
        else:
            st.error("❌ Invalid license key")
    else:
        # License activation form
        st.write("**Enter your license key:**")
        
        license_input = st.text_input("License Key", placeholder="TSGD-XXXX-XXXX-XXXX or TSPR-XXXX-XXXX-XXXX")
        
        if st.button("✅ Activate License", type="primary"):
            if license_input:
                license = SimpleLicenseValidator.validate_key(license_input)
                
                if license:
                    settings['license_key'] = license_input
                    settings_file.parent.mkdir(parents=True, exist_ok=True)
                    with open(settings_file, 'w') as f:
                        json.dump(settings, f)
                    
                    st.success(f"✅ {license.tier.upper()} Tier activated!")
                    st.balloons()
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error("❌ Invalid license key. Please check and try again.")
            else:
                st.warning("Please enter a license key")
    
    st.divider()
    
    st.write("**Upgrade to Pro or God Tier:**")
    st.write("- **Pro:** $9/month - Daily updates, 163 signatures")
    st.write("- **God:** $999 lifetime - All 180 signatures, exclusive access")
    
    if st.button("🚀 Get God Tier"):
        st.info("God Tier launching February 2026 - First 500 only!")

# Auto-refresh every 5 seconds
time.sleep(5)
st.rerun()
