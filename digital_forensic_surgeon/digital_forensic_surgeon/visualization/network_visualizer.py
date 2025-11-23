"""
Network Visualizer
Creates interactive network graphs showing tracking relationships
"""

from typing import List, Dict, Set
import plotly.graph_objects as go
import networkx as nx
from collections import defaultdict


class NetworkVisualizer:
    """Creates network visualizations of tracking ecosystem"""
    
    def __init__(self):
        self.graph = nx.Graph()
        self.node_colors = {}
        self.edge_weights = {}
    
    def build_tracking_network(self, tracking_events: List[Dict]) -> nx.Graph:
        """
        Build network graph from tracking events
        
        Nodes: User (center) + Companies
        Edges: Tracking relationships (weighted by frequency)
        
        Args:
            tracking_events: List of dicts with 'company', 'risk_score'
        
        Returns:
            NetworkX graph
        """
        
        # Clear existing graph
        self.graph.clear()
        
        # Add central "YOU" node
        self.graph.add_node("YOU", node_type="user", size=50)
        
        # Track company connections
        company_stats = defaultdict(lambda: {'count': 0, 'total_risk': 0, 'max_risk': 0})
        
        for event in tracking_events:
            company = event.get('company', 'Unknown')
            risk = event.get('risk_score', 0)
            
            company_stats[company]['count'] += 1
            company_stats[company]['total_risk'] += risk
            company_stats[company]['max_risk'] = max(company_stats[company]['max_risk'], risk)
        
        # Add company nodes and edges
        for company, stats in company_stats.items():
            if company == 'Unknown':
                continue
            
            avg_risk = stats['total_risk'] / stats['count']
            
            # Add node
            self.graph.add_node(
                company,
                node_type="company",
                size=min(5 + stats['count'] / 10, 30),  # Size based on frequency
                risk_score=avg_risk,
                count=stats['count']
            )
            
            # Add edge from YOU to company
            self.graph.add_edge(
                "YOU",
                company,
                weight=stats['count'],
                risk=avg_risk
            )
        
        return self.graph
    
    def create_interactive_graph(self, risk_filter: str = 'all') -> go.Figure:
        """
        Create interactive Plotly network graph
        
        Args:
            risk_filter: 'all', 'high', 'medium', 'low'
        
        Returns:
            Plotly Figure
        """
        
        # Filter nodes by risk
        filtered_nodes = ["YOU"]
        for node in self.graph.nodes():
            if node == "YOU":
                continue
            
            risk = self.graph.nodes[node].get('risk_score', 0)
            
            if risk_filter == 'high' and risk < 8.0:
                continue
            elif risk_filter == 'medium' and (risk < 5.0 or risk >= 8.0):
                continue
            elif risk_filter == 'low' and risk >= 5.0:
                continue
            
            filtered_nodes.append(node)
        
        # Create subgraph
        subgraph = self.graph.subgraph(filtered_nodes)
        
        # Calculate layout
        pos = nx.spring_layout(subgraph, k=2, iterations=50)
        
        # Create edges
        edge_trace = []
        for edge in subgraph.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            
            weight = subgraph[edge[0]][edge[1]].get('weight', 1)
            risk = subgraph[edge[0]][edge[1]].get('risk', 5)
            
            # Color based on risk
            if risk >= 8.0:
                color = 'rgba(255, 0, 0, 0.6)'
            elif risk >= 5.0:
                color = 'rgba(255, 165, 0, 0.4)'
            else:
                color = 'rgba(0, 255, 0, 0.3)'
            
            edge_trace.append(go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                mode='lines',
                line=dict(width=min(weight/10, 5), color=color),
                hoverinfo='none',
                showlegend=False
            ))
        
        # Create nodes
        node_x = []
        node_y = []
        node_text = []
        node_size = []
        node_color = []
        
        for node in subgraph.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            
            if node == "YOU":
                # Special styling for user node
                node_size.append(60)
                node_color.append('#00ffff')
                node_text.append("🎯 YOU")
            else:
                data = subgraph.nodes[node]
                size = data.get('size', 10)
                risk = data.get('risk_score', 0)
                count = data.get('count', 0)
                
                node_size.append(size)
                
                # Color by risk
                if risk >= 8.0:
                    node_color.append('#ff0000')
                elif risk >= 5.0:
                    node_color.append('#ffaa00')
                else:
                    node_color.append('#00ff00')
                
                node_text.append(f"{node}<br>Tracks: {count}<br>Risk: {risk:.1f}/10")
        
        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=[t.split('<br>')[0] for t in node_text],  # Just company name
            hovertext=node_text,
            textposition="top center",
            marker=dict(
                size=node_size,
                color=node_color,
                line=dict(width=2, color='white')
            ),
            showlegend=False
        )
        
        # Create figure
        fig = go.Figure(data=edge_trace + [node_trace])
        
        fig.update_layout(
            title={
                'text': "🕸️ Your Tracking Network",
                'x': 0.5,
                'xanchor': 'center'
            },
            showlegend=False,
            hovermode='closest',
            margin=dict(b=0, l=0, r=0, t=40),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='#1a1a1a',
            paper_bgcolor='#1a1a1a',
            font=dict(color='white'),
            height=700
        )
        
        return fig
    
    def get_network_stats(self) -> Dict:
        """Get statistics about the network"""
        
        if len(self.graph.nodes()) <= 1:
            return {
                'total_nodes': 0,
                'total_edges': 0,
                'avg_connections': 0,
                'max_connections': 0
            }
        
        # Count connections per company
        connections = []
        for node in self.graph.nodes():
            if node != "YOU":
                connections.append(self.graph.degree[node])
        
        return {
            'total_nodes': len(self.graph.nodes()) - 1,  # Exclude YOU
            'total_edges': len(self.graph.edges()),
            'avg_connections': sum(connections) / len(connections) if connections else 0,
            'max_connections': max(connections) if connections else 0,
            'density': nx.density(self.graph)
        }
    
    def create_circular_layout(self) -> go.Figure:
        """
        Create circular layout with YOU at center
        Companies arranged in circle by risk level
        """
        
        import math
        
        # Get companies sorted by risk
        companies = []
        for node in self.graph.nodes():
            if node != "YOU":
                risk = self.graph.nodes[node].get('risk_score', 0)
                companies.append((node, risk))
        
        companies.sort(key=lambda x: x[1], reverse=True)
        
        # Position YOU at center
        pos = {"YOU": (0, 0)}
        
        # Position companies in circle
        n = len(companies)
        radius = 2.0
        
        for i, (company, risk) in enumerate(companies):
            angle = 2 * math.pi * i / n
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            pos[company] = (x, y)
        
        # Create visualization (similar to create_interactive_graph but with circular layout)
        edge_traces = []
        for edge in self.graph.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            
            risk = self.graph[edge[0]][edge[1]].get('risk', 5)
            
            if risk >= 8.0:
                color = 'rgba(255, 0, 0, 0.6)'
            elif risk >= 5.0:
                color = 'rgba(255, 165, 0, 0.4)'
            else:
                color = 'rgba(0, 255, 0, 0.3)'
            
            edge_traces.append(go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                mode='lines',
                line=dict(width=2, color=color),
                hoverinfo='none',
                showlegend=False
            ))
        
        # Node trace
        node_x = []
        node_y = []
        node_text = []
        node_size = []
        node_color = []
        
        for node, (x, y) in pos.items():
            node_x.append(x)
            node_y.append(y)
            
            if node == "YOU":
                node_size.append(80)
                node_color.append('#00ffff')
                node_text.append("🎯 YOU")
            else:
                data = self.graph.nodes[node]
                risk = data.get('risk_score', 0)
                count = data.get('count', 0)
                
                node_size.append(30)
                
                if risk >= 8.0:
                    node_color.append('#ff0000')
                elif risk >= 5.0:
                    node_color.append('#ffaa00')
                else:
                    node_color.append('#00ff00')
                
                node_text.append(f"{node}<br>{count} tracks<br>{risk:.1f}/10")
        
        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode='markers+text',
            text=[t.split('<br>')[0] for t in node_text],
            hovertext=node_text,
            hoverinfo='text',
            textposition="top center",
            marker=dict(
                size=node_size,
                color=node_color,
                line=dict(width=2, color='white')
            ),
            showlegend=False
        )
        
        fig = go.Figure(data=edge_traces + [node_trace])
        
        fig.update_layout(
            title="🎯 Tracking Radar",
            showlegend=False,
            hovermode='closest',
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='#1a1a1a',
            paper_bgcolor='#1a1a1a',
            font=dict(color='white'),
            height=700
        )
        
        return fig


def create_from_database(db_connection, risk_filter: str = 'all') -> Dict:
    """
    Create network visualization from database
    
    Returns:
        Dict with figure and stats
    """
    
    visualizer = NetworkVisualizer()
    
    # Query events
    cursor = db_connection.cursor()
    cursor.execute("""
        SELECT company_name, risk_score
        FROM tracking_events
    """)
    
    events = []
    for row in cursor.fetchall():
        events.append({
            'company': row[0],
            'risk_score': row[1]
        })
    
    # Build network
    visualizer.build_tracking_network(events)
    
    # Create visualizations
    return {
        'force_graph': visualizer.create_interactive_graph(risk_filter),
        'circular_graph': visualizer.create_circular_layout(),
        'stats': visualizer.get_network_stats()
    }
