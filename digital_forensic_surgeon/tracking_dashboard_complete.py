"""
Phase 3 Ultimate Dashboard
ALL features: Phases 1, 2, 3 combined!
"""

import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import time

# Page config
st.set_page_config(
    page_title="Digital Forensic Surgeon - COMPLETE",
    page_icon="🕸️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .big-stat { font-size: 36px; font-weight: bold; text-align: center; }
    .shock-mode { animation: pulse-red 2s infinite; }
    @keyframes pulse-red {
        0%, 100% { background-color: rgba(255, 0, 0, 0.1); }
        50% { background-color: rgba(255, 0, 0, 0.3); }
    }
</style>
""", unsafe_allow_html=True)

# Initialize
from digital_forensic_surgeon.database.tracking_schema import TrackingDatabase
from digital_forensic_surgeon.services.background_monitor import MonitorManager
from digital_forensic_surgeon.analytics.data_value_calculator import calculate_from_database
from digital_forensic_surgeon.privacy.privacy_fixer import generate_from_database as generate_blocking_rules
from digital_forensic_surgeon.gamification.gamification import GamificationEngine
from digital_forensic_surgeon.visualization.network_visualizer import create_from_database as create_network
from digital_forensic_surgeon.visualization.geo_visualizer import create_from_database as create_geo

db = TrackingDatabase()
gamification = GamificationEngine()

# Sidebar
with st.sidebar:
    st.title("🎮 Control Center")
    
    shock_mode = st.toggle("😱 Shock Mode", value=False)
    
    st.markdown("---")
    st.subheader("🔄 Monitor")
    
    is_running = MonitorManager.is_running()
    if is_running:
        st.success("🟢 ACTIVE")
        if st.button("⏹️ Stop"):
            MonitorManager.stop_monitor()
            st.rerun()
    else:
        st.error("🔴 STOPPED")
        if st.button("▶️ Start"):
            MonitorManager.start_monitor()
            st.rerun()

# Header
st.markdown("<h1 style='text-align: center;'>🕸️ Digital Forensic Surgeon - COMPLETE EDITION</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #888;'>All Phases Integrated</p>", unsafe_allow_html=True)

# Get data
stats = db.get_stats_summary()

# Tabs
tabs = st.tabs([
    "🕸️ Network Graph", "🌍 Geographic View", "🛡️ Privacy Fixer", 
    "🏆 Achievements", "💰 Data Value", "🕐 Timeline", "📊 Stats"
])

# TAB 1: NETWORK GRAPH (Phase 3 - NEW!)
with tabs[0]:
    st.header("🕸️ Your Tracking Network")
    
    if stats['total_events'] > 0:
        risk_filter = st.selectbox(
            "Filter by Risk:",
            ["all", "high", "medium", "low"],
            format_func=lambda x: {
                "all": "Show All",
                "high": "High Risk Only (8+)",
                "medium": "Medium Risk (5-8)",
                "low": "Low Risk (<5)"
            }[x]
        )
        
        layout_type = st.radio("Layout:", ["Force-Directed", "Circular Radar"], horizontal=True)
        
        # Generate network visualization
        network_data = create_network(db.conn, risk_filter)
        
        # Show stats
        col1, col2, col3 = st.columns(3)
        col1.metric("Companies", network_data['stats']['total_nodes'])
        col2.metric("Connections", network_data['stats']['total_edges'])
        col3.metric("Network Density", f"{network_data['stats']['density']:.2%}")
        
        # Show graph
        if layout_type == "Force-Directed":
            st.plotly_chart(network_data['force_graph'], use_container_width=True)
        else:
            st.plotly_chart(network_data['circular_graph'], use_container_width=True)
        
        st.info("💡 **YOU** are the cyan node at the center. Companies are connected to you. Red = High Risk, Yellow = Medium, Green = Low")
    else:
        st.warning("No data yet. Run a scan or start monitoring!")

# TAB 2: GEOGRAPHIC VIEW (Phase 3 - NEW!)
with tabs[1]:
    st.header("🌍 Where Your Data Travels")
    
    if stats['total_events'] > 0:
        # User location input (optional)
        user_location = None  # Initialize first
        
        with st.expander("📍 Set Your Location (Optional)"):
            col1, col2 = st.columns(2)
            user_lat = col1.number_input("Latitude", value=20.0, step=0.1)
            user_lon = col2.number_input("Longitude", value=0.0, step=0.1)
            user_location = {'lat': user_lat, 'lon': user_lon, 'city': 'Your Location'}
        
        # Generate geo visualization
        geo_data = create_geo(db.conn, user_location)
        
        # Shocking stats
        st.subheader("🚀 Travel Statistics")
        for fact in geo_data['stats']['facts']:
            if shock_mode:
                st.error(fact)
            else:
                st.info(fact)
        
        # World map
        st.plotly_chart(geo_data['world_map'], use_container_width=True)
        
        # Country breakdown
        st.plotly_chart(geo_data['country_chart'], use_container_width=True)
        
        st.info("💡 Red lines show data flowing from YOU (cyan star) to tracking companies around the world")
    else:
        st.warning("No data yet")

# TAB 3: PRIVACY FIXER (Phase 2)
with tabs[2]:
    st.header("🛡️ Block All Trackers")
    
    if stats['total_events'] > 0:
        risk_level = st.selectbox("What to block:", ["all", "high", "medium"])
        
        blocking_rules = generate_blocking_rules(db.conn, risk_level)
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Domains Found", blocking_rules['stats']['total_domains'])
        col2.metric("High-Risk", blocking_rules['stats']['high_risk'])
        col3.metric("Will Block", blocking_rules['stats']['would_block'])
        
        st.subheader("💾 Download Blocking Rules")
        col1, col2 = st.columns(2)
        
        with col1:
            st.download_button("📥 uBlock Origin", blocking_rules['ublock_origin'], 
                             file_name="ublock_rules.txt", mime="text/plain")
            st.download_button("📥 AdGuard", blocking_rules['adguard'],
                             file_name="adguard_rules.txt", mime="text/plain")
        
        with col2:
            st.download_button("📥 DNS Blocklist", blocking_rules['dns_blocklist'],
                             file_name="dns_blocklist.txt", mime="text/plain")
            st.download_button("📥 Hosts File", blocking_rules['hosts_file'],
                             file_name="hosts_file.txt", mime="text/plain")
    else:
        st.warning("No data yet")

# TAB 4: ACHIEVEMENTS (Phase 2)
with tabs[3]:
    st.header("🏆 Achievements & Privacy Score")
    
    score_data = gamification.calculate_privacy_score(stats)
    
    # Big score
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        color = "#00ff00" if score_data['score'] >= 70 else "#ffaa00" if score_data['score'] >= 50 else "#ff0000"
        st.markdown(f"<div class='big-stat' style='color: {color};'>{score_data['score']}/100</div>", unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align: center;'>Grade: {score_data['grade']}</h2>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align: center;'>{score_data['message']}</h3>", unsafe_allow_html=True)
    
    # Achievements
    st.subheader("🏆 Achievements")
    value_data = calculate_from_database(db.conn) if stats['total_events'] > 0 else {'yearly_value': 0}
    gamification.check_achievements({
        'total_events': stats['total_events'],
        'high_risk_events': stats['high_risk_events'],
        'data_value_yearly': value_data.get('yearly_value', 0)
    })
    
    cols = st.columns(3)
    for idx, achievement in enumerate(gamification.ACHIEVEMENTS.values()):
        with cols[idx % 3]:
            if achievement.unlocked:
                st.success(f"{achievement.icon} **{achievement.name}**\n\n✅ Unlocked!")
            else:
                st.info(f"🔒 **{achievement.name}**\n\n(Locked)")

# TAB 5: DATA VALUE (Phase 1)
with tabs[4]:
    st.header("💰 What Your Data Is Worth")
    
    if stats['total_events'] > 0:
        value_data = calculate_from_database(db.conn)
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("💸 Daily", f"${value_data['daily_value']:.2f}")
        col2.metric("💰 Monthly", f"${value_data['monthly_value']:.2f}")
        col3.metric("🤑 Yearly", f"${value_data['yearly_value']:.2f}")
        col4.metric("📈 10-Year", f"${value_data['yearly_value'] * 10:.2f}")
        
        from digital_forensic_surgeon.analytics.data_value_calculator import DataValueCalculator
        calculator = DataValueCalculator()
        for fact in calculator.get_shocking_facts(value_data):
            st.info(fact)
    else:
        st.warning("No data yet")

# TAB 6: TIMELINE (Phase 2)
with tabs[5]:
    st.header("🕐 Timeline Explorer")
    
    if stats['total_events'] > 0:
        cursor = db.conn.cursor()
        cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM tracking_events")
        min_date, max_date = cursor.fetchone()
        
        if min_date:
            min_dt = datetime.fromisoformat(min_date).date()
            max_dt = datetime.fromisoformat(max_date).date()
            
            selected_date = st.date_input("📅 Jump to Date", value=max_dt, 
                                         min_value=min_dt, max_value=max_dt)
            
            results = db.query_events_by_date(str(selected_date), str(selected_date))
            
            if results:
                st.success(f"Found {len(results)} events on {selected_date}")
                df = pd.DataFrame(results, columns=['Time', 'Company', 'Domain', 'URL', 'Type', 'Category', 'Risk', 'Browser'])
                st.dataframe(df, use_container_width=True, height=400, hide_index=True)
            else:
                st.info("No events on this date")
    else:
        st.warning("No timeline data")

# TAB 7: STATISTICS
with tabs[6]:
    st.header("📊 Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Events", f"{stats['total_events']:,}")
    col2.metric("Companies", stats['unique_companies'])
    col3.metric("High-Risk", f"{stats['high_risk_events']:,}")
    col4.metric("Sessions", stats['active_sessions'])
    
    companies_data = db.get_company_stats()
    if companies_data:
        df = pd.DataFrame(companies_data, columns=['Company', 'Category', 'Risk', 'Total', 'First', 'Last'])
        st.dataframe(df, use_container_width=True, hide_index=True)

# Footer
st.markdown("---")
st.markdown("<p style='text-align: center;'>🕸️ Digital Forensic Surgeon - Complete Edition (All Phases)</p>", unsafe_allow_html=True)
