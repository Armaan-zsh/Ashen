"""
PDF Report Generator
Creates professional PDF reports with tracking statistics
"""

from digital_forensic_surgeon.dashboard.timeline_view import render_timeline_view
from fpdf import FPDF
from datetime import datetime
import tempfile
from pathlib import Path

class TrackingReportPDF(FPDF):
    """Custom PDF for tracking reports"""
    
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Digital Forensic Surgeon - Tracking Report', 0, 1, 'C')
        self.ln(5)
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_pdf_report(db_conn, privacy_score) -> bytes:
    """Generate PDF report"""
    
    pdf = TrackingReportPDF()
    pdf.add_page()
    
    # Title
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Privacy & Tracking Analysis Report', 0, 1, 'C')
    pdf.ln(5)
    
    # Date
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 5, f'Generated: {datetime.now().strftime("%B %d, %Y at %H:%M")}', 0, 1, 'C')
    pdf.ln(10)
    
    # Privacy Score
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Privacy Score', 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 6, 
        f"Your Privacy Score: {privacy_score['score']}/100 (Grade: {privacy_score['grade']})\n"
        f"Frequency Score: {privacy_score['components']['frequency']:.0f}/100\n"
        f"Tracker Diversity: {privacy_score['components']['diversity']:.0f}/100\n"
        f"Risk Level: {privacy_score['components']['risk']:.0f}/100\n"
        f"Data Brokers: {privacy_score['components']['brokers']:.0f}/100"
    )
    pdf.ln(5)
    
    # Stats
    cursor = db_conn.cursor()
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(DISTINCT company_name) as companies,
            AVG(risk_score) as avg_risk,
            COUNT(DISTINCT DATE(timestamp)) as active_days
        FROM tracking_events
    """)
    stats = cursor.fetchone()
    
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Tracking Statistics', 0, 1)
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 6,
        f"Total Tracking Events: {stats[0]:,}\n"
        f"Unique Companies: {stats[1]}\n"
        f"Average Risk Score: {stats[2]:.1f}/10\n"
        f"Days Tracked: {stats[3]}"
    )
    pdf.ln(5)
    
    # Top Trackers
    cursor.execute("""
        SELECT company_name, COUNT(*) as count, AVG(risk_score) as risk
        FROM tracking_events
        GROUP BY company_name
        ORDER BY count DESC
        LIMIT 10
    """)
    top_trackers = cursor.fetchall()
    
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Top 10 Trackers', 0, 1)
    pdf.set_font('Arial', '', 10)
    
    for idx, (company, count, risk) in enumerate(top_trackers, 1):
        pdf.cell(0, 6, f"{idx}. {company}: {count:,} events (Risk: {risk:.1f}/10)", 0, 1)
    
    pdf.ln(5)
    
    # Improvement Tips
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Improvement Recommendations', 0, 1)
    pdf.set_font('Arial', '', 11)
    
    for tip in privacy_score['tips']:
        # Remove emoji for PDF
        clean_tip = tip.split(' ', 1)[1] if ' ' in tip else tip
        pdf.multi_cell(0, 5, f"• {clean_tip}")
    
    return pdf.output(dest='S').encode('latin1')

def create_export_button(db_conn, privacy_score):
    """Create download button for PDF report"""
    import streamlit as st
    
    try:
        pdf_bytes = generate_pdf_report(db_conn, privacy_score)
        
        st.download_button(
            label="📄 Download PDF Report",
            data=pdf_bytes,
            file_name=f"tracking_report_{datetime.now().strftime('%Y%m%d')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    except ImportError:
        st.warning("⚠️ PDF export requires fpdf package. Install with: pip install fpdf")
    except Exception as e:
        st.error(f"❌ Error generating PDF: {e}")
