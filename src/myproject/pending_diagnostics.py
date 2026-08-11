import pandas as pd
import urllib.parse
from typing import Dict, Any

def categorize_pending_record(applied_date_val: Any) -> Dict[str, Any]:
    """Categorize a pending application by operational age and return diagnostic metrics."""
    if pd.isna(applied_date_val) or applied_date_val is None:
        return {
            "category": "🟡 Follow-up Needed (7-14 Days)",
            "badge": "🟡 Follow-up Needed",
            "reason": "Missing timestamp — recommended follow-up check",
            "action": "📧 Send Follow-up Email",
            "days": 10
        }

    try:
        dt = pd.to_datetime(applied_date_val)
        now = pd.Timestamp.now(tz=dt.tz if dt.tz is not None else None)
        days = int((now - dt).days)
        if days < 0:
            days = 0
    except Exception:
        days = 10

    if days > 14:
        return {
            "category": "🔴 Stale (> 14 Days)",
            "badge": "🔴 Stale (> 14 Days)",
            "reason": f"No recruiter response for {days} days",
            "action": "📧 Send Follow-up Email",
            "days": days
        }
    elif days >= 7:
        return {
            "category": "🟡 Follow-up Needed (7-14 Days)",
            "badge": "🟡 Follow-up Needed (7-14 Days)",
            "reason": f"Pending initial screen for {days} days",
            "action": "📧 Send Follow-up Email",
            "days": days
        }
    else:
        return {
            "category": "🟢 Recently Applied (< 7 Days)",
            "badge": "🟢 Recently Applied (< 7 Days)",
            "reason": f"Applied {days} days ago — within review window",
            "action": "⏳ Awaiting Review",
            "days": days
        }


def build_pending_diagnostics_df(df: pd.DataFrame, apps_df: pd.DataFrame = None) -> pd.DataFrame:
    """Build a sanitized dataframe of pending applications with diagnostic metrics and action links."""
    display_rows = []

    # 1. Live tracker pending jobs
    if df is not None and not df.empty and 'status' in df.columns:
        active_jobs = df[df['status'].astype(str).str.lower().isin(['applied', 'pending', 'reviewing'])]
        for _, job in active_jobs.iterrows():
            company = str(job.get('company', 'Unknown')).strip().title()
            role = str(job.get('job_title', 'Unknown')).strip().title()
            raw_date = job.get('first_seen_at')
            fmt_date = pd.to_datetime(raw_date).strftime('%Y-%m-%d') if pd.notnull(raw_date) else ''
            
            diag = categorize_pending_record(raw_date)
            encoded_query = urllib.parse.quote(f"{company} {role}")
            gmail_link = f"https://mail.google.com/mail/u/0/#search/{encoded_query}"
            job_link = job.get('job_url', '')
            if pd.isna(job_link): job_link = ''

            display_rows.append({
                'Company': company,
                'Role': role,
                'Status': str(job.get('status', 'Pending')).title(),
                'Applied Date': fmt_date,
                'Days Pending': diag['days'],
                'Diagnostic Category': diag['category'],
                'Diagnostic Reason': diag['reason'],
                'Recommended Action': diag['action'],
                'Job Link': job_link,
                'Gmail': gmail_link
            })

    # 2. Historical apps_df pending records
    if apps_df is not None and not apps_df.empty and 'status' in apps_df.columns:
        hist_active = apps_df[apps_df['status'].astype(str).str.lower().isin(['applied', 'pending', 'reviewing'])]
        if df is not None and not df.empty and 'id' in df.columns and 'job_id' in hist_active.columns:
            hist_active = hist_active[~hist_active['job_id'].isin(df['id'])]

        for _, app in hist_active.iterrows():
            company = str(app.get('company', 'Unknown')).strip().title()
            role = str(app.get('role_title', 'Unknown')).strip().title()
            raw_date = app.get('applied_at')
            fmt_date = pd.to_datetime(raw_date).strftime('%Y-%m-%d') if pd.notnull(raw_date) else ''

            diag = categorize_pending_record(raw_date)
            encoded_query = urllib.parse.quote(f"{company} {role}")
            gmail_link = f"https://mail.google.com/mail/u/0/#search/{encoded_query}"
            job_link = app.get('job_posting_url', '')
            if pd.isna(job_link): job_link = ''

            display_rows.append({
                'Company': company,
                'Role': role,
                'Status': str(app.get('status', 'Pending')).title(),
                'Applied Date': fmt_date,
                'Days Pending': diag['days'],
                'Diagnostic Category': diag['category'],
                'Diagnostic Reason': diag['reason'],
                'Recommended Action': diag['action'],
                'Job Link': job_link,
                'Gmail': gmail_link
            })

    if not display_rows:
        return pd.DataFrame(columns=[
            'Sr No', 'Company', 'Role', 'Status', 'Applied Date', 'Days Pending',
            'Diagnostic Category', 'Diagnostic Reason', 'Recommended Action', 'Job Link', 'Gmail'
        ])

    diag_df = pd.DataFrame(display_rows)
    diag_df = diag_df.sort_values(by='Days Pending', ascending=False).reset_index(drop=True)
    diag_df.insert(0, 'Sr No', range(1, len(diag_df) + 1))
    return diag_df


def render_pending_diagnostics_component(df: pd.DataFrame, apps_df: pd.DataFrame = None) -> None:
    """Render the Pending Items Audit & Diagnostics component with KPI metrics, pills, and actionable suggestions."""
    import streamlit as st

    diag_df = build_pending_diagnostics_df(df, apps_df)

    if diag_df.empty:
        st.info("🎉 **No active or pending applications found.** All applications have been processed or moved to outcome stages.")
        return

    # Calculate breakdown metrics
    total_pending = len(diag_df)
    stale_count = len(diag_df[diag_df['Diagnostic Category'] == '🔴 Stale (> 14 Days)'])
    followup_count = len(diag_df[diag_df['Diagnostic Category'] == '🟡 Follow-up Needed (7-14 Days)'])
    recent_count = len(diag_df[diag_df['Diagnostic Category'] == '🟢 Recently Applied (< 7 Days)'])

    st.markdown("### 📋 Pending Items Audit & Operational Diagnostics")
    st.caption("Inspect why applications are pending, monitor data staleness, and launch quick follow-up actions.")

    # 1. Metric Breakdown Bar
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="📋 Total Pending", value=f"{total_pending}", delta="In active pipeline")
    with col2:
        st.metric(label="🔴 Stale (> 14 Days)", value=f"{stale_count}", delta="High follow-up priority")
    with col3:
        st.metric(label="🟡 Follow-up Needed", value=f"{followup_count}", delta="7-14 days pending")
    with col4:
        st.metric(label="🟢 Recently Applied", value=f"{recent_count}", delta="< 7 days review window")

    st.write("")

    # 2. Interactive Quick-Filter Pills
    filter_options = ["All Pending", "🔴 Stale (> 14 Days)", "🟡 Follow-up Needed (7-14 Days)", "🟢 Recently Applied (< 7 Days)"]
    selected_filter = st.pills("Filter Pending Reason:", filter_options, default="All Pending", key="pending_diag_pill_filter")

    filtered_df = diag_df.copy()
    if selected_filter != "All Pending":
        filtered_df = filtered_df[filtered_df['Diagnostic Category'] == selected_filter]

    filtered_df['Sr No'] = range(1, len(filtered_df) + 1)

    if filtered_df.empty:
        st.info(f"No pending applications match filter: **{selected_filter}**.")
    else:
        st.dataframe(
            filtered_df[[
                'Sr No', 'Company', 'Role', 'Status', 'Applied Date', 'Days Pending',
                'Diagnostic Reason', 'Recommended Action', 'Job Link', 'Gmail'
            ]],
            hide_index=True,
            width="stretch",
            column_config={
                "Sr No": st.column_config.NumberColumn("Sr No", width="small"),
                "Company": st.column_config.TextColumn("Company"),
                "Role": st.column_config.TextColumn("Role"),
                "Status": st.column_config.TextColumn("Status"),
                "Applied Date": st.column_config.TextColumn("Applied Date"),
                "Days Pending": st.column_config.NumberColumn("Days Pending", width="small"),
                "Diagnostic Reason": st.column_config.TextColumn("Diagnostic Reason"),
                "Recommended Action": st.column_config.TextColumn("Recommended Action"),
                "Job Link": st.column_config.LinkColumn("Job Posting", display_text="🔗 View Job"),
                "Gmail": st.column_config.LinkColumn("Gmail Follow-up", display_text="📧 Open Gmail")
            }
        )
