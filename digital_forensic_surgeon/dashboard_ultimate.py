"""
TrackerShield ULTIMATE Dashboard
Combines ALL features: tracking data + gamification + global intel
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
import time

# Page config
st.set_page_config(
    page_title="TrackerShield - Ultimate Privacy Protection",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #ff3b3b 0%, #cc0000 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    .achievement-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        background: #ffd700;
        border-radius: 20px;
        margin: 0.5rem;
        font-weight: bold;
    }
    .live-stat {
        background: #28a745;
        color: white;
        padding: 0.5rem;
        border-radius: 5px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Load systems
@st.cache_resource
def get_systems():
    """Load all TrackerShield systems"""
    from tracker_shield.compiler.sig_compiler import SignatureCompiler
    from tracker_shield.gamification.privacy_game import PrivacyGameifier
    from tracker_shield.intel.feed import TrackerIntelFeed
    
    compiler = SignatureCompiler()
    stats = {
        'free': len(compiler.load_database(Path('tracker_shield/data/tracker_shield_free.tsdb'))),
        'pro': len(compiler.load_database(Path('tracker_shield/data/tracker_shield_pro.tsdb'))),
        'god': len(compiler.load_database(Path('tracker_shield/data/tracker_shield_god.tsdb')))
    }
    
    game = PrivacyGameifier()
    intel = TrackerIntelFeed()
    
    return stats, game, intel

# Main app
def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🛡️ TrackerShield ULTIMATE</h1>
        <p>Complete Privacy Protection + Gamification + Global Intel</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load systems
    ts_stats, game, intel = get_systems()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Dashboard")
        
        # Tier selector
        tier = st.selectbox("Your Tier", ["Free", "Pro", "God"], index=0)
        
        st.divider()
        
        # System stats
        st.subheader("📊 TrackerShield")
        st.metric("Signatures", f"{ts_stats[tier.lower()]} active")
        st.metric("Performance", "30,000+ URLs/sec")
        
        st.divider()
        
        # Your stats
        st.subheader("🎮 Your Stats")
        st.metric("Level", game.stats['level'])
        st.metric("XP", game.stats['xp'])
        st.metric("Streak", f"{game.stats['streak_days']} days")
        st.metric("Total Blocked", f"{game.stats['total_blocked']:,}")
        
        if st.button("🔄 Refresh"):
            st.cache_data.clear()
            st.rerun()
    
    # Global stats banner
    global_stats = intel.get_global_stats()
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="live-stat">
            <h3>{global_stats['total_blocked_today']:,}</h3>
            <p>Trackers Blocked Today (Global)</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="live-stat">
            <h3>{global_stats['active_users']:,}</h3>
            <p>Active Users Protected</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        privacy_score = game.calculate_daily_score(game.stats['total_blocked'])
        st.markdown(f"""
        <div class="live-stat">
            <h3>{privacy_score}/100</h3>
            <p>Your Privacy Score Today</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.divider()
    
    # Main tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎮 Gamification",
        "🌍 Global Intel",
        "📊 Your Activity",
        "🏆 Achievements",
        "⚙️ Settings"
    ])
    
    with tab1:
        st.header("🎮 Privacy Gamification")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Your Progress")
            st.metric("Level", game.stats['level'], delta=f"{game.stats['xp']} XP to next")
            st.metric("Streak", f"{game.stats['streak_days']} days", delta="🔥 Keep it up!")
            
            # Progress bar
            xp_needed = game.stats['level'] * 100
            progress = game.stats['xp'] / xp_needed if xp_needed > 0 else 0
            st.progress(progress)
            st.caption(f"{game.stats['xp']}/{xp_needed} XP")
        
        with col2:
            st.subheader("Privacy Score")
            score = game.calculate_daily_score(game.stats['total_blocked'])
            
            if score >= 80:
                grade = "A+"
                color = "green"
            elif score >= 60:
                grade = "B"
                color = "yellow"
            else:
                grade = "C"
                color = "red"
            
            st.markdown(f"### :{color}[{score}/100 - Grade {grade}]")
            st.caption("Based on trackers blocked today + streak")
            
            # Share button
            if st.button("📱 Share Your Score"):
                st.code(game.get_share_message())
    
    with tab2:
        st.header("🌍 Global Tracker Intel")
        
        # Live feed message
        st.info(intel.get_live_feed_message())
        
        # Top offenders
        st.subheader("🏆 Top Tracking Companies (Today)")
        
        offenders = intel.get_top_offenders(10)
        df_offenders = pd.DataFrame(offenders)
        
        # Custom display
        for i, row in df_offenders.iterrows():
            trend = {'up': '📈', 'down': '📉', 'stable': '➡️'}[row['trend']]
            
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write(f"**{i+1}. {row['company']}**")
            with col2:
                st.write(f"{row['blocks_today']:,} blocks")
            with col3:
                st.write(f"Risk: {row['avg_risk_score']}/10 {trend}")
        
        # Recent blocks
        st.subheader("🔴 Live Detection Feed")
        recent = intel.get_recent_blocks(5)
        
        for block in recent:
            time_ago = (datetime.now() - datetime.fromisoformat(block['timestamp'])).seconds
            st.caption(f"⚡ {time_ago}s ago: {block['company']} ({block['country']}) - {block['tracker_type']}")
    
    with tab3:
        st.header("📊 Your Tracking Activity")
        
        if game.stats['total_blocked'] == 0:
            st.info("""
            📡 **No trackers blocked yet!**
            
            To start protecting yourself:
            1. Run: `mitmdump -s tracker_shield_addon.py`
            2. Configure browser proxy (localhost:8080)
            3. Browse the web normally
            4. Watch trackers get blocked!
            """)
        else:
            # Show stats
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Blocked", f"{game.stats['total_blocked']:,}")
            with col2:
                worth = game.stats['total_blocked'] * 0.50
                st.metric("Data Worth", f"₹{worth:,.0f}")
            with col3:
                avg_per_day = game.stats['total_blocked'] / max(game.stats['streak_days'], 1)
                st.metric("Avg/Day", f"{avg_per_day:.0f}")
            
            st.info("💡 **Tip:** Increase your streak by using TrackerShield daily!")
    
    with tab4:
        st.header("🏆 Achievements")
        
        if len(game.stats['achievements']) == 0:
            st.info("🎯 No achievements unlocked yet! Block trackers to earn badges.")
        else:
            st.success(f"🎉 You've unlocked {len(game.stats['achievements'])} achievements!")
            
            for achievement in game.stats['achievements']:
                st.markdown(f"""
                <div class="achievement-badge">
                    {achievement}
                </div>
                """, unsafe_allow_html=True)
        
        st.divider()
        
        st.subheader("📋 Available Achievements")
        achievements_list = [
            ("💯 Century", "Block 100 trackers"),
            ("🏆 Millennium", "Block 1,000 trackers"),
            ("👑 Legend", "Block 10,000 trackers"),
            ("🔥 Week Warrior", "7 day streak"),
            ("🚀 Month Master", "30 day streak"),
        ]
        
        for icon_name, desc in achievements_list:
            unlocked = any(icon_name.split()[1] in a for a in game.stats['achievements'])
            status = "✅" if unlocked else "🔒"
            st.write(f"{status} **{icon_name}** - {desc}")
    
    with tab5:
        st.header("⚙️ Settings")
        
        st.subheader("🔑 License")
        tier_display = st.selectbox("Current Tier", ["Free", "Pro", "God"], index=0, disabled=True)
        
        license_key = st.text_input("Enter License Key", placeholder="TSGD-LIFETIME-XXXXXX")
        
        if st.button("Activate"):
            if license_key:
                from tracker_shield.license.validator import SimpleLicenseValidator
                license_obj = SimpleLicenseValidator.validate_key(license_key)
                if license_obj:
                    st.success(f"✅ {license_obj.tier.upper()} Tier activated!")
                    st.balloons()
                else:
                    st.error("❌ Invalid license key")
        
        st.divider()
        
        st.subheader("📤 Export Data")
        
        if st.button("Export Tracking Data"):
            from tracker_shield.export.data_exporter import DataExporter
            exporter = DataExporter()
            
            with st.spinner("Exporting..."):
                try:
                    output_dir = Path('exports')
                    output_dir.mkdir(exist_ok=True)
                    
                    exporter.export_json(output_dir / 'trackers.json')
                    exporter.export_csv(output_dir / 'trackers.csv')
                    exporter.export_html_report(output_dir / 'report.html')
                    
                    st.success("✅ Data exported to `exports/` folder!")
                except Exception as e:
                    st.error(f"❌ Export failed: {e}")
    
    # Footer
    st.divider()
    st.caption("TrackerShield Ultimate v1.0 - The Complete Privacy Protection System")

if __name__ == '__main__':
    main()
