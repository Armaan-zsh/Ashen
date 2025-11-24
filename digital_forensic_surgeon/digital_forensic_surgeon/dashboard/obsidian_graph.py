"""
Obsidian-Style Interactive Network Graph
Clean, interactive visualization like Obsidian's graph view
"""

import streamlit as st
import plotly.graph_objects as go
import networkx as nx
from typing import Dict, List, Tuple

def create_obsidian_graph(companies: List[Tuple], max_nodes: int = 15):
    """
    Create Obsidian-style interactive graph
    
    Args:
        companies: List of (name, count, risk, category) tuples
        max_nodes: Maximum number of company nodes to show
    
    Returns:
        Plotly figure
    """
    
    # Create directed graph
    G = nx.Graph()
    
    # Add YOU at center
    G.add_node("YOU", 
               node_type="user",
               size=100,
               color="#00d9ff")  # Bright cyan for YOU
    
    # Add company nodes
    for company_name, count, avg_risk, category in companies[:max_nodes]:
        # Node size based on tracking count
        node_size = min(30 + (count / 100), 80)
        
        # Color based on risk (Obsidian-style: green/yellow/red)
        if avg_risk >= 8:
            color = "#ff6b6b"  # Red - high risk
        elif avg_risk >= 5:
            color = "#ffd93d"  # Yellow - medium risk
        else:
            color = "#6bcf7f"  # Green - low risk
        
        G.add_node(company_name,
                   node_type="company",
                   size=node_size,
                   color=color,
                   count=count,
                   risk=avg_risk,
                   category=category)
        
        # Add edge from YOU to company
        G.add_edge("YOU", company_name, weight=count)
    
    # Use spring layout for clean distribution
    pos = nx.spring_layout(G, k=1.5, iterations=50, seed=42)
    
    # Create edge traces (connections)
    edge_traces = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        
        # Edge thickness based on tracking count
        weight = G[edge[0]][edge[1]]['weight']
        thickness = min(1 + weight/500, 4)
        
        edge_trace = go.Scatter(
            x=[x0, x1, None],
            y=[y0, y1, None],
            mode='lines',
            line=dict(
                width=thickness,
                color='rgba(255, 255, 255, 0.15)'  # Subtle gray lines
            ),
            hoverinfo='none',
            showlegend=False
        )
        edge_traces.append(edge_trace)
    
    # Create node trace
    node_x = []
    node_y = []
    node_sizes = []
    node_colors = []
    node_text = []
    hover_text = []
    
    for node in G.nodes():
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        
        data = G.nodes[node]
        node_sizes.append(data['size'])
        node_colors.append(data['color'])
        
        if node == "YOU":
            node_text.append("YOU")
            hover_text.append("<b>YOU</b><br>Your digital footprint")
        else:
            node_text.append("")  # No label by default (shows on hover)
            hover_text.append(
                f"<b>{node}</b><br>"
                f"{data['count']:,} tracking events<br>"
                f"Risk: {data['risk']:.1f}/10<br>"
                f"Category: {data['category']}"
            )
    
    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        marker=dict(
            size=node_sizes,
            color=node_colors,
            line=dict(width=2, color='#1a1a1a')  # Dark outline
        ),
        text=node_text,
        hovertext=hover_text,
        hoverinfo='text',
        textposition="top center",
        textfont=dict(size=14, color='white', family='monospace'),
        showlegend=False
    )
    
    # Create figure
    fig = go.Figure(data=edge_traces + [node_trace])
    
    # Obsidian-style layout
    fig.update_layout(
        showlegend=False,
        hovermode='closest',
        plot_bgcolor='#0e1117',  # Dark background
        paper_bgcolor='#0e1117',
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False,
            showticklabels=False
        ),
        height=500,
        margin=dict(l=0, r=0, t=0, b=0),
        font=dict(family='monospace')
    )
    
    return fig


def render_interactive_graph(db_conn):
    """Render the Obsidian-style graph in dashboard"""
    
    st.markdown("## 🕸️ Your Tracking Network")
    st.markdown("*Interactive graph - hover over nodes for details*")
    
    # Get company data (with error handling)
    try:
        cursor = db_conn.cursor()
        cursor.execute("""
            SELECT company_name, COUNT(*) as count, AVG(risk_score) as avg_risk, category
            FROM tracking_events
            GROUP BY company_name
            ORDER BY count DESC
            LIMIT 20
        """)
        companies = cursor.fetchall()
    except Exception as e:
        st.error(f"⚠️ Error loading graph data: {e}")
        return
    
    if not companies:
        st.warning("No tracking data")
        return
    
    # Controls
    col1, col2 = st.columns([3, 1])
    with col1:
        max_nodes = st.slider("Show top N trackers:", 5, 20, 12)
    
    # Create and display graph
    fig = create_obsidian_graph(companies, max_nodes)
    st.plotly_chart(fig, use_container_width=True)
    
    # Legend
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("🟢 **Low Risk** (< 5)")
    with col2:
        st.markdown("🟡 **Medium Risk** (5-8)")
    with col3:
        st.markdown("🔴 **High Risk** (8+)")
    
    st.info("💡 **YOU** (cyan) are at the center. Lines show data flow to companies. Hover over nodes for details!")
