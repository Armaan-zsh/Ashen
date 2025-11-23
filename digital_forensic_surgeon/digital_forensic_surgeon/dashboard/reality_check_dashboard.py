"""
Reality Check - Live Dashboard
Streamlit-based live dashboard showing shocking privacy violations in real-time
"""

import streamlit as st
import time
from datetime import datetime, timedelta
import pandas as pd
from typing import Dict, Any
import plotly.graph_objects as go
import plotly.express as px

# Must be first Streamlit command
st.set_page_config(
    page_title="Reality Check - Live Privacy Monitor",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="collapsed"
)


def create_dashboard(monitor):
    """Create the Reality Check dashboard"""
    
    # Custom CSS for dramatic styling
    st.markdown("""
        <style>
        .big-font {
            font-size:60px !important;
            font-weight: bold;
            color: #ff4444;
            text-align: center;
        }
        .metric-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;
            color: white;
        }
        .shock-metric {
            font-size: 48px;
            font-weight: bold;
            color: #ff4444;
        }
        .warning-box {
            background: #ff4444;
            color: white;
            padding: 15px;
            border-radius: 5px;
            margin: 10px 0;
            font-weight: bold;
        }
        .stAlert {
            background-color: #1e1e1e;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Title
    st.markdown("<h1 style='text-align: center; color: #ff4444;'>🔥 REALITY CHECK</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #666;'>See Who's Tracking You RIGHT NOW</h3>", unsafe_allow_html=True)
    
    # Create placeholder for auto-refresh
    placeholder = st.empty()
    
    # Main loop for live updates
    while monitor.is_monitoring:
        with placeholder.container():
            # Get live stats
            stats = monitor.get_live_stats()
            
            # === SHOCK METRICS (Top Banner) ===
            st.markdown("---")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                    <div class="metric-container">
                        <div style="font-size: 48px; font-weight: bold;">{stats['total_companies']}</div>
                        <div style="font-size: 16px;">Companies Tracking You</div>
                        <div style="font-size: 12px; opacity: 0.8;">RIGHT NOW</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                    <div class="metric-container">
                        <div style="font-size: 48px; font-weight: bold;">{stats['data_points_leaked']:,}</div>
                        <div style="font-size: 16px;">Data Points Leaked</div>
                        <div style="font-size: 12px; opacity: 0.8;">in {stats['runtime_display']}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col3:
                privacy_score = stats['privacy_score']
                score_color = "#00ff00" if privacy_score > 70 else "#ffaa00" if privacy_score > 40 else "#ff4444"
                st.markdown(f"""
                    <div class="metric-container">
                        <div style="font-size: 48px; font-weight: bold; color: {score_color};">{privacy_score}/100</div>
                        <div style="font-size: 16px;">Privacy Score</div>
                        <div style="font-size: 12px; opacity: 0.8;">{'TERRIBLE' if privacy_score < 40 else 'POOR' if privacy_score < 70 else 'OK'}</div>
                    </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                    <div class="metric-container">
                        <div style="font-size: 48px; font-weight: bold;">{stats['total_trackers']:,}</div>
                        <div style="font-size: 16px;">Tracking Requests</div>
                        <div style="font-size: 12px; opacity: 0.8;">{stats['trackers_per_minute']:.1f} per minute</div>
                    </div>
                """, unsafe_allow_html=True)
            
            # === SHOCKING REALITY ===
            if stats['total_companies'] > 20:
                st.markdown(f"""
                    <div class="warning-box">
                        ⚠️ SHOCKING: Over {stats['total_companies']} different companies are currently receiving your personal data!
                    </div>
                """, unsafe_allow_html=True)
            
                # === LIVE NETWORK FEED ===
            st.markdown("---")
            st.markdown("### 📡 Live Network Feed")
            st.markdown("*See tracking events as they happen*")
            
            if stats['recent_events']:
                feed_data = []
                for event in reversed(stats['recent_events'][-15:]):  # Last 15 events
                    timestamp = datetime.fromisoformat(event['timestamp'])
                    feed_data.append({
                        "Time": timestamp.strftime("%H:%M:%S"),
                        "Tracker": event['entity_name'],
                        "Type": event['tracking_type'],
                        "Risk": f"{event['risk_score']:.1f}/10",
                        "Category": event['category']
                    })
                
                if feed_data:
                    df = pd.DataFrame(feed_data)
                    st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("Waiting for tracking events... Browse the web to see the reality.")
            
            # === TRACKER BREAKDOWN ===
            st.markdown("---")
            col_left, col_right = st.columns(2)
            
            with col_left:
                st.markdown("### 💀 Top Trackers")
                if monitor.tracking_events:
                    from collections import Counter
                    tracker_counts = Counter()
                    for event in monitor.tracking_events:
                        tracker_counts[event.entity_name] += 1
                    
                    top_10 = tracker_counts.most_common(10)
                    tracker_df = pd.DataFrame({
                        "Company": [t[0] for t in top_10],
                        "Requests": [t[1] for t in top_10]
                    })
                    
                    fig = px.bar(
                        tracker_df,
                        x="Requests",
                        y="Company",
                        orientation='h',
                        color="Requests",
                        color_continuous_scale="reds"
                    )
                    fig.update_layout(
                        showlegend=False,
                        height=400,
                        yaxis={'categoryorder': 'total ascending'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No tracking data yet...")
            
            with col_right:
                st.markdown("### 📊 Tracking Categories")
                if stats['categories']:
                    cat_df = pd.DataFrame({
                        "Category": list(stats['categories'].keys()),
                        "Count": list(stats['categories'].values())
                    })
                    
                    fig = px.pie(
                        cat_df,
                        values="Count",
                        names="Category",
                        hole=0.4,
                        color_discrete_sequence=px.colors.sequential.RdBu
                    )
                    fig.update_layout(height=400)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No category data yet...")
            
            # === PRIVACY VIOLATIONS TIMELINE ===
            st.markdown("---")
            st.markdown("### ⚠️ High-Risk Privacy Violations")
            
            violations = monitor.get_violations_timeline()
            if violations:
                viol_data = []
                for v in violations[-10:]:  # Last 10
                    viol_data.append({
                        "Time": datetime.fromisoformat(v['timestamp']).strftime("%H:%M:%S"),
                        "Severity": v['severity'].upper(),
                        "Entity": v['entity'],
                        "Type": v['type'],
                        "Description": v['description']
                    })
                
                viol_df = pd.DataFrame(viol_data)
                st.dataframe(viol_df, use_container_width=True, hide_index=True)
            else:
                st.success("No high-risk violations detected yet")
            
            # === WHO HAS YOUR DATA ===
            st.markdown("---")
            st.markdown("### 🕸️ Who Has Your Data")
            
            if stats['company_names']:
                st.markdown(f"**{len(stats['company_names'])} companies** have received your data:")
                
                # Group by category
                companies_by_category = {}
                for company in stats['company_names']:
                    entity = monitor.broker_db.get_entity_by_name(company)
                    if entity:
                        category = entity.category
                        if category not in companies_by_category:
                            companies_by_category[category] = []
                        companies_by_category[category].append(company)
                
                for category, companies in companies_by_category.items():
                    with st.expander(f"{category} ({len(companies)})"):
                        for company in companies:
                            entity = monitor.broker_db.get_entity_by_name(company)
                            if entity:
                                risk_color = "🔴" if entity.risk_score >= 8 else "🟠" if entity.risk_score >= 6 else "🟡"
                                st.markdown(f"{risk_color} **{company}** (Risk: {entity.risk_score}/10)")
                                if entity.known_for:
                                    st.markdown(f"   *{entity.known_for}*")
            
            # === STATS FOOTER ===
            st.markdown("---")
            st.markdown(f"""
                <div style="text-align: center; color: #666; padding: 20px;">
                    Monitoring: {stats['runtime_display']} | 
                    Total Requests: {stats['total_requests']:,} | 
                    Intercepted Trackers: {stats['total_trackers']:,} | 
                    Privacy Score: {stats['privacy_score']}/100
                </div>
            """, unsafe_allow_html=True)
        
        # Refresh every 2 seconds
        time.sleep(2)
    
    # Monitoring stopped
    st.markdown("<h2 style='text-align: center; color: #ff4444;'>⏸️ Monitoring Stopped</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Final results are shown above</p>", unsafe_allow_html=True)
    
    # Generate report button
    if st.button("📊 Generate Full Report", type="primary", use_container_width=True):
        st.success("Report will be generated... (Feature coming soon)")


def run_dashboard(monitor):
    """Run the Streamlit dashboard"""
    try:
        create_dashboard(monitor)
    except KeyboardInterrupt:
        st.info("Dashboard stopped by user")
