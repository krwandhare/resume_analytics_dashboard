import streamlit as st
import pandas as pd
import urllib.parse
from myproject.data_loader import format_staleness
from myproject.logger import get_logger
from myproject.statuses import (
    ACTIVE_STATUSES,
    INTERVIEW_STATUSES,
    OFFER_STATUSES,
    PRE_APPLICATION_STATUSES,
    STATUS_OPTIONS,
)

logger = get_logger(__name__)

try:
    from myproject.pending_diagnostics import render_pending_diagnostics_component
except ImportError:
    from ..pending_diagnostics import render_pending_diagnostics_component





def get_match_label(score):
    try:
        score = float(score)
        if pd.isna(score):
            return "N/A"
        if score >= 80:
            return f"🟢 Strong Match ({score:.0f}%)"
        elif score >= 60:
            return f"🟡 Good Match ({score:.0f}%)"
        else:
            return f"🔴 Low Match ({score:.0f}%)"
    except (ValueError, TypeError):
        return "N/A"

def render_overview(df: pd.DataFrame, events_df: pd.DataFrame = None, apps_df: pd.DataFrame = None) -> None:
    """Render high-level overview metrics."""
    st.markdown("<h3 style='margin-top: -0.5rem; margin-bottom: 0.5rem;'> <span class='material-symbols-outlined' style='vertical-align: middle;'>dashboard</span> Job Pipeline Overview</h3>", unsafe_allow_html=True)

    if df.empty:
        st.info("No matching records found for the selected filters.")
        return

    # Calculate metrics
    total_tracked = len(df)
    if apps_df is not None and not apps_df.empty:
        hist_apps = apps_df[~apps_df['job_id'].isin(df['id'])] if 'job_id' in apps_df.columns and not df.empty else apps_df
        total_tracked += len(hist_apps)
        
    avg_match = 0.0
    if 'match_score' in df.columns and not df['match_score'].dropna().empty:
        avg_match = df['match_score'].mean()
        
    total_companies = df['company'].nunique() if 'company' in df.columns else 0
    
    pending_count = len(df[df['status'].str.lower().isin(ACTIVE_STATUSES)]) if 'status' in df.columns else 0
    
    if events_df is not None and not events_df.empty and 'event_type' in events_df.columns and 'application_id' in events_df.columns:
        interview_events = events_df[events_df['event_type'].astype(str).str.lower().isin(INTERVIEW_STATUSES)]
        total_interviews = interview_events['application_id'].nunique()
        offer_events = events_df[events_df['event_type'].astype(str).str.lower().isin(OFFER_STATUSES)]
        total_offers = offer_events['application_id'].nunique()
    else:
        total_interviews = len(df[df['status'].str.lower().isin(INTERVIEW_STATUSES)]) if 'status' in df.columns else 0
        total_offers = len(df[df['status'].str.lower().isin(OFFER_STATUSES)]) if 'status' in df.columns else 0

    total_applications = len(df[~df['status'].str.lower().isin(PRE_APPLICATION_STATUSES)]) if 'status' in df.columns else len(df)
    if apps_df is not None and not apps_df.empty:
        total_applications += len(hist_apps)

    # Calculate conversion metrics
    app_to_interview_pct = (total_interviews / total_applications * 100) if total_applications > 0 else 0.0
    interview_to_offer_pct = (total_offers / total_interviews * 100) if total_interviews > 0 else 0.0

    if app_to_interview_pct >= 15.0:
        app_to_int_badge = "🟢 Strong"
    elif app_to_interview_pct >= 8.0:
        app_to_int_badge = "🟡 Moderate"
    else:
        app_to_int_badge = "🔴 Low Pass"

    if interview_to_offer_pct >= 30.0:
        int_to_off_badge = "🟢 Strong"
    elif interview_to_offer_pct >= 15.0:
        int_to_off_badge = "🟡 Moderate"
    else:
        int_to_off_badge = "🔴 Low Pass"

    # Custom HTML Flexbox KPI Cards (Glassmorphism Dark Aesthetics)
    kpi_html = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Fira+Code:wght@600;700&display=swap');
    
    .kpi-container {{ display: flex; gap: 14px; margin-bottom: 24px; flex-wrap: wrap; }}
    .kpi-card {{ 
        flex: 1; min-width: 150px; padding: 18px 14px; border-radius: 14px; 
        background: rgba(30, 41, 59, 0.65);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4), inset 0 1px 1px 0 rgba(255, 255, 255, 0.1);
        text-align: center; font-family: 'Inter', -apple-system, sans-serif;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }}
    .kpi-card::before {{
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; height: 3px;
        border-radius: 14px 14px 0 0;
    }}
    .kpi-card:hover {{
        transform: translateY(-5px);
        border-color: rgba(99, 102, 241, 0.4);
        box-shadow: 0 15px 35px -5px rgba(0, 0, 0, 0.5), 0 0 20px 0 rgba(99, 102, 241, 0.2);
    }}
    .kpi-card .kpi-title {{ font-size: 0.82em; font-weight: 600; color: #94A3B8; margin-bottom: 8px; text-transform: uppercase; letter-spacing: 0.6px; }}
    .kpi-card .kpi-value {{ font-size: 2.1em; font-weight: 700; color: #F8FAFC; margin-bottom: 4px; line-height: 1.1; font-family: 'Fira Code', monospace; }}
    .kpi-card .kpi-desc {{ font-size: 0.76em; color: #64748B; font-weight: 400; }}
    
    .kpi-indigo::before {{ background: linear-gradient(90deg, #6366f1, #818cf8); }}
    .kpi-rose::before {{ background: linear-gradient(90deg, #f43f5e, #fb7185); }}
    .kpi-amber::before {{ background: linear-gradient(90deg, #f59e0b, #fbbf24); }}
    .kpi-blue::before {{ background: linear-gradient(90deg, #3b82f6, #60a5fa); }}
    .kpi-emerald::before {{ background: linear-gradient(90deg, #10b981, #34d399); }}
    .kpi-purple::before {{ background: linear-gradient(90deg, #a855f7, #c084fc); }}
    .kpi-teal::before {{ background: linear-gradient(90deg, #14b8a6, #2dd4bf); }}
    </style>
    <div class="kpi-container">
        <div class="kpi-card kpi-purple">
            <div class="kpi-title">📈 App → Interview</div>
            <div class="kpi-value">{app_to_interview_pct:.1f}%</div>
            <div class="kpi-desc">{app_to_int_badge} ({total_interviews}/{total_applications})</div>
        </div>
        <div class="kpi-card kpi-teal">
            <div class="kpi-title">🏆 Interview → Offer</div>
            <div class="kpi-value">{interview_to_offer_pct:.1f}%</div>
            <div class="kpi-desc">{int_to_off_badge} ({total_offers}/{total_interviews if total_interviews > 0 else 0})</div>
        </div>
    </div>
    """
    st.markdown(kpi_html, unsafe_allow_html=True)
    # KPI Drilldown using st.pills
    drilldown_options = ["Hide Table", "💼 View All Jobs", "🏢 View Unique Companies", "👀 View Active / Pending", "🎤 View Interviews"]
    selected_drilldown = st.pills("Drill down into KPIs:", drilldown_options, default="Hide Table")
    
    if selected_drilldown == "💼 View All Jobs":
        display_rows = []

        for _, job in df.iterrows():
            raw_date = job.get('first_seen_at')
            fmt_date = pd.to_datetime(raw_date).strftime('%Y-%m-%d') if pd.notnull(raw_date) else ''
            
            company = job.get('company', 'Unknown')
            role = job.get('job_title', 'Unknown')
            encoded_query = urllib.parse.quote(f"{company} {role}")
            gmail_link = f"https://mail.google.com/mail/u/0/#search/{encoded_query}"
            
            display_rows.append({
                '_id': job.get('id'),
                '_source_table': job.get('_source_table', 'jobs'),
                'Company': company,
                'Role': role,
                'Status': str(job.get('status', 'Unknown')).title(),
                'Applied Date': fmt_date,
                'Match Score': get_match_label(job.get('match_score')),
                'Source': 'Live Tracker',
                'Job Link': job.get('job_url', '') if pd.notnull(job.get('job_url')) else '',
                'Gmail': gmail_link
            })
            
        if apps_df is not None and not apps_df.empty:
            hist_apps = apps_df[~apps_df['job_id'].isin(df['id'])] if 'job_id' in apps_df.columns and not df.empty else apps_df
            for _, app in hist_apps.iterrows():
                raw_date = app.get('applied_at')
                fmt_date = pd.to_datetime(raw_date).strftime('%Y-%m-%d') if pd.notnull(raw_date) else ''
                
                company = app.get('company', 'Unknown')
                role = app.get('role_title', 'Unknown')
                encoded_query = urllib.parse.quote(f"{company} {role}")
                gmail_link = f"https://mail.google.com/mail/u/0/#search/{encoded_query}"
                
                display_rows.append({
                    '_id': app.get('id'),
                    '_source_table': 'job_applications',
                    'Company': company,
                    'Role': role,
                    'Status': str(app.get('status', 'Unknown')).title(),
                    'Applied Date': fmt_date,
                    'Match Score': 'N/A',
                    'Source': 'Historical Backfill',
                    'Job Link': app.get('job_posting_url', '') if pd.notnull(app.get('job_posting_url')) else '',
                    'Gmail': gmail_link
                })
                
        if display_rows:
            display_df = pd.DataFrame(display_rows)
            display_df.insert(0, 'Sr No', range(1, len(display_df) + 1))
            
            if "jobs_editor_version" not in st.session_state:
                st.session_state["jobs_editor_version"] = 0
            jobs_ver = st.session_state["jobs_editor_version"]
            jobs_key = f"overview_jobs_{jobs_ver}"

            with st.form("overview_jobs_editor"):
                st.caption("You can edit and delete jobs directly here. Changes are routed to their original source table.")
                edited_df = st.data_editor(
                    display_df,
                    hide_index=True,
                    num_rows="dynamic",
                    width="stretch",
                    key=jobs_key,
                    column_config={
                        "_id": None, 
                        "_source_table": None, 
                        "Sr No": st.column_config.NumberColumn(disabled=True),
                        "Source": st.column_config.TextColumn(disabled=True),
                        "Match Score": st.column_config.TextColumn(disabled=True),
                        "Job Link": st.column_config.LinkColumn("Job Posting", display_text="🔗 View Posting", disabled=True),
                        "Gmail": st.column_config.LinkColumn("Gmail Search", display_text="📧 Search Gmail", disabled=True)
                    }
                )
                
                if st.form_submit_button("💾 Save Changes", type="primary"):
                    changes = st.session_state.get(jobs_key, {})
                    if any(len(v) > 0 for v in changes.values() if isinstance(v, (list, dict))):
                        from myproject.data_loader import get_supabase_client
                        client = get_supabase_client()
                        if not client:
                            st.error("Not connected to Supabase.")
                        else:
                            try:
                                # Deletes
                                for idx in changes.get("deleted_rows", []):
                                    row = display_df.iloc[idx]
                                    if pd.notna(row['_id']):
                                        target_id = int(float(row['_id']))
                                        client.table(row['_source_table']).delete().eq('id', target_id).execute()

                                # Updates
                                for idx_val, edits in changes.get("edited_rows", {}).items():
                                    idx = int(idx_val)
                                    row = display_df.iloc[idx]
                                    source_tbl = str(row['_source_table'])
                                    if pd.isna(row['_id']): continue
                                    target_id = int(float(row['_id']))
                                    
                                    clean_edits = {}
                                    for k, v in edits.items():
                                        db_val = None if pd.isna(v) else v
                                        if k == 'Company': clean_edits['company'] = db_val
                                        elif k == 'Status': clean_edits['status'] = db_val
                                        elif k == 'Applied Date':
                                            if db_val == "": continue
                                            col = 'first_seen_at' if source_tbl == 'jobs' else 'applied_at'
                                            clean_edits[col] = db_val
                                        elif k == 'Role':
                                            col = 'job_title' if source_tbl == 'jobs' else 'role_title'
                                            clean_edits[col] = db_val
                                        elif k == 'Job Link':
                                            col = 'job_url' if source_tbl == 'jobs' else 'job_posting_url'
                                            clean_edits[col] = db_val

                                    if clean_edits:
                                        client.table(source_tbl).update(clean_edits).eq('id', target_id).execute()
                                
                                st.session_state.pop(jobs_key, None)
                                st.session_state["jobs_editor_version"] = jobs_ver + 1
                                st.cache_data.clear()
                                if changes.get("added_rows"):
                                    st.warning("Adding new jobs from this view is not supported. Use the Database Manager. Edits/Deletes were saved.")
                                else:
                                    st.toast("✅ Saved changes!")
                                    st.rerun()
                            except Exception as exc:
                                logger.error(
                                    "Saving job editor changes failed: error_type=%s",
                                    type(exc).__name__,
                                )
                                st.error(
                                    "Unable to save job changes right now. "
                                    "Please retry in a moment."
                                )
                    else:
                        st.info("No changes to save.")
        else:
            st.info("No jobs found.")
            
    elif selected_drilldown == "🏢 View Unique Companies":
        companies = []
        if not df.empty and 'company' in df.columns:
            companies.extend(df['company'].dropna().tolist())
            
        if apps_df is not None and not apps_df.empty and 'company' in apps_df.columns:
            hist_apps = apps_df[~apps_df['job_id'].isin(df['id'])] if 'job_id' in apps_df.columns and not df.empty else apps_df
            companies.extend(hist_apps['company'].dropna().tolist())
            
        if companies:
            company_counts = pd.Series(companies).value_counts().reset_index()
            company_counts.columns = ['Company Name', 'Number of Jobs Tracked']
            company_counts.insert(0, 'Sr No', range(1, len(company_counts) + 1))
            st.dataframe(company_counts, hide_index=True, width="stretch")
        else:
            st.info("No companies found.")
            
    elif selected_drilldown == "👀 View Active / Pending":
        render_pending_diagnostics_component(df, apps_df)
            
    elif selected_drilldown == "🎤 View Interviews":
        display_rows = []
        
        if events_df is not None and not events_df.empty and 'event_type' in events_df.columns:
            # 1. Find all historical events that indicate an interview
            interview_events = events_df[events_df['event_type'].astype(str).str.lower().isin(['recruiter call', 'interviewing', 'offer', 'offer received', 'hired'])]
            
            if 'application_id' in interview_events.columns and not interview_events.empty:
                # Aggregate to get latest interview date and round count
                agg_interviews = interview_events.groupby('application_id').agg(
                    interview_date=('event_date', 'max'),
                    round_level=('id', 'count')
                ).reset_index()
                
                # Get the unique applications from events_df to pull their base info
                unique_apps = interview_events.drop_duplicates(subset=['application_id']).copy()
                unique_apps = unique_apps.merge(agg_interviews, on='application_id', how='left')
                
                for _, app in unique_apps.iterrows():
                    # Check if this app is actively tracked in jobs_df
                    job_id = app.get('job_id')
                    if pd.notnull(job_id) and not df.empty:
                        job_id_mask = df['id'] == job_id
                        if '_source_table' in df.columns:
                            job_id_mask &= (df['_source_table'] == 'jobs')
                        live_job = df[job_id_mask]
                    else:
                        live_job = pd.DataFrame()
                    
                    if not live_job.empty:
                        job_row = live_job.iloc[0]
                        company = job_row.get('company', 'Unknown')
                        role = job_row.get('job_title', 'Unknown')
                        status = str(job_row.get('status', 'Unknown')).title()
                        job_link = job_row.get('job_url', '')
                        rejection_reason = app.get('rejection_reason', '')
                    else:
                        company = app.get('company', 'Unknown')
                        role = app.get('role_title', 'Unknown')
                        status_val = app.get('status_app') if 'status_app' in unique_apps.columns else app.get('status', 'Unknown')
                        status = str(status_val).title()
                        job_link = app.get('job_posting_url', '')
                        rejection_reason = app.get('rejection_reason', '')
                    
                    if pd.isna(job_link): job_link = ''
                    if pd.isna(rejection_reason): rejection_reason = ''
                    
                    raw_date = app.get('interview_date')
                    fmt_date = pd.to_datetime(raw_date).strftime('%Y-%m-%d') if pd.notnull(raw_date) else ''
                    
                    encoded_query = urllib.parse.quote(f"{company} {role}")
                    gmail_link = f"https://mail.google.com/mail/u/0/#search/{encoded_query}"
                    
                    # IMPORTANT: When live_job is empty, the authoritative record to UPDATE
                    # is always job_applications (not job_application_events).
                    # app.get('id') here is the event's ID from job_application_events;
                    # app.get('application_id') is the job_applications.id we must target.
                    if not live_job.empty:
                        source_tbl = 'jobs'
                        rec_id = job_row.get('id')
                    else:
                        source_tbl = 'job_applications'
                        rec_id = app.get('application_id')  # FK into job_applications.id

                    display_rows.append({
                        '_id': rec_id,
                        '_source_table': source_tbl,
                        '_job_id': app.get('job_id') if not live_job.empty else None,  # jobs.id for cross-sync
                        'Company': str(company),
                        'Role': str(role),
                        'Status': str(status),
                        'Round': str(app.get('round_level', '1')),
                        'Interview Date': str(fmt_date),
                        'Rejection Reason': str(rejection_reason),
                        'Job Link': str(job_link),
                        'Gmail': str(gmail_link)
                    })
        
        # 2. Append any live interviews that might not have historical events (e.g. manually added)
        jobs_only_df = df[df['_source_table'] == 'jobs'] if '_source_table' in df.columns else df
        live_interviews = jobs_only_df[jobs_only_df['status'].str.lower().isin(['recruiter call', 'interviewing', 'offer', 'offer received', 'hired'])]
        processed_companies = [r['Company'] for r in display_rows]
        for _, job in live_interviews.iterrows():
            company = job.get('company', 'Unknown')
            role = job.get('job_title', 'Unknown')
            if company not in processed_companies:
                job_link = job.get('job_url', '')
                if pd.isna(job_link): job_link = ''
                
                encoded_query = urllib.parse.quote(f"{company} {role}")
                gmail_link = f"https://mail.google.com/mail/u/0/#search/{encoded_query}"
                
                display_rows.append({
                        '_id': job.get('id'),
                        '_source_table': 'jobs',
                        '_job_id': job.get('id'),  # same as _id for live jobs
                        'Company': str(company),
                        'Role': str(role),
                        'Status': str(job.get('status', 'Unknown')).title(),
                        'Round': 'Manual',
                        'Interview Date': '',
                        'Rejection Reason': '',
                        'Job Link': str(job_link),
                        'Gmail': str(gmail_link)
                    })
                
        if display_rows:
            display_df = pd.DataFrame(display_rows)

            # st.data_editor doesn't support click-to-sort on headers (it would
            # desync the row-index-based edited_rows/added_rows tracking), so
            # sorting is exposed as explicit controls instead.
            sort_col, asc_col = st.columns([3, 1])
            with sort_col:
                sort_by = st.selectbox(
                    "Sort by",
                    ["Interview Date", "Company", "Role", "Status", "Round"],
                    key="interviews_sort_by"
                )
            with asc_col:
                sort_ascending = st.checkbox("Ascending", value=False, key="interviews_sort_asc")

            if sort_by == "Interview Date":
                display_df['_sort_key'] = pd.to_datetime(display_df['Interview Date'], errors='coerce')
            elif sort_by == "Round":
                display_df['_sort_key'] = pd.to_numeric(display_df['Round'], errors='coerce')
            else:
                display_df['_sort_key'] = display_df[sort_by].astype(str).str.lower()
            display_df = display_df.sort_values('_sort_key', ascending=sort_ascending, na_position='last').drop(columns=['_sort_key']).reset_index(drop=True)

            display_df.insert(0, 'Sr No', range(1, len(display_df) + 1))

            if "editor_version" not in st.session_state:
                st.session_state["editor_version"] = 0
            editor_ver = st.session_state["editor_version"]
            editor_key = f"data_editor_grid_{editor_ver}"

            with st.form("overview_interviews_editor"):
                st.caption("Double-click any cell to update status, interview date, or notes. Save changes to sync to Supabase.")
                edited_df = st.data_editor(
                    display_df,
                    hide_index=True,
                    num_rows="dynamic",
                    width="stretch",
                    key=editor_key,
                    disabled=["Sr No", "Job Link", "Gmail"],
                    column_config={
                        "_id": None,
                        "_source_table": None,
                        "_job_id": None,
                        "Sr No": st.column_config.NumberColumn(disabled=True),
                        "Company": st.column_config.TextColumn("Company"),
                        "Role": st.column_config.TextColumn("Role"),
                        "Status": st.column_config.SelectboxColumn("Status", options=STATUS_OPTIONS),
                        "Round": st.column_config.TextColumn("Round"),
                        "Interview Date": st.column_config.TextColumn("Interview Date"),
                        "Rejection Reason": st.column_config.TextColumn("Rejection Reason / Notes"),
                        "Job Link": st.column_config.LinkColumn("Job Posting", display_text="🔗 View Posting", disabled=True),
                        "Gmail": st.column_config.LinkColumn("Gmail Search", display_text="📧 Search Gmail", disabled=True)
                    }
                )
                
                if st.form_submit_button("💾 Save Interview Changes", type="primary"):
                    changes = st.session_state.get(editor_key, {})
                    if not changes or not any(len(v) > 0 for v in changes.values() if isinstance(v, (list, dict))):
                        for k in list(st.session_state.keys()):
                            if (k.startswith("data_editor_grid_") or k.startswith("interviews_grid_") or k.startswith("overview_interviews_") or k in ["interviews_editor", "jobs_editor"]) and isinstance(st.session_state[k], dict):
                                candidate_changes = st.session_state[k]
                                if any(len(v) > 0 for v in candidate_changes.values() if isinstance(v, (list, dict))):
                                    changes = candidate_changes
                                    break
                    if any(len(v) > 0 for v in changes.values() if isinstance(v, (list, dict))):
                        from myproject.data_loader import get_supabase_client
                        client = get_supabase_client()
                        logger.info(
                            "Saving interview editor changes: updates=%s deletes=%s additions=%s",
                            len(changes.get("edited_rows", {})),
                            len(changes.get("deleted_rows", [])),
                            len(changes.get("added_rows", [])),
                        )
                        try:
                            # Deletes
                            for idx_val in changes.get("deleted_rows", []):
                                idx = int(idx_val)
                                row = display_df.iloc[idx]
                                if pd.notna(row['_id']):
                                    target_id = int(float(row['_id']))
                                    source_tbl = str(row['_source_table'])
                                    if client:
                                        client.table(source_tbl).delete().eq('id', target_id).execute()
                                        logger.info(
                                            "Deleted interview record: table=%s id=%s",
                                            source_tbl,
                                            target_id,
                                        )

                            # Updates
                            for idx_val, edits in changes.get("edited_rows", {}).items():
                                idx = int(idx_val)
                                row = display_df.iloc[idx]
                                source_tbl = str(row['_source_table'])

                                raw_id = row.get('_id') if pd.notna(row.get('_id')) else (row.get('id') if pd.notna(row.get('id')) else row.get('job_id'))
                                if pd.isna(raw_id) or raw_id is None:
                                    continue
                                target_id = int(float(raw_id))
                                # _job_id is jobs.id for cross-table status sync; may differ from target_id
                                raw_job_id = row.get('_job_id')
                                linked_job_id = int(float(raw_job_id)) if (raw_job_id is not None and pd.notna(raw_job_id)) else None

                                clean_edits = {}
                                for k, v in edits.items():
                                    db_val = None if pd.isna(v) else v
                                    if k == 'Company': clean_edits['company'] = db_val
                                    elif k == 'Status': clean_edits['status'] = db_val
                                    elif k in ['Rejection Reason', 'Notes', 'Notes / Evidence']:
                                        if source_tbl == 'jobs':
                                            clean_edits['match_analysis'] = db_val
                                        else:
                                            clean_edits['rejection_reason'] = db_val
                                    elif k == 'Role':
                                        col = 'job_title' if source_tbl == 'jobs' else 'role_title'
                                        clean_edits[col] = db_val
                                    elif k == 'Job Link':
                                        col = 'job_url' if source_tbl == 'jobs' else 'job_posting_url'
                                        clean_edits[col] = db_val
                                    elif k == 'Interview Date':
                                        if source_tbl == 'job_application_events':
                                            clean_edits['event_date'] = db_val
                                        elif source_tbl == 'jobs':
                                            clean_edits['first_seen_at'] = db_val
                                        else:
                                            clean_edits['applied_at'] = db_val

                                if clean_edits:
                                    changed_fields = sorted(clean_edits)
                                    # job_applications has a CHECK constraint requiring lowercase status values.
                                    # jobs table accepts any case, so we only normalize for job_applications.
                                    if source_tbl == 'job_applications' and 'status' in clean_edits and clean_edits['status']:
                                        clean_edits['status'] = clean_edits['status'].lower()

                                    if client:
                                        try:
                                            res = client.table(source_tbl).update(clean_edits).eq('id', target_id).select('id,status').execute()

                                            # Sync status change to main 'jobs' table when source is job_applications.
                                            # Use linked_job_id (jobs.id) — NOT target_id (job_applications.id).
                                            if source_tbl != 'jobs' and clean_edits.get('status') and linked_job_id:
                                                try:
                                                    client.table('jobs').update({'status': clean_edits['status']}).eq('id', linked_job_id).select('id,status').execute()
                                                except Exception as parent_sync_err:
                                                    logger.warning(
                                                        "Parent job status sync failed: jobs.id=%s error_type=%s",
                                                        linked_job_id,
                                                        type(parent_sync_err).__name__,
                                                    )

                                            if hasattr(res, 'data') and (res.data is None or len(res.data) == 0):
                                                warn_msg = (
                                                    "⚠️ The database did not confirm this update. "
                                                    "The record may be missing or blocked by access policy."
                                                )
                                                logger.warning(
                                                    "Interview update returned no rows: table=%s id=%s fields=%s",
                                                    source_tbl,
                                                    target_id,
                                                    changed_fields,
                                                )
                                                st.warning(warn_msg)
                                            else:
                                                logger.info(
                                                    "Updated interview record: table=%s id=%s fields=%s",
                                                    source_tbl,
                                                    target_id,
                                                    changed_fields,
                                                )
                                        except Exception as update_err:
                                            logger.error(
                                                "Interview update failed: table=%s id=%s fields=%s error_type=%s",
                                                source_tbl,
                                                target_id,
                                                changed_fields,
                                                type(update_err).__name__,
                                            )
                                            if "PGRST204" in str(update_err):
                                                err_msg = str(update_err)
                                                for bad_col in ['notes', 'interview_date', 'match_analysis', 'rejection_reason', 'is_manually_overridden']:
                                                    if bad_col in err_msg:
                                                        clean_edits.pop(bad_col, None)
                                                if clean_edits:
                                                    fallback_fields = sorted(clean_edits)
                                                    res = client.table(source_tbl).update(clean_edits).eq('id', target_id).select('id,status').execute()
                                                    if hasattr(res, 'data') and (res.data is None or len(res.data) == 0):
                                                        warn_msg = (
                                                            "⚠️ The database did not confirm this update. "
                                                            "The record may be missing or blocked by access policy."
                                                        )
                                                        logger.warning(
                                                            "Interview fallback update returned no rows: table=%s id=%s fields=%s",
                                                            source_tbl,
                                                            target_id,
                                                            fallback_fields,
                                                        )
                                                        st.warning(warn_msg)
                                                    else:
                                                        logger.info(
                                                            "Updated interview record with schema fallback: table=%s id=%s fields=%s",
                                                            source_tbl,
                                                            target_id,
                                                            fallback_fields,
                                                        )
                                            else:
                                                raise update_err

                            for k in list(st.session_state.keys()):
                                if k.startswith("data_editor_grid_") or k.startswith("interviews_grid_") or k.startswith("overview_interviews_"):
                                    st.session_state.pop(k, None)
                            st.session_state["editor_version"] = editor_ver + 1
                            st.cache_data.clear()
                            st.success("Successfully updated Supabase!")
                            st.toast("✅ Saved interview changes!")
                            st.rerun()
                        except Exception as save_err:
                            logger.error(
                                "Saving interview changes failed: error_type=%s",
                                type(save_err).__name__,
                            )
                            st.error(
                                "Unable to save interview changes right now. "
                                "Please retry in a moment."
                            )
                    else:
                        st.info("No changes to save.")
        else:
            st.info("No Interviewing applications found.")

