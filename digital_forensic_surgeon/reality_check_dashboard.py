"""
Reality Check Dashboard - COMPLETE EDITION
Network visualization + Profile poisoning + All real data
"""

import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from collections import Counter
import networkx as nx

# Page config
st.set_page_config(
    page_title="Reality Check",
    page_icon="🔴",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# PREMIUM CSS - Enhanced for Week 2
st.markdown("""
<style>
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Import Google Font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    /* Global styles */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Red banner - improved */
    .red-banner {
        background: linear-gradient(135deg, #ff0000 0%, #cc0000 100%);
        padding: 25px 30px;
        color: white;
        text-align: center;
        font-size: 24px;
        font-weight: 700;
        border-radius: 12px;
        margin-bottom: 30px;
        box-shadow: 0 4px 20px rgba(255, 0, 0, 0.3);
        animation: pulse 2s infinite;
        letter-spacing: 0.5px;
    }
    
    @keyframes pulse {
        0%, 100% { box-shadow: 0 4px 20px rgba(255, 0, 0, 0.3); }
        50% { box-shadow: 0 8px 30px rgba(255, 0, 0, 0.5); }
    }
    
    /* Money counter - enhanced */
    .money-counter {
        font-size: 64px;
        font-weight: 700;
        color: #00ff41;
        text-align: center;
        text-shadow: 0 0 30px rgba(0, 255, 65, 0.5);
        font-family: 'Courier New', monospace;
        margin: 20px 0;
    }
    
    /* Tracker card - improved */
    .tracker-card {
        background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #ff0000;
        margin: 10px 0;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .tracker-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(255, 0, 0, 0.2);
    }
    
    /* Stat box - cleaner */
    .stat-box {
        background: rgba(255, 255, 255, 0.05);
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        margin: 8px 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Mobile responsive */
    @media (max-width: 768px) {
        .red-banner {
            font-size: 18px;
            padding: 20px;
        }
        .money-counter {
            font-size: 48px;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize
from digital_forensic_surgeon.database.tracking_schema import TrackingDatabase
from digital_forensic_surgeon.analytics.data_value_calculator import calculate_from_database

db = TrackingDatabase()
stats = db.get_stats_summary()

# Calculate money (with error handling)
if stats['total_events'] > 0:
    try:
        value_data = calculate_from_database(db.conn)
    except Exception as e:
        st.error(f"⚠️ Error calculating value: {e}")
        value_data = {'yearly_value': 0, 'monthly_value': 0, 'daily_value': 0, 'top_earners': []}
else:
    value_data = {'yearly_value': 0, 'monthly_value': 0, 'daily_value': 0, 'top_earners': []}

# Get company data
cursor = db.conn.cursor()

# DATE RANGE FILTER (NEW!)
st.sidebar.markdown("## 📅 Date Range Filter")
cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM tracking_events WHERE DATE(timestamp) <= DATE('now')")
db_min, db_max = cursor.fetchone()

if db_min and db_max:
    min_dt = datetime.fromisoformat(db_min).date()
    max_dt = min(datetime.fromisoformat(db_max).date(), datetime.now().date())  # Cap at today
    
    start_date = st.sidebar.date_input("From:", value=min_dt, min_value=min_dt, max_value=max_dt)
    end_date = st.sidebar.date_input("To:", value=max_dt, min_value=min_dt, max_value=max_dt)
    
    st.sidebar.info(f"📊 Showing: {start_date} to {end_date}")
else:
    start_date = datetime(2024, 1, 1).date()
    end_date = datetime.now().date()

# Query with date filter (with error handling)
try:
    cursor.execute("""
        SELECT company_name, COUNT(*) as count, AVG(risk_score) as avg_risk, category
        FROM tracking_events
        WHERE DATE(timestamp) BETWEEN ? AND ?
        GROUP BY company_name
        ORDER BY count DESC
    """, (str(start_date), str(end_date)))
    companies = cursor.fetchall()
except Exception as e:
    st.error(f"⚠️ Error querying data: {e}")
    companies = []

# Recalculate stats for filtered date range
cursor.execute("""
    SELECT COUNT(*) as total, COUNT(DISTINCT company_name) as unique_companies
    FROM tracking_events
    WHERE DATE(timestamp) BETWEEN ? AND ?
""", (str(start_date), str(end_date)))
filtered_stats = cursor.fetchone()
total_events_filtered = filtered_stats[0]
unique_companies_filtered = filtered_stats[1]

# 🔴 RED BANNER (use filtered stats)
if total_events_filtered > 0:
    st.markdown(f"""
    <div class='red-banner'>
        ⚠️ {unique_companies_filtered} COMPANIES TRACKING YOU · ₹{value_data.get('yearly_value', 0):,.0f} GIVEN AWAY THIS YEAR ⚠️
    </div>
    """, unsafe_allow_html=True)
else:
    st.warning("⚡ No tracking data in selected date range. Try expanding the dates.")
    st.stop()

# 🎯 PRIVACY SCORE (NEW!)
from digital_forensic_surgeon.analytics.privacy_score import PrivacyScoreCalculator
privacy_calc = PrivacyScoreCalculator()
privacy = privacy_calc.calculate_score(db.conn)

col1, col2, col3 = st.columns([1, 2, 2])

with col1:
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #1a1a1a, #2d2d2d); padding: 30px; border-radius: 12px; text-align: center;'>
        <div style='font-size: 48px; margin-bottom: 10px;'>{privacy['emoji']}</div>
        <div style='font-size: 56px; font-weight: 700; color: #00ff41; margin-bottom: 5px;'>{privacy['score']}</div>
        <div style='font-size: 24px; font-weight: 600;'>Grade: {privacy['grade']}</div>
        <div style='color: #888; margin-top: 10px;'>Privacy Score</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("### 📊 Score Breakdown")
    st.progress(privacy['components']['frequency'] / 100, text=f"Frequency: {privacy['components']['frequency']:.0f}/100")
    st.progress(privacy['components']['diversity'] / 100, text=f"Tracker Diversity: {privacy['components']['diversity']:.0f}/100")
    st.progress(privacy['components']['risk'] / 100, text=f"Risk Level: {privacy['components']['risk']:.0f}/100")
    st.progress(privacy['components']['brokers'] / 100, text=f"Data Brokers: {privacy['components']['brokers']:.0f}/100")

with col3:
    st.markdown("### 💡 Improvement Tips")
    for tip in privacy['tips']:
        st.markdown(f"- {tip}")

st.markdown("---")

# 📅 CALENDAR HEATMAP (SIMPLE VERSION)
from digital_forensic_surgeon.dashboard.heatmap import render_simple_heatmap
render_simple_heatmap(db.conn)

st.markdown("---")

# TABS
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["🔴 Live Feed", "📅 Timeline", "🕸️ Network", "📊 Data & Money", "🎭 Poison", "🛡️ Actions"])

# TAB 1: LIVE FEED
with tab1:
    from digital_forensic_surgeon.dashboard.live_feed import render_live_feed
    render_live_feed()

# TAB 2: TIMELINE VIEW (NEW!)
with tab2:
    from digital_forensic_surgeon.dashboard.timeline_view import render_timeline_view
    render_timeline_view(db.conn)

# TAB 3: INTERACTIVE GRAPH
with tab3:
    from digital_forensic_surgeon.dashboard.obsidian_graph import render_interactive_graph
    render_interactive_graph(db.conn)


# TAB 4: DATA & MONEY
with tab4:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🕵️ Who's Tracking You")
        
        HIDDEN_TRACKERS = {
            'AppNexus': 'Ad exchange - sold your profile to 100+ buyers',
            'Taboola': 'Recommendation engine - tracks across thousands of sites',
            'Criteo': 'Retargeting ads - follows you everywhere',
            'Quantcast': 'Audience measurement - profiles 100M+ people',
            'ScoreCard Research': 'Market research - tracks all your browsing'
        }
        
        for company_name, count, avg_risk, category in companies[:10]:
            if company_name in HIDDEN_TRACKERS:
                st.markdown(f"""
                <div class='tracker-card'>
                    <h4>🎯 {company_name}</h4>
                    <p><strong>{count:,} times</strong> · Risk: {avg_risk:.1f}/10</p>
                    <p style='color: #ff6666;'>{HIDDEN_TRACKERS[company_name]}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class='stat-box'>
                    <strong>{company_name}</strong><br>
                    {count:,} times · Risk: {avg_risk:.1f}/10 · {category}
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 💰 Money Given Away")
        st.markdown(f"""
        <div class='money-counter'>₹{value_data.get('yearly_value', 0):,.0f}</div>
        <p style='text-align: center;'>THIS YEAR</p>
        """, unsafe_allow_html=True)
        
        st.metric("Daily", f"₹{value_data.get('daily_value', 0):.0f}")
        st.metric("Monthly", f"₹{value_data.get('monthly_value', 0):.0f}")
        
        if value_data.get('yearly_value', 0) > 0:
            samosas = int(value_data['yearly_value'] / 15.5)
            st.info(f"💡 That's **{samosas:,} samosas**!")

# TAB 5: POISON PROFILE
with tab5:
    st.markdown("## 🎭 Poison Your Tracking Profile")
    st.markdown("*Confuse trackers by generating fake interests*")
    
    from digital_forensic_surgeon.privacy.profile_poisoner import ProfilePoisoner
    
    poisoner = ProfilePoisoner()
    
    num_personas = st.slider("How many fake personas to mix:", 1, 5, 3)
    
    if st.button("🎲 Generate Poison Profile", type="primary"):
        profile = poisoner.generate_poison_profile(num_personas)
        
        st.success(f"✅ Generated profile mixing: {', '.join([p.replace('_', ' ').title() for p in profile['personas']])}")
        
        # Show instructions
        instructions = poisoner.get_poison_instructions(profile)
        st.markdown(instructions)
        
        # Show browser script
        with st.expander("🔧 Browser Console Script (Advanced)"):
            script = poisoner.generate_browser_script(profile)
            st.code(script, language='javascript')
            st.warning("⚠️ This will open multiple tabs. Close them after a few seconds!")

# TAB 6: TAKE ACTION
with tab6:
    st.markdown("## 🛡️ Take Control")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🚫 Block Trackers")
        
        risk_level = st.selectbox("What to block:", ["All trackers", "High risk only", "Medium + High risk"])
        risk_map = {"All trackers": "all", "High risk only": "high", "Medium + High risk": "medium"}
        
        if st.button("Generate Blocking Rules", type="primary", use_container_width=True):
            from digital_forensic_surgeon.privacy.privacy_fixer import generate_from_database
            blocking_rules = generate_from_database(db.conn, risk_map[risk_level])
            
            st.download_button(
                "📥 Download uBlock Origin Rules",
                blocking_rules['ublock_origin'],
                file_name="ublock_rules.txt",
                mime="text/plain",
                use_container_width=True
            )
            st.success(f"✅ Blocking {blocking_rules['stats']['would_block']} domains")
    
    with col2:
        st.markdown("### 📊 Export Data")
        
        if st.button("Export All Data as CSV", use_container_width=True):
            cursor.execute("SELECT * FROM tracking_events")
            all_data = cursor.fetchall()
            st.success(f"✅ {len(all_data):,} events ready")

# Footer
st.markdown("---")
st.markdown(f"""
<p style='text-align: center; color: #666;'>
    🔴 Reality Check · {stats['total_events']:,} events tracked · 
    Last updated: {datetime.now().strftime('%H:%M:%S')}
</p>
""", unsafe_allow_html=True)
