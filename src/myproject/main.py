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
from myproject.views import (
    render_overview_analytics_view,
    render_job_tracker_view,
    render_ats_scorer_view,
    render_admin_tools_view
)

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

    # Inject Custom Glassmorphism, Dark Theme & Viewport CSS Overrides
    st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Fira+Code:wght@400;500;600&display=swap');

html, body {
    font-family: 'Inter', -apple-system, sans-serif;
}

.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 1rem !important;
}

[data-testid="stMetricValue"] {
    font-size: 1.8rem !important;
}

h1, h2, h3, h4 {
    font-family: 'Inter', sans-serif;
    font-weight: 700;
    letter-spacing: -0.02em;
}

/* Preserve Streamlit Material Icons font ligatures across all viewports */
[data-testid="stExpanderToggleIcon"], 
[data-testid*="icon"], 
[data-testid*="Icon"], 
.material-symbols-outlined, 
.material-icons,
summary i,
summary span[aria-hidden="true"] {
    font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons', sans-serif !important;
}

/* Obsidian Glassmorphism Container & Expander Styling */
.stExpander, [data-testid="stForm"], div[data-testid="stContainer"][border="true"] {
    background: rgba(15, 23, 42, 0.65) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    backdrop-filter: blur(16px) !important;
    border: 1px solid rgba(59, 130, 246, 0.25) !important;
    border-radius: 12px !important;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.35), 0 0 15px rgba(59, 130, 246, 0.08) !important;
    margin-bottom: 1rem !important;
    overflow: hidden !important;
    transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease !important;
}

.stExpander:hover, [data-testid="stForm"]:hover {
    border-color: rgba(59, 130, 246, 0.45) !important;
    box-shadow: 0 10px 36px 0 rgba(0, 0, 0, 0.45), 0 0 20px rgba(59, 130, 246, 0.15) !important;
}

/* Expander Header Summary Flex Alignment */
.stExpander summary {
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
    padding: 0.85rem 1.1rem !important;
    cursor: pointer !important;
}

.stExpander summary p, details summary p {
    font-weight: 600 !important;
    font-size: 1.05rem !important;
    color: #F8FAFC !important;
    margin: 0 !important;
    flex-grow: 1 !important;
}

/* Form Widgets & Labels */
label[data-testid="stWidgetLabel"], div[data-testid="stMarkdownContainer"] p {
    font-weight: 600 !important;
    color: #F1F5F9 !important;
}

/* Universal Buttons Layout & Alignment - Prevents icon/text collisions */
button, [data-testid*="baseButton"] {
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 8px !important;
    font-weight: 600 !important;
}

button p, [data-testid*="baseButton"] p {
    margin: 0 !important;
    padding: 0 !important;
    white-space: nowrap !important;
    font-weight: 600 !important;
}

button svg, [data-testid*="baseButton"] svg, [data-testid="stExpanderToggleIcon"] svg {
    flex-shrink: 0 !important;
    vertical-align: middle !important;
}

/* Form Submit Buttons */
button[kind="primaryFormSubmit"], button[data-testid="baseButton-primaryFormSubmit"] {
    margin-top: 0.75rem !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    box-shadow: 0 4px 14px rgba(59, 130, 246, 0.3) !important;
    height: 42px !important;
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
        padding: 0.85rem !important;
        margin-bottom: 0.75rem !important;
    }
    h1 { font-size: 1.75rem !important; }
    h2 { font-size: 1.35rem !important; }
    h3 { font-size: 1.1rem !important; }
    [data-testid="stMetricValue"] { font-size: 1.35rem !important; }
}

/* Universal Interactive Element Pointer & Smooth Transitions */
button, [data-testid*="baseButton"], [data-testid="stPill"], [data-testid="stSegmentedControl"], summary, div[role="button"], [data-baseweb="tab"] {
    cursor: pointer !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

button:hover, [data-testid*="baseButton"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 16px rgba(59, 130, 246, 0.35) !important;
}

/* Metric Cards UI/UX Pro Max Styling */
[data-testid="stMetric"] {
    background: rgba(15, 23, 42, 0.5) !important;
    border: 1px solid rgba(59, 130, 246, 0.2) !important;
    border-radius: 10px !important;
    padding: 0.85rem 1.1rem !important;
    transition: border-color 0.2s ease, transform 0.2s ease !important;
}

[data-testid="stMetric"]:hover {
    border-color: rgba(59, 130, 246, 0.4) !important;
    transform: translateY(-1px) !important;
}

[data-testid="stMetricValue"] {
    font-family: 'Fira Code', monospace !important;
    font-weight: 600 !important;
}

/* Custom Scrollbars */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: #0f172a;
}
::-webkit-scrollbar-thumb {
    background: #334155;
    border-radius: 4px;
}
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
    st.markdown('<span class="header-badge">✨ RESUME ANALYTICS v1.2</span>', unsafe_allow_html=True)
    st.title("Job Intelligence Dashboard")
    st.markdown("Track your job search progress, analyze your ATS match scores, and monitor interview conversions in real-time.")

    # Display subtle status indicator
    if is_live:
        st.caption(f"🟢 {status_msg} Showing {len(filtered_data)} of {len(job_data)} jobs.")
    else:
        st.caption(f"🟡 {status_msg}")

    # Tabs navigation setup
    tab_overview, tab_tracker, tab_ats, tab_admin = st.tabs([
        "📊 Overview & Analytics",
        "📝 Job Tracker & Applications",
        "🎯 ATS Scorer",
        "⚙️ Admin & Tools"
    ])

    with tab_overview:
        render_overview_analytics_view(filtered_data, events_df, apps_df)

    with tab_tracker:
        render_job_tracker_view(filtered_data, apps_df)

    with tab_ats:
        render_ats_scorer_view(filtered_data)

    with tab_admin:
        render_admin_tools_view(job_data, apps_df, events_df)

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center;">
        <p>Resume Analytics Dashboard v1.2 • Modular Architecture</p>
        <p>© 2026 Resume Analytics Inc. All rights reserved.</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
