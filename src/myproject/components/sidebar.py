import streamlit as st
import pandas as pd
import datetime
from typing import Tuple, List

def render_sidebar(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str], List[str]]:
    """Render sidebar title, information, and filters using Material Symbols & Obsidian Glassmorphism."""
    with st.sidebar:
        st.markdown("<div style='margin-bottom: 1rem;'><span class='header-badge'>:material/analytics: REAL-TIME TRACKER</span><h2 style='margin: 4px 0; color: #F8FAFC;'>Resume Analytics</h2><p style='font-size: 0.85rem; color: #94A3B8;'>Powered by Supabase & AI Match Scoring</p></div>", unsafe_allow_html=True)

        st.markdown("### :material/tune: Filters")
        st.caption("Narrow down applications across companies and status levels.")

        if df.empty:
            st.warning("No job data available to filter.")
            return df, [], []

        # Get unique values cleanly
        companies = sorted([c for c in df['company'].unique() if pd.notna(c) and str(c).strip()])
        statuses = sorted([s for s in df['status'].unique() if pd.notna(s) and str(s).strip()])

        company_filter = st.multiselect(
            "Filter by Company",
            options=companies,
            default=[],
            help="Select one or more target companies"
        )
        status_filter = st.multiselect(
            "Filter by Status",
            options=statuses,
            default=[],
            help="Select application stage"
        )

        # Apply filters
        filtered_df = df.copy()
        if company_filter:
            filtered_df = filtered_df[filtered_df['company'].isin(company_filter)]
        if status_filter:
            filtered_df = filtered_df[filtered_df['status'].isin(status_filter)]

        st.markdown("---")
        st.markdown("### :material/download: Export Data")
        if not filtered_df.empty:
            csv_data = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Filtered CSV",
                data=csv_data,
                file_name=f"job_applications_{datetime.date.today().isoformat()}.csv",
                mime="text/csv",
                width="stretch",
                type="secondary"
            )

        st.markdown("---")
        now_str = datetime.datetime.now().strftime("%I:%M %p")
        st.caption(f":material/sync: Last synced: Today at {now_str}")
        st.caption("Made with ❤️ by Job Analytics Team")

    return filtered_df, company_filter, status_filter
