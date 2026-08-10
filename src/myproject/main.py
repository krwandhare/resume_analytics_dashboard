import sys
import os

# Add package directories to Python path for Streamlit Cloud deployment
_curr_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_curr_dir)
if _curr_dir not in sys.path:
    sys.path.insert(0, _curr_dir)
if _parent_dir not in sys.path:
    sys.path.insert(0, _parent_dir)

import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from myproject.data_loader import load_job_data, load_historical_data, unify_job_statuses
from myproject.components.sidebar import render_sidebar
from myproject.components.overview import render_overview
from myproject.components.insights import render_insights
from myproject.components.data_manager import render_data_manager
from myproject.components.resume_scorer import render_resume_scorer
from myproject.components.email_webhook_ingestion import render_email_webhook_ingestion
from myproject.components.add_job_form import render_add_job_form
from myproject.analytics import generate_analytics

def main():
    st.set_page_config(
        page_title="Resume Analytics Dashboard", 
        layout="wide",
        page_icon="📊"
    )

    # Inject Mobile PWA Meta Tags
    st.markdown("""
        <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
        <meta name="apple-mobile-web-app-title" content="Resume Analytics">
        <link rel="apple-touch-icon" href="https://raw.githubusercontent.com/twitter/twemoji/master/assets/72x72/1f4ca.png">
    """, unsafe_allow_html=True)

    # Inject Custom Glassmorphism & Dark Theme CSS
    st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Fira+Code:wght@400;500;600&display=swap');

html, body, [class*="st-"] {
    font-family: 'Inter', -apple-system, sans-serif;
}

h1, h2, h3, h4 {
    font-family: 'Inter', sans-serif;
    font-weight: 700;
    letter-spacing: -0.02em;
}

.stExpander, [data-testid="stForm"] {
    background: rgba(30, 41, 59, 0.55) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    backdrop-filter: blur(12px) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 12px !important;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.25) !important;
    margin-bottom: 1rem !important;
}

.header-badge {
    display: inline-flex;
    align-items: center;
    padding: 5px 14px;
    border-radius: 20px;
    background: -webkit-linear-gradient(135deg, rgba(59, 130, 246, 0.25), rgba(99, 102, 241, 0.25)) !important;
    background: linear-gradient(135deg, rgba(59, 130, 246, 0.25), rgba(99, 102, 241, 0.25)) !important;
    border: 1px solid rgba(96, 165, 250, 0.4);
    color: #60A5FA !important;
    font-size: 0.82em;
    font-weight: 600;
    letter-spacing: 0.5px;
    margin-bottom: 8px;
    box-shadow: 0 2px 10px rgba(59, 130, 246, 0.15);
}

@media (max-width: 768px) {
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        padding-left: 0.75rem !important;
        padding-right: 0.75rem !important;
    }
    [data-testid="stForm"] {
        padding: 0.75rem !important;
        margin-bottom: 0.75rem !important;
    }
    h1 { font-size: 1.8rem !important; }
    h2 { font-size: 1.4rem !important; }
    h3 { font-size: 1.15rem !important; }
    [data-testid="stMetricValue"] { font-size: 1.4rem !important; }
}

::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}
::-webkit-scrollbar-track {
    background: #0F172A;
}
::-webkit-scrollbar-thumb {
    background: #334155;
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
    background: #475569;
}
</style>""", unsafe_allow_html=True)

    # Fetch and sanitize data
    with st.spinner("Fetching job data..."):
        job_data, is_live, status_msg = load_job_data()
        apps_df, events_df = load_historical_data(job_data)
        
        # Unify statuses across dashboard
        job_data = unify_job_statuses(job_data, apps_df)

    # Sidebar setup & filtering
    filtered_data, company_filter, status_filter = render_sidebar(job_data)

    with st.sidebar:
        with st.expander("📚 Job Hunting Playbook", expanded=False):
            st.markdown("""
            **Data-Driven Job Hunting**
            
            **ATS Match Score:** A percentage score predicting your likelihood to pass Automated Tracking Systems. >80% is ideal.
            
            **Tailoring:** Customize your resume keywords for each application using the AI tips provided in the Details tab.
            
            **Funnel:** Track your applications from "Applied" to "Interviewing". If your drop-off is high, reconsider your application strategy.
            """)

    # Main content header
    st.markdown('<span class="header-badge">✨ RESUME ANALYTICS v1.1</span>', unsafe_allow_html=True)
    st.title("Job Intelligence Dashboard")
    st.markdown("Track your job search progress, analyze your ATS match scores, and monitor interview conversions in real-time.")

    # Display subtle status indicator
    if is_live:
        st.caption(f"🟢 {status_msg} Showing {len(filtered_data)} of {len(job_data)} jobs.")
    else:
        st.caption(f"🟡 {status_msg}")

    # Render Interactive Add New Job Application Form
    render_add_job_form()

    # Tabs navigation
    st.write("")
    st.divider()
    
    if len(filtered_data) == 0:
        with st.container():
            st.info("👋 **Welcome to Resume Analytics!**")
            st.markdown("""
            Here is how this tool helps you land interviews:
            1. **Track** your applications.
            2. **Analyze** your AI Match Score for each job.
            3. **Improve** your resume with coaching tips.
            """)
            st.button("➕ Add Your First Job", on_click=lambda: st.success("Feature coming soon!"))
    else:
        st.markdown("## 📊 Overview")
        render_overview(filtered_data, events_df, apps_df)

        st.divider()
        st.markdown("## 📈 Visual Analytics")
        generate_analytics(filtered_data, events_df, apps_df)

        st.divider()
        st.markdown("## 📝 Details & Insights")
        render_insights(filtered_data, apps_df)
        
        st.divider()
        render_resume_scorer(filtered_data)

        st.divider()
        render_email_webhook_ingestion(filtered_data)

        st.divider()
        render_data_manager(job_data, apps_df, events_df)

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center;">
        <p>Resume Analytics Dashboard v1.1 • Robust Data Engine</p>
        <p>© 2026 Resume Analytics Inc. All rights reserved.</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
