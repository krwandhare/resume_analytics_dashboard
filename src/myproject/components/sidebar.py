import streamlit as st
import pandas as pd
import datetime
from typing import Tuple, List

def render_sidebar(df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str], List[str]]:
    """Render sidebar title, information, and filters."""
    with st.sidebar:
        st.title("📊 Job Analytics")
        st.markdown("""
        **Job Application Analytics** powered by Supabase.
        """)

        st.markdown("---")
        st.markdown("### Filters")
        st.caption("Use these filters to narrow down your job search. All charts and metrics will update automatically.")

        if df.empty:
            st.warning("No job data available to filter.")
            return df, [], []

        # Get unique values cleanly
        companies = sorted([c for c in df['company'].unique() if pd.notna(c) and str(c).strip()])
        statuses = sorted([s for s in df['status'].unique() if pd.notna(s) and str(s).strip()])

        company_filter = st.multiselect(
            "Filter by Company",
            options=companies,
            default=[]
        )
        status_filter = st.multiselect(
            "Filter by Status",
            options=statuses,
            default=[]
        )

        # Apply filters
        filtered_df = df.copy()
        if company_filter:
            filtered_df = filtered_df[filtered_df['company'].isin(company_filter)]
        if status_filter:
            filtered_df = filtered_df[filtered_df['status'].isin(status_filter)]

        st.markdown("---")
        st.markdown("### 📥 Export Data")
        if not filtered_df.empty:
            csv_data = filtered_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Download Filtered Data (CSV)",
                data=csv_data,
                file_name=f"job_applications_{datetime.date.today().isoformat()}.csv",
                mime="text/csv",
                width="stretch"
            )

        st.markdown("---")
        now_str = datetime.datetime.now().strftime("%I:%M %p")
        st.caption(f"Last synced: Today at {now_str}")
        st.markdown("Made with ❤️ by Job Analytics Team")

    return filtered_df, company_filter, status_filter
