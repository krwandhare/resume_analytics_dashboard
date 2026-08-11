import sys
import os

_this_dir = os.path.dirname(os.path.abspath(__file__))
_myproject_dir = os.path.dirname(_this_dir)
_src_dir = os.path.dirname(_myproject_dir)

for _p in [_src_dir, _myproject_dir, _this_dir]:
    if _p and _p not in sys.path:
        sys.path.insert(0, _p)

import streamlit as st
import pandas as pd

try:
    from myproject.components.overview import render_overview
    from myproject.analytics import generate_analytics
    from myproject.data_loader import format_staleness
except ImportError:
    from ..components.overview import render_overview
    from ..analytics import generate_analytics
    from ..data_loader import format_staleness

def render_recent_activity_tab(events_df: pd.DataFrame, key_prefix: str = "activity") -> None:
    """Render Recent Activity with a consolidated master table and 3-column inline filters."""
    st.markdown("### 📋 Consolidated Activity Feed & Master Table")
    st.caption("Inspect and filter all recent application updates, interviews, and status events across your target companies.")

    if events_df is None or events_df.empty:
        st.info("No recent historical events recorded.")
        return

    # 3-Column Inline Filter Bar with unique key_prefix scoping
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        search_query = st.text_input("🔍 Search Activity", "", placeholder="Company, role, or status...", key=f"{key_prefix}_search")
    with fc2:
        all_companies = ["All Companies"] + sorted(list(set(events_df['company'].dropna().astype(str).str.title().tolist()))) if 'company' in events_df.columns else ["All Companies"]
        selected_company = st.selectbox("Filter Company", all_companies, key=f"{key_prefix}_company_filter")
    with fc3:
        all_statuses = ["All Statuses", "🟢 Interviewing", "🔴 Rejected", "🔵 Applied", "🟡 Offer Received"]
        selected_status = st.selectbox("Filter Status", all_statuses, key=f"{key_prefix}_status_filter")

    date_col = next((c for c in ['created_at', 'event_date', 'date', 'timestamp'] if c in events_df.columns), None)
    desc_col = next((c for c in ['description', 'event_type', 'body', 'message', 'type'] if c in events_df.columns), None)

    if date_col and desc_col:
        events_view = events_df.sort_values(by=date_col, ascending=False).copy()
        if 'application_id' in events_view.columns:
            events_view = events_view.drop_duplicates(subset=['application_id'], keep='first')

        rows = []
        for idx, (_, event) in enumerate(events_view.iterrows(), 1):
            comp = str(event.get('company', 'Unknown')).strip().title()
            role = str(event.get('role_title', 'Unknown')).strip().title()
            raw_status = str(event.get(desc_col, 'Unknown')).lower()

            if raw_status == 'interviewing':
                badge = "🟢 Interviewing"
            elif raw_status in ['rejected', 'rejection']:
                badge = "🔴 Rejected"
            elif raw_status in ['applied', 'pending']:
                badge = "🔵 Applied"
            elif raw_status in ['offer', 'offer received']:
                badge = "🟡 Offer Received"
            else:
                badge = f"⚪ {raw_status.title()}"

            date_val = event.get(date_col)
            age_badge = format_staleness(date_val)
            evidence = event.get('evidence_snippet', '')
            if pd.isna(evidence):
                evidence = ''

            rows.append({
                "Sr No": idx,
                "Company": comp,
                "Role": role,
                "Status": badge,
                "Data Age": age_badge,
                "Notes / Evidence": evidence
            })

        act_df = pd.DataFrame(rows)

        # Apply Filters
        if selected_company != "All Companies":
            act_df = act_df[act_df['Company'] == selected_company]

        if selected_status != "All Statuses":
            act_df = act_df[act_df['Status'] == selected_status]

        if search_query.strip():
            sq = search_query.strip().lower()
            mask = (
                act_df['Company'].astype(str).str.lower().str.contains(sq) |
                act_df['Role'].astype(str).str.lower().str.contains(sq) |
                act_df['Status'].astype(str).str.lower().str.contains(sq)
            )
            act_df = act_df[mask]

        if not act_df.empty:
            act_df['Sr No'] = range(1, len(act_df) + 1)

            st.dataframe(
                act_df,
                hide_index=True,
                width="stretch",
                column_config={
                    "Sr No": st.column_config.NumberColumn("Sr No", width="small"),
                    "Company": st.column_config.TextColumn("Company"),
                    "Role": st.column_config.TextColumn("Role"),
                    "Status": st.column_config.TextColumn("Status"),
                    "Data Age": st.column_config.TextColumn("Data Age", help="Elapsed time since last update"),
                    "Notes / Evidence": st.column_config.TextColumn("Notes / Evidence")
                }
            )
        else:
            st.info("No activity records match your current filters.")
    else:
        st.dataframe(events_df.head(15), width="stretch", hide_index=True)

def render_overview_analytics_view(filtered_data: pd.DataFrame, events_df: pd.DataFrame = None, apps_df: pd.DataFrame = None) -> None:
    """Render the Overview & Analytics view with Top 4-Column KPI Ribbon and Sub-Tabs."""
    st.markdown("## 📊 Overview & Pipeline Health")
    st.caption("Track high-level metrics, analyze funnel performance, and review recent activity.")

    if filtered_data.empty:
        st.info("👋 **No matching job records found for the selected filters.** Adjust your sidebar filters or add a new application.")
        return

    # Calculate Top Metrics
    total_tracked = len(filtered_data)
    if apps_df is not None and not apps_df.empty:
        hist_apps = apps_df[~apps_df['job_id'].isin(filtered_data['id'])] if 'job_id' in apps_df.columns and not filtered_data.empty else apps_df
        total_tracked += len(hist_apps)

    avg_match = filtered_data['match_score'].mean() if ('match_score' in filtered_data.columns and not filtered_data['match_score'].dropna().empty) else 0.0

    pending_count = len(filtered_data[filtered_data['status'].str.lower().isin(['applied', 'pending', 'reviewing'])]) if 'status' in filtered_data.columns else 0

    if events_df is not None and not events_df.empty and 'event_type' in events_df.columns and 'application_id' in events_df.columns:
        interview_events = events_df[events_df['event_type'].astype(str).str.lower().isin(['interviewing', 'offer', 'offer received', 'hired'])]
        total_interviews = interview_events['application_id'].nunique()
    else:
        total_interviews = len(filtered_data[filtered_data['status'].str.lower().isin(['interviewing', 'offer', 'offer received', 'hired'])]) if 'status' in filtered_data.columns else 0

    # 1. Top 4-Column KPI Ribbon
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)

    with kpi_col1:
        st.metric(label="📊 Total Jobs", value=f"{total_tracked}", delta="Tracked in pipeline")

    with kpi_col2:
        st.metric(label="🎯 Avg Match", value=f"{avg_match:.1f}%", delta="ATS screen rate")

    with kpi_col3:
        st.metric(label="🎤 Interviews", value=f"{total_interviews}", delta="Reached interview stage")

    with kpi_col4:
        st.metric(label="⏳ Active/Pending", value=f"{pending_count}", delta="Awaiting decision")

    st.write("")
    st.divider()

    # 2. Sub-Tab Architecture (Summary, Analytics, Job Details, Recent Activity)
    sub_tab1, sub_tab2, sub_tab3, sub_tab4 = st.tabs([
        "📊 Summary",
        "📈 Analytics",
        "🏢 Job Details",
        "📋 Recent Activity Feed"
    ])

    with sub_tab1:
        render_overview(filtered_data, events_df, apps_df)
        st.write("")
        st.divider()
        render_recent_activity_tab(events_df, key_prefix="summary_act")

    with sub_tab2:
        generate_analytics(filtered_data, events_df, apps_df)

    with sub_tab3:
        try:
            from myproject.components.insights import render_insights
        except ImportError:
            from ..components.insights import render_insights
        render_insights(filtered_data, apps_df, key_prefix="overview_insights")

    with sub_tab4:
        render_recent_activity_tab(events_df, key_prefix="feed_act")
