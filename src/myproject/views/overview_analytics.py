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
from myproject.statuses import ACTIVE_STATUSES, INTERVIEW_STATUSES

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

    pending_count = len(filtered_data[filtered_data['status'].str.lower().isin(ACTIVE_STATUSES)]) if 'status' in filtered_data.columns else 0

    if events_df is not None and not events_df.empty and 'event_type' in events_df.columns and 'application_id' in events_df.columns:
        interview_events = events_df[events_df['event_type'].astype(str).str.lower().isin(INTERVIEW_STATUSES)]
        total_interviews = interview_events['application_id'].nunique()
    else:
        total_interviews = len(filtered_data[filtered_data['status'].str.lower().isin(INTERVIEW_STATUSES)]) if 'status' in filtered_data.columns else 0

    # 1. Top 4-Column KPI Ribbon
    top_kpi_html = f"""
    <style>
    .top-kpi-container {{ display: flex; gap: 14px; margin-bottom: 24px; flex-wrap: wrap; }}
    .top-kpi-card {{
        flex: 1; min-width: 150px; padding: 18px 14px; border-radius: 14px;
        background: rgba(30, 41, 59, 0.65);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4), inset 0 1px 1px 0 rgba(255, 255, 255, 0.1);
        text-align: center; font-family: 'Inter', -apple-system, sans-serif;
        position: relative; overflow: hidden;
    }}
    .top-kpi-card::before {{
        content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; border-radius: 14px 14px 0 0;
    }}
    .top-kpi-card .kpi-title {{ font-size: 0.82em; font-weight: 600; color: #94A3B8; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.6px; }}
    .top-kpi-card .kpi-value {{ font-size: 2.1em; font-weight: 700; color: #F8FAFC; margin-bottom: 4px; line-height: 1.1; font-family: 'Fira Code', monospace; }}
    .top-kpi-card .kpi-desc {{ font-size: 0.76em; color: #64748B; font-weight: 400; }}

    .kpi-indigo::before {{ background: linear-gradient(90deg, #6366f1, #818cf8); }}
    .kpi-rose::before {{ background: linear-gradient(90deg, #f43f5e, #fb7185); }}
    .kpi-emerald::before {{ background: linear-gradient(90deg, #10b981, #34d399); }}
    .kpi-blue::before {{ background: linear-gradient(90deg, #3b82f6, #60a5fa); }}
    </style>

    <div class="top-kpi-container">
        <div class="top-kpi-card kpi-indigo">
            <div class="kpi-title">📊 Total Jobs</div>
            <div class="kpi-value">{total_tracked}</div>
            <div class="kpi-desc">Tracked in pipeline</div>
        </div>
        <div class="top-kpi-card kpi-rose">
            <div class="kpi-title">🎯 Avg Match</div>
            <div class="kpi-value">{avg_match:.1f}%</div>
            <div class="kpi-desc">ATS screen rate</div>
        </div>
        <div class="top-kpi-card kpi-emerald">
            <div class="kpi-title">🎤 Interviews</div>
            <div class="kpi-value">{total_interviews}</div>
            <div class="kpi-desc">Reached interview stage</div>
        </div>
        <div class="top-kpi-card kpi-blue">
            <div class="kpi-title">⏳ Active/Pending</div>
            <div class="kpi-value">{pending_count}</div>
            <div class="kpi-desc">Awaiting decision</div>
        </div>
    </div>
    """
    st.markdown(top_kpi_html, unsafe_allow_html=True)

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
