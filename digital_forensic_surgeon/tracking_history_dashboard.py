"""
Unified Tracking Dashboard
Query and visualize both historical and live tracking data
"""

import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Page config
st.set_page_config(
    page_title="Complete Tracking History",
    page_icon="🔍",
    layout="wide"
)

# Header
st.markdown("<h1 style='text-align: center;'>🔍 Complete Tracking History Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Historical + Live Tracking Data</p>", unsafe_allow_html=True)

# Initialize database
from digital_forensic_surgeon.database.tracking_schema import TrackingDatabase
from digital_forensic_surgeon.services.background_monitor import MonitorManager

db = TrackingDatabase()

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🔍 Query Explorer", "📜 Live Monitor", "📈 Statistics"])

# Tab 1: Overview
with tab1:
    st.subheader("System Overview")
    
    # Get stats
    stats = db.get_stats_summary()
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Events", f"{stats['total_events']:,}")
    col2.metric("Unique Companies", stats['unique_companies'])
    col3.metric("High-Risk Events", f"{stats['high_risk_events']:,}")
    col4.metric("Active Sessions", stats['active_sessions'])
    
    st.markdown("---")
    
    # Monitor status
    monitor = MonitorManager.get_monitor()
    is_running = MonitorManager.is_running()
    
    st.subheader("24/7 Monitor Status")
    if is_running:
        st.success("🟢 Monitor is ACTIVE - capturing all tracking")
        status = monitor.get_status()
        st.json(status)
    else:
        st.warning("🔴 Monitor is NOT running")
        if st.button("Start Monitor"):
            MonitorManager.start_monitor()
            st.rerun()
    
    st.markdown("---")
    
    # Recent events
    st.subheader("Recent Tracking Events")
    recent = db.get_recent_events(20)
    if recent:
        df = pd.DataFrame(recent, columns=['Timestamp', 'Company', 'Domain', 'Type', 'Risk'])
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No events yet - start the monitor or run a historical scan")

# Tab 2: Query Explorer
with tab2:
    st.subheader("🔍 Query Tracking Data")
    
    # Date range picker
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime.now() - timedelta(days=30))
    with col2:
        end_date = st.date_input("End Date", datetime.now())
    
    # Company filter
    companies_data = db.get_company_stats()
    if companies_data:
        companies = [c[0] for c in companies_data]
        selected_company = st.selectbox("Filter by Company (optional)", ["All"] + companies)
    else:
        selected_company = "All"
    
    if st.button("🔎 Search"):
        # Query database
        start_str = start_date.isoformat()
        end_str = end_date.isoformat() + " 23:59:59"
        
        if selected_company == "All":
            results = db.query_events_by_date(start_str, end_str)
            columns = ['Timestamp', 'Company', 'Domain', 'URL', 'Type', 'Category', 'Risk', 'Browser']
        else:
            results = db.query_events_by_company(selected_company)
            columns = ['Timestamp', 'Domain', 'URL', 'Type', 'Risk']
        
        if results:
            st.success(f"Found {len(results):,} events")
            df = pd.DataFrame(results, columns=columns)
            st.dataframe(df, use_container_width=True, height=500, hide_index=True)
            
            # Download button
            csv = df.to_csv(index=False)
            st.download_button(
                "📥 Download Results (CSV)",
                csv,
                file_name=f"tracking_query_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.warning("No events found for the selected criteria")

# Tab 3: Live Monitor
with tab3:
    st.subheader("📡 Live Monitoring Feed")
    
    if MonitorManager.is_running():
        # Show live feed with auto-refresh
        recent = db.get_recent_events(50)
        if recent:
            df = pd.DataFrame(recent, columns=['Timestamp', 'Company', 'Domain', 'Type', 'Risk'])
            st.dataframe(df, use_container_width=True, height=600, hide_index=True)
        
        # Auto-refresh
        st.markdown("*Auto-refreshing every 10 seconds...*")
        import time
        time.sleep(10)
        st.rerun()
    else:
        st.warning("Monitor is not running. Start it from the Overview tab.")

# Tab 4: Statistics
with tab4:
    st.subheader("📊 Tracking Statistics")
    
    # Company stats
    companies_data = db.get_company_stats()
    if companies_data:
        st.markdown("### Top Tracking Companies")
        df_companies = pd.DataFrame(
            companies_data,
            columns=['Company', 'Category', 'Risk', 'Total Requests', 'First Seen', 'Last Seen']
        )
        
        # Bar chart
        fig = px.bar(
            df_companies.head(15),
            x='Total Requests',
            y='Company',
            orientation='h',
            color='Risk',
            color_continuous_scale='Reds',
            labels={'Total Requests': 'Number of Tracking Events'}
        )
        fig.update_layout(height=500, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # Full table
        st.dataframe(df_companies, use_container_width=True, hide_index=True)
    else:
        st.info("No tracking data available yet")

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #888;'>Digital Forensic Surgeon - Complete Tracking History System</p>",
    unsafe_allow_html=True
)
