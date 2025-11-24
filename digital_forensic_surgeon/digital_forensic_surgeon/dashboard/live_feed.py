"""
Live Tracking Feed for Dashboard
Shows real-time tracking events as they happen
"""

import streamlit as st
import json
from pathlib import Path
from datetime import datetime
import time

def render_live_feed():
    """Render live tracking feed in dashboard"""
    
    st.markdown("## 🔴 Live Tracking Feed")
    st.markdown("*Real-time events from your browser (when proxy is active)*")
    
    # Check if proxy is running
    live_file = Path.home() / ".mitmproxy" / "live_events.jsonl"
    
    if not live_file.exists():
        st.warning("⚠️ No live events yet. Make sure proxy is running and browse with it enabled.")
        st.info("💡 **To enable:** Configure browser proxy to `localhost:8080`, then browse normally")
        return
    
    # Auto-refresh checkbox
    auto_refresh = st.checkbox("Auto-refresh (every 3 seconds)", value=False)
    
    if auto_refresh:
        st.empty()  # Placeholder for auto-refresh
        time.sleep(3)
        st.rerun()
    
    # Manual refresh button
    if st.button("🔄 Refresh Now"):
        st.rerun()
    
    # Read recent events
    try:
        with open(live_file, 'r') as f:
            lines = f.readlines()
            recent_events = []
            for line in lines[-50:]:  # Last 50 events
                try:
                    recent_events.append(json.loads(line.strip()))
                except:
                    pass
    except Exception as e:
        st.error(f"Error reading events: {e}")
        return
    
    if not recent_events:
        st.info("✅ Proxy is running but no trackers detected yet")
        return
    
    # Display events
    st.markdown(f"### 📡 Last {len(recent_events)} Events")
    
    for event in reversed(recent_events):  # Newest first
        timestamp = datetime.fromisoformat(event['timestamp'])
        time_ago = (datetime.now() - timestamp).seconds
        
        if time_ago < 60:
            time_str = f"{time_ago}s ago"
        elif time_ago < 3600:
            time_str = f"{time_ago//60}m ago"
        else:
            time_str = timestamp.strftime("%H:%M:%S")
        
        # Determine tracker color
        tracker = event['tracker']
        if 'Facebook' in tracker or 'Meta' in tracker:
            color = '#ff6b6b'
        elif 'Google' in tracker:
            color = '#ffd93d'
        elif 'TikTok' in tracker:
            color = '#6bcf7f'
        else:
            color = '#888'
        
        # Event card
        with st.expander(f"{time_str} · {tracker}", expanded=False):
            st.markdown(f"**URL:** `{event['url']}`")
            
            data = event.get('data', {})
            if data:
                st.markdown("**Decoded Data:**")
                st.json(data)
            else:
                st.markdown("*No decoded data*")
    
    # Stats
    st.markdown("---")
    tracker_counts = {}
    for event in recent_events:
        tracker = event['tracker']
        tracker_counts[tracker] = tracker_counts.get(tracker, 0) + 1
    
    st.markdown("### 📊 Event Breakdown")
    for tracker, count in sorted(tracker_counts.items(), key=lambda x: x[1], reverse=True):
        st.markdown(f"- **{tracker}**: {count} events")
