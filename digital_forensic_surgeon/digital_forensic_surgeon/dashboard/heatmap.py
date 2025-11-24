"""
Simple GitHub Heatmap - Rebuilt Properly
No complex logic, just a simple calendar grid
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar

def render_simple_heatmap(db_conn):
    """Simple, working GitHub-style heatmap"""
    
    st.markdown("## 📅 When Are You Tracked?")
    
    # Date range picker
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("From:", value=datetime.now().date() - timedelta(days=90))
    with col2:
        end_date = st.date_input("To:", value=datetime.now().date())
    
    # Get data
    cursor = db_conn.cursor()
    query = """
        SELECT DATE(timestamp) as date, COUNT(*) as count
        FROM tracking_events
        WHERE DATE(timestamp) BETWEEN ? AND ?
        GROUP BY DATE(timestamp)
    """
    cursor.execute(query, (str(start_date), str(end_date)))
    results = cursor.fetchall()
    
    if not results:
        st.warning("No data in this range")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(results, columns=['date', 'count'])
    df['date'] = pd.to_datetime(df['date'])
    
    # Create calendar display
    st.markdown("### Calendar View")
    
    # Group by month
    df['month'] = df['date'].dt.to_period('M')
    months = df['month'].unique()
    
    for month in sorted(months):
        month_data = df[df['month'] == month]
        month_date = month.to_timestamp()
        
        st.markdown(f"#### {month_date.strftime('%B %Y')}")
        
        # Create calendar grid for this month
        cal = calendar.monthcalendar(month_date.year, month_date.month)
        
        # Display as table
        header = "| Mon | Tue | Wed | Thu | Fri | Sat | Sun |"
        separator = "|-----|-----|-----|-----|-----|-----|-----|"
        
        rows = [header, separator]
        
        for week in cal:
            row_cells = []
            for day in week:
                if day == 0:
                    row_cells.append("     ")
                else:
                    date = datetime(month_date.year, month_date.month, day).date()
                    day_data = month_data[month_data['date'].dt.date == date]
                    
                    if not day_data.empty:
                        count = day_data['count'].values[0]
                        # Color coding
                        if count > 200:
                            emoji = "🔴"
                        elif count > 100:
                            emoji = "🟠"
                        elif count > 50:
                            emoji = "🟡"
                        else:
                            emoji = "🟢"
                        row_cells.append(f"{emoji} {day:2d}")
                    else:
                        row_cells.append(f"⚪ {day:2d}")
            
            rows.append("| " + " | ".join(row_cells) + " |")
        
        st.markdown("\n".join(rows))
        st.markdown("")
    
    # Stats
    st.markdown("### 📊 Statistics")
    
    total = df['count'].sum()
    avg = df['count'].mean()
    peak = df['count'].max()
    peak_date = df[df['count'] == peak]['date'].values[0]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Events", f"{total:,}")
    with col2:
        st.metric("Average/Day", f"{avg:.0f}")
    with col3:
        st.metric("Peak Day", f"{peak}")
    
    st.info(f"🔥 Busiest: {pd.to_datetime(peak_date).strftime('%B %d, %Y')} with **{peak} events**")
    
    # Legend
    st.markdown("""
    **Legend:**
    - ⚪ No tracking
    - 🟢 Low (1-50 events)
    - 🟡 Medium (51-100 events)
    - 🟠 High (101-200 events)
    - 🔴 Extreme (200+ events)
    """)
