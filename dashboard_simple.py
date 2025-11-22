"""
Reality Check Dashboard - Shows ALL tracking with timestamps!
"""

import streamlit as st
import time
from datetime import datetime
import pandas as pd
import plotly.express as px
from collections import Counter

# Page config
st.set_page_config(
    page_title="Reality Check Dashboard",
    page_icon="🔥",
    layout="wide"
)

# Initialize monitor ONCE
if 'monitor_initialized' not in st.session_state:
    from digital_forensic_surgeon.scanners.reality_check_monitor import RealityCheckMonitor
    st.session_state.monitor = RealityCheckMonitor(proxy_port=8080)
    st.session_state.monitor.start(duration_seconds=600)  # 10 minutes
    st.session_state.monitor_initialized = True
    st.session_state.start_time = datetime.now()

monitor = st.session_state.monitor

# Header
st.markdown("<h1 style='text-align: center; color: #ff4444;'>🔥 REALITY CHECK</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center;'>Live Tracking Dashboard with Timestamps</h3>", unsafe_allow_html=True)

# Get stats
stats = monitor.get_live_stats()

# Metrics row
col1, col2, col3, col4 = st.columns(4)
col1.metric("🎯 Companies", stats['total_companies'])
col2.metric("📊 Data Points", f"{stats['data_points_leaked']:,}")
col3.metric("🎯 Privacy Score", f"{stats['privacy_score']}/100")
col4.metric("📡 Requests", stats['total_trackers'])

st.markdown("---")

# Check if we have data
if len(monitor.tracking_events) == 0:
    st.warning("⚠️ NO TRACKING DATA YET")
    st.markdown("""
    ### 📋 Setup Instructions:
    
    **Step 1: Configure Firefox Proxy (REQUIRED!)**
    
    1. Open Firefox Settings (or type `about:preferences` in address bar)
    2. Search for "proxy" or scroll to "Network Settings"
    3. Click "Settings..." button
    4. Select **"Manual proxy configuration"**
    5. Enter:
       - **HTTP Proxy:** `localhost`   **Port:** `8080`
       - **HTTPS Proxy:** `localhost`  **Port:** `8080`
       - ✅ Check "Also use this proxy for HTTPS"
    6. Click **OK**
    
    **Step 2: Visit Websites**
    
    In the SAME Firefox window, visit:
    - facebook.com
    - google.com
    - youtube.com
    - news sites (cnn.com, bbc.com)
    - amazon.com
    
    **Step 3: Watch This Dashboard!**
    
    This page will auto-refresh and show tracking data as it's captured!
    
    ---
    
    **Status:** Proxy is running on `localhost:8080` ✓
    """)
else:
    # We have data! Show it!
    st.success(f"✅ CAPTURING LIVE DATA - {len(monitor.tracking_events)} events so far!")
    
    # Live feed
    st.subheader("📡 Live Feed (Last 15 Events)")
    recent = monitor.tracking_events[-15:][::-1]
    
    feed_data = []
    for e in recent:
        feed_data.append({
            "⏱️ Time": e.timestamp.strftime("%H:%M:%S"),
            "Company": e.entity_name,
            "Category": e.category,
            "Type": e.tracking_type,
            "Risk": f"{e.risk_score:.1f}/10"
        })
    
    st.dataframe(pd.DataFrame(feed_data), use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Charts
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("📊 Top Trackers")
        counts = Counter([e.entity_name for e in monitor.tracking_events])
        top10 = dict(counts.most_common(10))
        fig = px.bar(x=list(top10.values()), y=list(top10.keys()), orientation='h',
                     labels={'x': 'Requests', 'y': ''}, color=list(top10.values()),
                     color_continuous_scale='Reds')
        fig.update_layout(showlegend=False, height=350)
        st.plotly_chart(fig, use_container_width=True)
    
    with col_right:
        st.subheader("🎯 Categories")
        if stats['categories']:
            fig = px.pie(values=list(stats['categories'].values()),
                        names=list(stats['categories'].keys()),
                        color_discrete_sequence=px.colors.sequential.Reds_r)
            fig.update_layout(height=350)
            st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Full timeline
    st.subheader("📜 Complete Timeline (All Events)")
    timeline = []
    for e in monitor.tracking_events:
        timeline.append({
            "Timestamp": e.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "Company": e.entity_name,
            "Category": e.category,
            "Type": e.tracking_type,
            "Risk": f"{e.risk_score:.1f}/10",
            "Cookies": len(e.cookies),
            "URL": e.url[:80] + "..." if len(e.url) > 80 else e.url
        })
    
    df = pd.DataFrame(timeline)
    st.dataframe(df, use_container_width=True, height=400, hide_index=True)
    
    # Download
    csv = df.to_csv(index=False)
    st.download_button(
        "📥 Download Complete Timeline (CSV)",
        csv,
        file_name=f"tracking_timeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

# Footer
runtime = (datetime.now() - st.session_state.start_time).total_seconds()
status = "🟢 ACTIVE" if monitor.is_monitoring else "🔴 STOPPED"
st.markdown(f"**Status:** {status} | **Runtime:** {int(runtime//60)}m {int(runtime%60)}s")

# Auto-refresh every 3 seconds
time.sleep(3)
st.rerun()
