import streamlit as st
import pandas as pd
from myproject.components import render_add_job_form_content, render_insights

@st.dialog("➕ Add New Job Application")
def show_add_job_dialog():
    render_add_job_form_content()

def render_job_tracker_view(filtered_data: pd.DataFrame, apps_df: pd.DataFrame = None) -> None:
    """Render the Job Tracker & Applications tab view."""
    top_col1, top_col2 = st.columns([3, 1])
    with top_col1:
        st.markdown("## 📝 Job Applications Tracker")
        st.caption("Search, filter, inspect details, and launch deep Gmail links for your applications.")
    with top_col2:
        st.write("") # Spacing alignment
        if st.button("➕ Add New Job", type="primary", width="stretch", help="Click to open job application modal"):
            show_add_job_dialog()

    if filtered_data.empty:
        st.info("No application records match your current filters.")
        return

    # Render Table, Search, Gmail Deep Links, and Inspector
    render_insights(filtered_data, apps_df, key_prefix="job_tracker_insights")

