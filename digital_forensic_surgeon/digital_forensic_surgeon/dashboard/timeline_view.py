"""
Timeline View - Chronological Feed
Shows all tracking events in timeline format
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

def render_timeline_view(db_conn):
    """Render timeline of all tracking events"""
    
    st.markdown("## 📅 Timeline View")
    st.markdown("*Chronological feed of all tracking activity*")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        days_back = st.selectbox("Show:", ["Last 7 days", "Last 30 days", "Last 90 days", "All time"], index=1)
    
    with col2:
        # Get companies for filter
        cursor = db_conn.cursor()
        cursor.execute("SELECT DISTINCT company_name FROM tracking_events ORDER BY company_name")
        all_companies = [row[0] for row in cursor.fetchall()]
        company_filter = st.selectbox("Company:", ["All"] + all_companies)
    
    with col3:
        category_filter = st.selectbox("Category:", ["All", "Advertising", "Analytics", "Social Media", "E-Commerce"])
    
    # Parse date range
    days_map = {"Last 7 days": 7, "Last 30 days": 30, "Last 90 days": 90, "All time": 3650}
    start_date = datetime.now() - timedelta(days=days_map[days_back])
    
    # Build query
    query = """
        SELECT timestamp, company_name, domain, url, tracking_type, 
               category, risk_score, data_sent
        FROM tracking_events
        WHERE DATE(timestamp) >= ?
    """
    params = [start_date.date()]
    
    if company_filter != "All":
        query += " AND company_name = ?"
        params.append(company_filter)
    
    if category_filter != "All":
        query += " AND category = ?"
        params.append(category_filter)
    
    query += " ORDER BY timestamp DESC LIMIT 500"
    
    # Execute query
    try:
        cursor.execute(query, params)
        events = cursor.fetchall()
    except Exception as e:
        st.error(f"⚠️ Error loading timeline: {e}")
        return
    
    if not events:
        st.info("📭 No events found in this date range")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(events, columns=[
        'timestamp', 'company', 'domain', 'url', 
        'type', 'category', 'risk', 'data'
    ])
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['date'] = df['timestamp'].dt.date
    df['time'] = df['timestamp'].dt.strftime('%H:%M:%S')
    
    # Statistics
    st.markdown("### 📊 Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Events", f"{len(df):,}")
    with col2:
        st.metric("Companies", df['company'].nunique())
    with col3:
        avg_risk = df['risk'].mean()
        st.metric("Avg Risk", f"{avg_risk:.1f}/10")
    with col4:
        high_risk = len(df[df['risk'] >= 8])
        st.metric("High Risk", f"{high_risk:,}")
    
    st.markdown("---")
    
    # Visual timeline chart
    st.markdown("### 📈 Activity Over Time")
    
    # Group by date
    daily = df.groupby('date').size().reset_index(name='count')
    daily['date'] = pd.to_datetime(daily['date'])
    
    fig = px.bar(
        daily,
        x='date',
        y='count',
        title='Tracking Events Per Day',
        labels={'date': 'Date', 'count': 'Events'},
        color='count',
        color_continuous_scale='Reds'
    )
    
    fig.update_layout(
        plot_bgcolor='#0e1117',
        paper_bgcolor='#0e1117',
        font=dict(color='#fafafa'),
        xaxis=dict(gridcolor='#333'),
        yaxis=dict(gridcolor='#333'),
        height=300
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Event feed
    st.markdown("### 📜 Event Feed")
    
    # Search
    search = st.text_input("🔍 Search events (URL, company, domain)")
    
    if search:
        mask = (
            df['company'].str.contains(search, case=False, na=False) |
            df['domain'].str.contains(search, case=False, na=False) |
            df['url'].str.contains(search, case=False, na=False)
        )
        df_filtered = df[mask]
    else:
        df_filtered = df
    
    # Group by date
    for date in df_filtered['date'].unique():
        day_events = df_filtered[df_filtered['date'] == date]
        
        st.markdown(f"#### 📅 {date.strftime('%B %d, %Y')} ({len(day_events)} events)")
        
        for idx, event in day_events.iterrows():
            # Risk color
            if event['risk'] >= 8:
                risk_color = "#ff6b6b"
                risk_emoji = "🔴"
            elif event['risk'] >= 5:
                risk_color = "#ffd93d"
                risk_emoji = "🟡"
            else:
                risk_color = "#6bcf7f"
                risk_emoji = "🟢"
            
            # Event card
            with st.expander(f"{event['time']} {risk_emoji} {event['company']} · {event['type']}", expanded=False):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Company:** {event['company']}")
                    st.markdown(f"**Domain:** `{event['domain']}`")
                    st.markdown(f"**Type:** {event['type']}")
                    st.markdown(f"**Category:** {event['category']}")
                    
                    if event['url']:
                        url_preview = event['url'][:100] + "..." if len(event['url']) > 100 else event['url']
                        st.markdown(f"**URL:** `{url_preview}`")
                
                with col2:
                    st.markdown(f"<div style='background: {risk_color}22; padding: 10px; border-radius: 8px; text-align: center;'>"
                               f"<b>Risk Score</b><br><span style='font-size: 24px; color: {risk_color};'>{event['risk']:.1f}/10</span></div>", 
                               unsafe_allow_html=True)
                
                if event['data']:
                    st.markdown("**Data Sent:**")
                    st.code(event['data'], language='json')
        
        st.markdown("---")
    
    # Pagination info
    if len(events) >= 500:
        st.warning("⚠️ Showing only 500 most recent events. Use filters to narrow down.")
