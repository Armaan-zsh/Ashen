"""
Standalone Dashboard for Reality Check
Shows ALL tracking data with timestamps, charts, and graphs!
"""

import streamlit as st
import time
from datetime import datetime
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter

# Page config
st.set_page_config(
    page_title="Reality Check - Live Tracking Dashboard",
    page_icon="🔥",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .big-metric {
        font-size: 48px;
        font-weight: bold;
        text-align: center;
    }
    .shock-header {
        background: linear-gradient(135deg, #ff4444, #cc0000);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize monitor in session state
if 'monitor' not in st.session_state:
    from digital_forensic_surgeon.scanners.reality_check_monitor import RealityCheckMonitor
    st.session_state.monitor = RealityCheckMonitor(proxy_port=8080)
    st.session_state.monitor.start(duration_seconds=600)  # 10 minutes
    st.session_state.start_time = datetime.now()

monitor = st.session_state.monitor

# Header
st.markdown("<h1 style='text-align: center; color: #ff4444;'>🔥 REALITY CHECK - LIVE TRACKING DASHBOARD</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Every company tracking you RIGHT NOW with exact timestamps!</p>", unsafe_allow_html=True)

# Auto-refresh
st_autorefresh = st.empty()
with st_autorefresh:
    time.sleep(2)  # Refresh every 2 seconds
    st.rerun()

# Get live stats
stats = monitor.get_live_stats()

# Shock Metrics Row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #ff4444, #cc0000); padding: 20px; border-radius: 10px; text-align: center;'>
        <div style='font-size: 48px; font-weight: bold; color: white;'>{stats['total_companies']}</div>
        <div style='color: white;'>Companies Tracking You</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #ff8800, #cc6600); padding: 20px; border-radius: 10px; text-align: center;'>
        <div style='font-size: 48px; font-weight: bold; color: white;'>{stats['data_points_leaked']:,}</div>
        <div style='color: white;'>Data Points Leaked</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    score = stats['privacy_score']
    color = '#00ff00' if score > 70 else '#ffaa00' if score > 40 else '#ff0000'
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, {color}, {color}aa); padding: 20px; border-radius: 10px; text-align: center;'>
        <div style='font-size: 48px; font-weight: bold; color: white;'>{score}/100</div>
        <div style='color: white;'>Privacy Score</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div style='background: linear-gradient(135deg, #8800ff, #6600cc); padding: 20px; border-radius: 10px; text-align: center;'>
        <div style='font-size: 48px; font-weight: bold; color: white;'>{stats['total_trackers']}</div>
        <div style='color: white;'>Tracking Requests</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Live Feed of Tracking Events
st.subheader("📡 Live Tracking Feed (with Timestamps!)")

if monitor.tracking_events:
    # Show most recent 20 events
    recent_events = monitor.tracking_events[-20:][::-1]  # Reverse to show newest first
    
    feed_data = []
    for event in recent_events:
        feed_data.append({
            "⏱️ Time": event.timestamp.strftime("%H:%M:%S"),
            "🎯 Company": event.entity_name,
            "📂 Category": event.category,
            "🔍 Type": event.tracking_type,
            "⚠️ Risk": f"{event.risk_score}/10",
            "🌐 URL": event.url[:50] + "..." if len(event.url) > 50 else event.url
        })
    
    df = pd.DataFrame(feed_data)
    st.dataframe(df, use_container_width=True, height=400)
else:
    st.info("📡 Waiting for tracking data... Make sure your browser proxy is configured!")
    st.code("""
Browser Proxy Settings:
• HTTP Proxy: localhost
• Port: 8080
• HTTPS Proxy: localhost  
• Port: 8080
    """)

st.markdown("---")

# Charts Row
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📊 Top Trackers")
    if monitor.tracking_events:
        tracker_counts = Counter([e.entity_name for e in monitor.tracking_events])
        top_trackers = dict(tracker_counts.most_common(10))
        
        fig = px.bar(
            x=list(top_trackers.values()),
            y=list(top_trackers.keys()),
            orientation='h',
            labels={'x': 'Requests', 'y': 'Company'},
            color=list(top_trackers.values()),
            color_continuous_scale='Reds'
        )
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No tracking data yet")

with col_right:
    st.subheader("🎯 Tracking Categories")
    if stats['categories']:
        fig = px.pie(
            values=list(stats['categories'].values()),
            names=list(stats['categories'].keys()),
            color_discrete_sequence=px.colors.sequential.Reds_r
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No tracking data yet")

st.markdown("---")

# Full Timeline with Timestamps
st.subheader("📜 Complete Tracking Timeline")

if monitor.tracking_events:
    timeline_data = []
    for event in monitor.tracking_events:
        timeline_data.append({
            "Timestamp": event.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "Company": event.entity_name,
            "Category": event.category,
            "Type": event.tracking_type,
            "Risk": event.risk_score,
            "Cookies": len(event.cookies),
            "URL": event.url
        })
    
    timeline_df = pd.DataFrame(timeline_data)
    st.dataframe(timeline_df, use_container_width=True, height=600)
    
    # Download button
    csv = timeline_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Full Timeline (CSV)",
        data=csv,
        file_name=f"reality_check_timeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )
else:
    st.warning("No events captured yet. Configure your browser proxy and start browsing!")

# Status footer
st.markdown("---")
status_text = "🟢 Monitoring ACTIVE" if monitor.is_monitoring else "🔴 Monitoring STOPPED"
runtime = (datetime.now() - st.session_state.start_time).total_seconds()
st.markdown(f"**Status:** {status_text} | **Runtime:** {int(runtime//60)}m {int(runtime%60)}s | **Auto-refresh:** Every 2 seconds")
