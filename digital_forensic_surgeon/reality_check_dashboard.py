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

# PREMIUM CSS
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .red-banner {
        background: linear-gradient(135deg, #ff0000 0%, #cc0000 100%);
        padding: 30px;
        color: white;
        text-align: center;
        font-size: 28px;
        font-weight: bold;
        border-radius: 10px;
        margin-bottom: 30px;
        box-shadow: 0 4px 15px rgba(255, 0, 0, 0.4);
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { box-shadow: 0 4px 15px rgba(255, 0, 0, 0.4); }
        50% { box-shadow: 0 8px 25px rgba(255, 0, 0, 0.6); }
    }
    
    .money-counter {
        font-size: 56px;
        font-weight: bold;
        color: #00ff00;
        text-align: center;
        text-shadow: 0 0 20px #00ff00;
        font-family: 'Courier New', monospace;
    }
    
    .tracker-card {
        background: linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%);
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #ff0000;
        margin: 8px 0;
    }
    
    .stat-box {
        background: rgba(255, 255, 255, 0.05);
        padding: 12px;
        border-radius: 6px;
        text-align: center;
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize
from digital_forensic_surgeon.database.tracking_schema import TrackingDatabase
from digital_forensic_surgeon.analytics.data_value_calculator import calculate_from_database

db = TrackingDatabase()
stats = db.get_stats_summary()

# Calculate money
if stats['total_events'] > 0:
    value_data = calculate_from_database(db.conn)
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

# Query with date filter
cursor.execute("""
    SELECT company_name, COUNT(*) as count, AVG(risk_score) as avg_risk, category
    FROM tracking_events
    WHERE DATE(timestamp) BETWEEN ? AND ?
    GROUP BY company_name
    ORDER BY count DESC
""", (str(start_date), str(end_date)))
companies = cursor.fetchall()

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

# 📅 CALENDAR HEATMAP (SIMPLE VERSION)
from digital_forensic_surgeon.dashboard.heatmap import render_simple_heatmap
render_simple_heatmap(db.conn)

st.markdown("---")

# TABS
tab1, tab2, tab3, tab4 = st.tabs(["🕸️ Network Map", "📊 Data & Money", "🎭 Poison Profile", "🛡️ Take Action"])

# TAB 1: NETWORK VISUALIZATION
with tab1:
    st.markdown("## 🕸️ Your Tracking Network")
    st.markdown("*See how companies share YOUR data*")
    
    # Build network graph
    G = nx.Graph()
    G.add_node("YOU", node_type="user")
    
    for company_name, count, avg_risk, category in companies[:15]:  # Top 15
        G.add_node(company_name, node_type="company", count=count, risk=avg_risk)
        G.add_edge("YOU", company_name, weight=count)
    
    # Calculate layout
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    
    # Create edge traces
    edge_traces = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        weight = G[edge[0]][edge[1]]['weight']
        
        edge_traces.append(go.Scatter(
            x=[x0, x1, None],
            y=[y0, y1, None],
            mode='lines',
            line=dict(width=min(weight/100, 5), color='rgba(255, 0, 0, 0.3)'),
            hoverinfo='none',
            showlegend=False
        ))
    
    # Create node trace
    node_x = []
    node_y = []
    node_text = []
    node_size = []
    node_color = []
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        
        if node == "YOU":
            node_size.append(60)
            node_color.append('#00ffff')
            node_text.append("🎯 YOU")
        else:
            data = G.nodes[node]
            count = data['count']
            risk = data['risk']
            
            node_size.append(min(20 + count/10, 50))
            node_color.append('#ff0000' if risk >= 8 else '#ffaa00' if risk >= 5 else '#00ff00')
            node_text.append(f"{node}<br>{count:,} tracks<br>Risk: {risk:.1f}/10")
    
    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        text=[t.split('<br>')[0] for t in node_text],
        hovertext=node_text,
        hoverinfo='text',
        textposition="top center",
        marker=dict(size=node_size, color=node_color, line=dict(width=2, color='white')),
        showlegend=False
    )
    
    # Create figure
    fig = go.Figure(data=edge_traces + [node_trace])
    fig.update_layout(
        showlegend=False,
        hovermode='closest',
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor='#0e1117',
        paper_bgcolor='#0e1117',
        height=600,
        margin=dict(l=0, r=0, t=0, b=0)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("💡 **YOU** are cyan in the center. Lines show data flow. Bigger nodes = more tracking. Red = dangerous!")

# TAB 2: DATA & MONEY
with tab2:
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

# TAB 3: POISON PROFILE
with tab3:
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

# TAB 4: TAKE ACTION
with tab4:
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
