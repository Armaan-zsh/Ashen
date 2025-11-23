"""
Enhanced Tracking History Dashboard - Ultimate Edition
Features: Data Value Calculator, Enhanced Visualizations, Shock Value Mode
"""

import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import time

# Page config
st.set_page_config(
    page_title="Complete Tracking History - Ultimate Edition",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for shock value mode and better styling
st.markdown("""
<style>
    .shock-mode {
        animation: pulse-red 2s infinite;
    }
    @keyframes pulse-red {
        0%, 100% { background-color: rgba(255, 0, 0, 0.1); }
        50% { background-color: rgba(255, 0, 0, 0.3); }
    }
    .big-money {
        font-size: 48px;
        font-weight: bold;
        color: #00ff00;
        text-shadow: 0 0 10px #00ff00;
    }
    .warning-flash {
        background-color: #ff0000;
        color: white;
        padding: 20px;
        border-radius: 10px;
        animation: flash 1s infinite;
    }
    @keyframes flash {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
</style>
""", unsafe_allow_html=True)

# Initialize
from digital_forensic_surgeon.database.tracking_schema import TrackingDatabase
from digital_forensic_surgeon.services.background_monitor import MonitorManager
from digital_forensic_surgeon.analytics.data_value_calculator import DataValueCalculator, calculate_from_database

db = TrackingDatabase()
calculator = DataValueCalculator()

# Sidebar - Settings
with st.sidebar:
    st.title("⚙️ Settings")
    
    # Shock Value Mode Toggle
    shock_mode = st.toggle("😱 Shock Value Mode", value=False)
    
    if shock_mode:
        st.warning("⚠️ Dramatic mode ACTIVE!")
    
    st.markdown("---")
    
    # Monitor control
    st.subheader("🔄 24/7 Monitor")
    is_running = MonitorManager.is_running()
    
    if is_running:
        st.success("🟢 ACTIVE")
        if st.button("⏹️ Stop Monitor"):
            MonitorManager.stop_monitor()
            st.rerun()
    else:
        st.error("🔴 STOPPED")
        if st.button("▶️ Start Monitor"):
            MonitorManager.start_monitor()
            st.rerun()

# Header
if shock_mode:
    st.markdown("<div class='warning-flash'><h1 style='text-align: center;'>⚠️ YOU ARE BEING TRACKED RIGHT NOW ⚠️</h1></div>", unsafe_allow_html=True)
else:
    st.markdown("<h1 style='text-align: center;'>💰 Complete Tracking History - Ultimate Edition</h1>", unsafe_allow_html=True)

# Get stats and calculate data value
stats = db.get_stats_summary()

# Calculate data value from database
if stats['total_events'] > 0:
    value_data = calculate_from_database(db.conn)
else:
    value_data = {
        'total_value': 0, 'daily_value': 0, 'monthly_value': 0,
        'yearly_value': 0, 'by_company': {}, 'top_earners': [],
        'events_analyzed': 0, 'days_tracked': 0
    }

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💰 Data Value", "📊 Enhanced Visualizations", "🔍 Query Explorer", 
    "📡 Live Monitor", "📈 Statistics"
])

# TAB 1: DATA VALUE (NEW!)
with tab1:
    st.header("💵 What Your Data Is Worth")
    
    if value_data['events_analyzed'] > 0:
        # Main value display
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if shock_mode:
                st.markdown(f"<div class='big-money'>${value_data['daily_value']:.2f}</div>", unsafe_allow_html=True)
            else:
                st.metric("💸 Daily Value", f"${value_data['daily_value']:.2f}")
            st.caption("Per Day")
        
        with col2:
            if shock_mode:
                st.markdown(f"<div class='big-money'>${value_data['monthly_value']:.2f}</div>", unsafe_allow_html=True)
            else:
                st.metric("💰 Monthly Value", f"${value_data['monthly_value']:.2f}")
            st.caption("Per Month")
        
        with col3:
            if shock_mode:
                st.markdown(f"<div class='big-money'>${value_data['yearly_value']:.2f}</div>", unsafe_allow_html=True)
            else:
                st.metric("🤑 Yearly Value", f"${value_data['yearly_value']:.2f}")
            st.caption("Per Year")
        
        with col4:
            ten_year = value_data['yearly_value'] * 10
            if shock_mode:
                st.markdown(f"<div class='big-money'>${ten_year:.2f}</div>", unsafe_allow_html=True)
            else:
                st.metric("📈 10-Year Value", f"${ten_year:.2f}")
            st.caption("Over 10 Years")
        
        st.markdown("---")
        
        # Shocking facts
        st.subheader("🔥 Shocking Facts About Your Data")
        facts = calculator.get_shocking_facts(value_data)
        
        for fact in facts:
            if shock_mode:
                st.error(fact)
            else:
                st.info(fact)
        
        st.markdown("---")
        
        # Top earners chart
        st.subheader("🎯 Companies Profiting From You")
        
        if value_data['top_earners']:
            earners_df = pd.DataFrame(
                value_data['top_earners'][:10],
                columns=['Company', 'Value']
            )
            
            fig = px.bar(
                earners_df,
                x='Value',
                y='Company',
                orientation='h',
                color='Value',
                color_continuous_scale='Reds' if shock_mode else 'Greens',
                labels={'Value': 'Money They Make ($)'}
            )
            fig.update_layout(
                height=500,
                showlegend=False,
                title="Who's Making Money From YOUR Data?"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Value breakdown
        st.subheader("💵 Value Breakdown")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Events Analyzed", f"{value_data['events_analyzed']:,}")
        with col2:
            st.metric("Days Tracked", value_data['days_tracked'])
        
    else:
        st.warning("📊 No tracking data yet. Start the monitor or run a historical scan!")

# TAB 2: ENHANCED VISUALIZATIONS (NEW!)
with tab2:
    st.header("📊 Enhanced Visualizations")
    
    if stats['total_events'] > 0:
        # Timeline heatmap
        st.subheader("🔥 Tracking Activity Heatmap")
        
        cursor = db.conn.cursor()
        cursor.execute("""
            SELECT DATE(timestamp) as date, COUNT(*) as count
            FROM tracking_events
            GROUP BY DATE(timestamp)
            ORDER BY date DESC
            LIMIT 90
        """)
        
        heatmap_data = cursor.fetchall()
        if heatmap_data:
            df_heatmap = pd.DataFrame(heatmap_data, columns=['Date', 'Count'])
            df_heatmap['Date'] = pd.to_datetime(df_heatmap['Date'])
            
            fig = px.density_heatmap(
                df_heatmap,
                x='Date',
                y=[1] * len(df_heatmap),  # Single row
                z='Count',
                color_continuous_scale='Reds' if shock_mode else 'Viridis',
                labels={'Count': 'Tracking Events'}
            )
            fig.update_layout(height=200, showlegend=False)
            fig.update_yaxis(showticklabels=False)
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Animated bar race (top trackers over time)
        st.subheader("🏁 Top Trackers Racing")
        
        companies_data = db.get_company_stats()
        if companies_data:
            df_companies = pd.DataFrame(
                companies_data,
                columns=['Company', 'Category', 'Risk', 'Total', 'First', 'Last']
            ).head(15)
            
            fig = px.bar(
                df_companies,
                x='Total',
                y='Company',
                orientation='h',
                color='Risk',
                color_continuous_scale='Reds',
                text='Total',
                labels={'Total': 'Tracking Events', 'Risk': 'Risk Score'}
            )
            fig.update_traces(texttemplate='%{text:,}', textposition='outside')
            fig.update_layout(height=600, showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Category breakdown (pie + sunburst)
        st.subheader("🎯 Tracking Categories")
        
        cursor.execute("""
            SELECT category, COUNT(*) as count
            FROM tracking_events
            WHERE category IS NOT NULL
            GROUP BY category
        """)
        
        cat_data = cursor.fetchall()
        if cat_data:
            df_cat = pd.DataFrame(cat_data, columns=['Category', 'Count'])
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_pie = px.pie(
                    df_cat,
                    names='Category',
                    values='Count',
                    color_discrete_sequence=px.colors.sequential.Reds if shock_mode else px.colors.sequential.Viridis
                )
                fig_pie.update_layout(title="Category Distribution")
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                fig_sun = px.sunburst(
                    df_cat,
                    names='Category',
                    values='Count',
                    color='Count',
                    color_continuous_scale='Reds' if shock_mode else 'Viridis'
                )
                fig_sun.update_layout(title="Category Sunburst")
                st.plotly_chart(fig_sun, use_container_width=True)
    
    else:
        st.warning("📊 No data to visualize yet")

# TAB 3: QUERY EXPLORER (Existing)
with tab3:
    st.subheader("🔍 Query Tracking Data")
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime.now() - timedelta(days=30))
    with col2:
        end_date = st.date_input("End Date", datetime.now())
    
    companies_data = db.get_company_stats()
    if companies_data:
        companies = [c[0] for c in companies_data]
        selected_company = st.selectbox("Filter by Company (optional)", ["All"] + companies)
    else:
        selected_company = "All"
    
    if st.button("🔎 Search"):
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
            
            csv = df.to_csv(index=False)
            st.download_button(
                "📥 Download Results (CSV)",
                csv,
                file_name=f"tracking_query_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.warning("No events found")

# TAB 4: LIVE MONITOR (Existing with shock mode)
with tab4:
    st.subheader("📡 Live Monitoring Feed")
    
    if MonitorManager.is_running():
        if shock_mode:
            st.markdown("<div class='warning-flash'><h3>⚠️ TRACKING IN PROGRESS ⚠️</h3></div>", unsafe_allow_html=True)
        
        recent = db.get_recent_events(50)
        if recent:
            df = pd.DataFrame(recent, columns=['Timestamp', 'Company', 'Domain', 'Type', 'Risk'])
            st.dataframe(df, use_container_width=True, height=600, hide_index=True)
        
        st.markdown("*Auto-refreshing every 10 seconds...*")
        time.sleep(10)
        st.rerun()
    else:
        st.warning("Monitor is not running")

# TAB 5: STATISTICS (Enhanced)
with tab5:
    st.subheader("📊 Tracking Statistics")
    
    # Overall stats
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Events", f"{stats['total_events']:,}")
    col2.metric("Unique Companies", stats['unique_companies'])
    col3.metric("High-Risk Events", f"{stats['high_risk_events']:,}")
    col4.metric("Active Sessions", stats['active_sessions'])
    
    # Company stats with enhanced visualization
    companies_data = db.get_company_stats()
    if companies_data:
        st.markdown("### Top Tracking Companies")
        df_companies = pd.DataFrame(
            companies_data,
            columns=['Company', 'Category', 'Risk', 'Total Requests', 'First Seen', 'Last Seen']
        )
        
        # 3D scatter plot of companies by requests vs risk
        fig_3d = px.scatter_3d(
            df_companies.head(30),
            x='Total Requests',
            y='Risk',
            z=range(len(df_companies.head(30))),
            color='Risk',
            size='Total Requests',
            hover_data=['Company'],
            color_continuous_scale='Reds'
        )
        fig_3d.update_layout(height=600)
        st.plotly_chart(fig_3d, use_container_width=True)
        
        st.dataframe(df_companies, use_container_width=True, hide_index=True)

# Footer
st.markdown("---")
if shock_mode:
    st.markdown(
        "<p style='text-align: center; color: #ff0000; font-size: 20px;'>⚠️ YOU ARE BEING WATCHED ⚠️</p>",
        unsafe_allow_html=True
    )
else:
    st.markdown(
        "<p style='text-align: center; color: #888;'>Digital Forensic Surgeon - Ultimate Edition 💰</p>",
        unsafe_allow_html=True
    )
