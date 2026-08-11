import streamlit as st
import pandas as pd
import urllib.parse
from myproject.data_loader import format_staleness
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
    st.subheader(":material/dashboard: Job Pipeline Overview")

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
    
    pending_count = len(df[df['status'].str.lower().isin(['applied', 'pending', 'reviewing'])]) if 'status' in df.columns else 0
    
    if events_df is not None and not events_df.empty and 'event_type' in events_df.columns and 'application_id' in events_df.columns:
        interview_events = events_df[events_df['event_type'].astype(str).str.lower().isin(['interviewing', 'offer', 'offer received', 'hired'])]
        total_interviews = interview_events['application_id'].nunique()
        offer_events = events_df[events_df['event_type'].astype(str).str.lower().isin(['offer', 'offer received', 'hired'])]
        total_offers = offer_events['application_id'].nunique()
    else:
        total_interviews = len(df[df['status'].str.lower().isin(['interviewing', 'offer', 'offer received', 'hired'])]) if 'status' in df.columns else 0
        total_offers = len(df[df['status'].str.lower().isin(['offer', 'offer received', 'hired'])]) if 'status' in df.columns else 0

    # Calculate conversion metrics
    app_to_interview_pct = (total_interviews / total_tracked * 100) if total_tracked > 0 else 0.0
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
        <div class="kpi-card kpi-indigo">
            <div class="kpi-title">📊 Total Jobs</div>
            <div class="kpi-value">{total_tracked}</div>
            <div class="kpi-desc">Tracked in pipeline</div>
        </div>
        <div class="kpi-card kpi-rose">
            <div class="kpi-title">🎯 Avg Match</div>
            <div class="kpi-value">{avg_match:.1f}%</div>
            <div class="kpi-desc">ATS screen pass rate</div>
        </div>
        <div class="kpi-card kpi-emerald">
            <div class="kpi-title">🎤 Interviews</div>
            <div class="kpi-value">{total_interviews}</div>
            <div class="kpi-desc">Reached interview stage</div>
        </div>
        <div class="kpi-card kpi-purple">
            <div class="kpi-title">📈 App → Interview</div>
            <div class="kpi-value">{app_to_interview_pct:.1f}%</div>
            <div class="kpi-desc">{app_to_int_badge} ({total_interviews}/{total_tracked})</div>
        </div>
        <div class="kpi-card kpi-teal">
            <div class="kpi-title">🏆 Interview → Offer</div>
            <div class="kpi-value">{interview_to_offer_pct:.1f}%</div>
            <div class="kpi-desc">{int_to_off_badge} ({total_offers}/{total_interviews if total_interviews > 0 else 0})</div>
        </div>
        <div class="kpi-card kpi-blue">
            <div class="kpi-title">⏳ Active/Pending</div>
            <div class="kpi-value">{pending_count}</div>
            <div class="kpi-desc">Awaiting decision</div>
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
                '_source_table': 'jobs',
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
                            except Exception as e:
                                st.error(f"Error saving: {e}")
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
            interview_events = events_df[events_df['event_type'].astype(str).str.lower().isin(['interviewing', 'offer', 'offer received', 'hired'])]
            
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
                    live_job = df[df['id'] == job_id] if pd.notnull(job_id) and not df.empty else pd.DataFrame()
                    
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
                    
                    source_tbl = 'jobs' if not live_job.empty else ('job_application_events' if 'id' in app and pd.notnull(app.get('id')) else 'job_applications')
                    rec_id = job_row.get('id') if not live_job.empty else app.get('id', app.get('application_id'))
                    
                    display_rows.append({
                        '_id': rec_id,
                        '_source_table': source_tbl,
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
        live_interviews = df[df['status'].str.lower().isin(['interviewing', 'offer', 'offer received', 'hired'])]
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
            
            # Default Sort: Newest interviews first
            display_df['sort_date'] = pd.to_datetime(display_df['Interview Date'], errors='coerce')
            display_df = display_df.sort_values('sort_date', ascending=False, na_position='last').drop(columns=['sort_date']).reset_index(drop=True)
            
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
                        "Sr No": st.column_config.NumberColumn(disabled=True),
                        "Company": st.column_config.TextColumn("Company"),
                        "Role": st.column_config.TextColumn("Role"),
                        "Status": st.column_config.SelectboxColumn("Status", options=["Interviewing", "Offer Received", "Hired", "Rejected", "Pending", "Applied"]),
                        "Round": st.column_config.TextColumn("Round"),
                        "Interview Date": st.column_config.TextColumn("Interview Date"),
                        "Rejection Reason": st.column_config.TextColumn("Rejection Reason / Notes"),
                        "Job Link": st.column_config.LinkColumn("Job Posting", display_text="🔗 View Posting", disabled=True),
                        "Gmail": st.column_config.LinkColumn("Gmail Search", display_text="📧 Search Gmail", disabled=True)
                    }
                )
                
                if st.form_submit_button("💾 Save Interview Changes", type="primary"):
                    debug_info = {
                        "active_editor_key": editor_key,
                        "session_editor_keys": {k: str(st.session_state[k]) for k in st.session_state.keys() if "editor" in k or "grid" in k},
                        "target_record_id": None,
                        "source_table": None,
                        "update_payload": None,
                        "supabase_response": None
                    }
                    print("\n=== DEBUG: SAVE BUTTON CLICKED ===", flush=True)
                    print("SESSION KEYS:", list(st.session_state.keys()), flush=True)
                    for k in list(st.session_state.keys()):
                        if "editor" in k or "grid" in k:
                            print(f"KEY [{k}]:", st.session_state[k], flush=True)

                    changes = st.session_state.get(editor_key, {})
                    if not changes or not any(len(v) > 0 for v in changes.values() if isinstance(v, (list, dict))):
                        for k in list(st.session_state.keys()):
                            if (k.startswith("data_editor_grid_") or k.startswith("interviews_grid_") or k.startswith("overview_interviews_") or k in ["interviews_editor", "jobs_editor"]) and isinstance(st.session_state[k], dict):
                                candidate_changes = st.session_state[k]
                                if any(len(v) > 0 for v in candidate_changes.values() if isinstance(v, (list, dict))):
                                    changes = candidate_changes
                                    break
                    print("EDITED ROWS DATA:", st.session_state.get("interviews_editor", st.session_state.get("jobs_editor", changes)), flush=True)
                    if any(len(v) > 0 for v in changes.values() if isinstance(v, (list, dict))):
                        from myproject.data_loader import get_supabase_client, update_job_status_and_notes
                        client = get_supabase_client()
                        try:
                            # Deletes
                            for idx_val in changes.get("deleted_rows", []):
                                idx = int(idx_val)
                                row = display_df.iloc[idx]
                                if pd.notna(row['_id']):
                                    target_id = int(float(row['_id']))
                                    debug_info["target_record_id"] = target_id
                                    debug_info["source_table"] = str(row['_source_table'])
                                    print(f"DEBUG: Deleting row ID {target_id} from table {row['_source_table']}", flush=True)
                                    if client:
                                        res = client.table(str(row['_source_table'])).delete().eq('id', target_id).execute()
                                        debug_info["supabase_response"] = str(res)
                                        print("SUPABASE PAYLOAD & RES:", res, flush=True)

                            # Updates
                            for idx_val, edits in changes.get("edited_rows", {}).items():
                                idx = int(idx_val)
                                row = display_df.iloc[idx]
                                source_tbl = str(row['_source_table'])

                                if pd.isna(row['_id']) or row['_id'] is None:
                                    continue
                                target_id = int(float(row['_id']))

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

                                debug_info["target_record_id"] = target_id
                                debug_info["source_table"] = source_tbl
                                debug_info["update_payload"] = clean_edits
                                print(f"DEBUG: Target row ID: {target_id} | Table: {source_tbl} | Payload: {clean_edits}", flush=True)

                                if clean_edits:
                                    # Fallback update to in-memory store for session consistency
                                    update_job_status_and_notes(
                                        target_id,
                                        clean_edits.get('status'),
                                        clean_edits.get('match_analysis') or clean_edits.get('rejection_reason')
                                    )

                                    if client:
                                        try:
                                            res = client.table(source_tbl).update(clean_edits).eq('id', target_id).execute()
                                            
                                            # Sync status change to main 'jobs' table if source table was an event sub-table
                                            if source_tbl != 'jobs' and clean_edits.get('status'):
                                                try:
                                                    client.table('jobs').update({'status': clean_edits['status']}).eq('id', target_id).execute()
                                                except Exception as parent_sync_err:
                                                    print(f"DEBUG: Parent jobs table sync notice: {parent_sync_err}", flush=True)

                                            if hasattr(res, 'data') and res.data:
                                                debug_info["supabase_response"] = f"✅ Updated row ID {target_id} in {source_tbl}: {res.data}"
                                            else:
                                                debug_info["supabase_response"] = f"✅ Update query executed successfully for row ID {target_id} in {source_tbl} ({res})"
                                            print("SUPABASE PAYLOAD & RES:", res, flush=True)
                                            print("===================================\n", flush=True)
                                        except Exception as update_err:
                                            debug_info["supabase_response"] = f"Error: {update_err}"
                                            print(f"DEBUG: Supabase update error: {update_err}", flush=True)
                                            if "PGRST204" in str(update_err):
                                                err_msg = str(update_err)
                                                for bad_col in ['notes', 'interview_date', 'match_analysis', 'rejection_reason', 'is_manually_overridden']:
                                                    if bad_col in err_msg:
                                                        clean_edits.pop(bad_col, None)
                                                if clean_edits:
                                                    res = client.table(source_tbl).update(clean_edits).eq('id', target_id).execute()
                                                    if hasattr(res, 'data') and res.data:
                                                        debug_info["supabase_response"] = f"✅ Updated row ID {target_id}: {res.data}"
                                                    else:
                                                        debug_info["supabase_response"] = f"✅ Fallback update query executed for row ID {target_id} in {source_tbl} ({res})"
                                                    print("SUPABASE PAYLOAD & RES:", res, flush=True)
                                                    print("===================================\n", flush=True)
                                            else:
                                                raise update_err

                            st.session_state["save_debug_info"] = debug_info
                            for k in list(st.session_state.keys()):
                                if k.startswith("data_editor_grid_") or k.startswith("interviews_grid_") or k.startswith("overview_interviews_"):
                                    st.session_state.pop(k, None)
                            st.session_state["editor_version"] = editor_ver + 1
                            st.cache_data.clear()
                            st.success("Successfully updated Supabase!")
                            st.toast("✅ Saved interview changes!")
                            st.rerun()
                        except Exception as e:
                            st.session_state["save_debug_info"] = debug_info
                            st.error(f"Error saving changes: {e}")
                    else:
                        st.info("No changes to save.")

            if "save_debug_info" in st.session_state:
                with st.expander("🔍 Mobile Diagnostic Logs (Save Response & Payload)", expanded=True):
                    st.json(st.session_state["save_debug_info"])
        else:
            st.info("No Interviewing applications found.")


