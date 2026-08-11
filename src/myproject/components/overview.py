import streamlit as st
import pandas as pd
import urllib.parse
from myproject.data_loader import format_staleness



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
            
            with st.form("overview_jobs_editor"):
                st.caption("You can edit and delete jobs directly here. Changes are routed to their original source table.")
                edited_df = st.data_editor(
                    display_df,
                    hide_index=True,
                    num_rows="dynamic",
                    width="stretch",
                    key="overview_jobs",
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
                    changes = st.session_state.get("overview_jobs", {})
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
                                        target_id = int(row['_id'])
                                        client.table(row['_source_table']).delete().eq('id', target_id).execute()

                                # Updates
                                for idx, edits in changes.get("edited_rows", {}).items():
                                    row = display_df.iloc[idx]
                                    source_tbl = row['_source_table']
                                    if pd.isna(row['_id']): continue
                                    target_id = int(row['_id'])
                                    
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
        display_rows = []
        
        # 1. Live tracker Active/Pending jobs
        active_jobs = df[df['status'].str.lower().isin(['applied', 'pending', 'reviewing'])]
        for _, job in active_jobs.iterrows():
            job_link = job.get('job_url', '')
            if pd.isna(job_link): job_link = ''
            
            raw_date = job.get('first_seen_at')
            fmt_date = pd.to_datetime(raw_date).strftime('%Y-%m-%d') if pd.notnull(raw_date) else ''
            
            days_since = ''
            if pd.notnull(raw_date):
                days_since = (pd.Timestamp.now(tz=pd.to_datetime(raw_date).tz) - pd.to_datetime(raw_date)).days
            
            display_rows.append({
                'Company': job.get('company', 'Unknown'),
                'Role': job.get('job_title', 'Unknown'),
                'Status': str(job.get('status', 'Unknown')).title(),
                'Applied Date': fmt_date,
                'Data Age': format_staleness(raw_date),
                'Days Since Applied': days_since,
                'Job Link': job_link
            })
            
        # 2. Historical Active/Pending apps
        if apps_df is not None and not apps_df.empty:
            hist_active = apps_df[apps_df['status'].str.lower().isin(['applied', 'pending', 'reviewing'])]
            
            if 'job_id' in hist_active.columns and not active_jobs.empty:
                hist_active = hist_active[~hist_active['job_id'].isin(active_jobs['id'])]
                
            for _, app in hist_active.iterrows():
                job_link = app.get('job_posting_url', '')
                if pd.isna(job_link): job_link = ''
                
                raw_date = app.get('applied_at')
                fmt_date = pd.to_datetime(raw_date).strftime('%Y-%m-%d') if pd.notnull(raw_date) else ''
                
                days_since = ''
                if pd.notnull(raw_date):
                    days_since = (pd.Timestamp.now(tz=pd.to_datetime(raw_date).tz) - pd.to_datetime(raw_date)).days
                
                company = app.get('company', 'Unknown')
                role = app.get('role_title', 'Unknown')
                encoded_query = urllib.parse.quote(f"{company} {role}")
                gmail_link = f"https://mail.google.com/mail/u/0/#search/{encoded_query}"

                display_rows.append({
                    'Company': company,
                    'Role': role,
                    'Status': str(app.get('status', 'Unknown')).title(),
                    'Applied Date': fmt_date,
                    'Data Age': format_staleness(raw_date),
                    'Days Since Applied': days_since,
                    'Job Link': job_link,
                    'Gmail': gmail_link
                })
                
        if display_rows:
            display_df = pd.DataFrame(display_rows)
            
            # Overwrite Status for ghosted applications
            display_df['numeric_days'] = pd.to_numeric(display_df['Days Since Applied'], errors='coerce')
            display_df.loc[display_df['numeric_days'] > 20, 'Status'] = 'Ghosted'
            
            # Default Sort: Oldest applications first (most days since applied)
            display_df = display_df.sort_values('numeric_days', ascending=False, na_position='last').drop(columns=['numeric_days'])
            
            display_df.insert(0, 'Sr No', range(1, len(display_df) + 1))
            cols = ['Sr No', 'Company', 'Role', 'Status', 'Applied Date', 'Data Age', 'Job Link', 'Gmail']
            display_cols = [c for c in cols if c in display_df.columns]
            
            # Apply color coding for ghosted rows
            def highlight_ghosted(row):
                if row['Status'] == 'Ghosted':
                    return ['background-color: rgba(255, 99, 71, 0.15)'] * len(row)
                return [''] * len(row)
                
            styled_df = display_df[display_cols].style.apply(highlight_ghosted, axis=1)
            
            st.dataframe(
                styled_df,
                hide_index=True,
                width="stretch",
                column_config={
                    "Data Age": st.column_config.TextColumn(
                        "Data Age",
                        help="Elapsed time since this record was created or last updated (🟢 Fresh < 24h, 🟡 Moderate 1-2d, 🔴 Stale > 2d)"
                    ),
                    "Job Link": st.column_config.LinkColumn("Job Posting", display_text="🔗 View Posting"),
                    "Gmail": st.column_config.LinkColumn("Gmail Search", display_text="📧 Search Gmail")
                }
            )
        else:
            st.info("No Active/Pending applications found.")
            
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
            
            with st.form("overview_interviews_editor"):
                st.caption("Double-click any cell to update status, interview date, or notes. Save changes to sync to Supabase.")
                edited_df = st.data_editor(
                    display_df,
                    hide_index=True,
                    num_rows="dynamic",
                    width="stretch",
                    key="overview_interviews",
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
                    changes = st.session_state.get("overview_interviews", {})
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
                                        target_id = int(row['_id'])
                                        client.table(row['_source_table']).delete().eq('id', target_id).execute()

                                # Updates
                                for idx, edits in changes.get("edited_rows", {}).items():
                                    row = display_df.iloc[idx]
                                    source_tbl = row['_source_table']

                                    if pd.isna(row['_id']): continue
                                    target_id = int(row['_id'])

                                    clean_edits = {}
                                    for k, v in edits.items():
                                        db_val = None if pd.isna(v) else v
                                        if k == 'Company': clean_edits['company'] = db_val
                                        elif k == 'Status': clean_edits['status'] = db_val
                                        elif k == 'Rejection Reason':
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
                                            col = 'event_date' if source_tbl == 'job_application_events' else ('first_seen_at' if source_tbl == 'jobs' else 'applied_at')
                                            clean_edits[col] = db_val

                                    if clean_edits:
                                        try:
                                            client.table(source_tbl).update(clean_edits).eq('id', target_id).execute()
                                        except Exception as update_err:
                                            if "PGRST204" in str(update_err) or "rejection_reason" in str(update_err):
                                                clean_edits.pop("rejection_reason", None)
                                                if clean_edits:
                                                    client.table(source_tbl).update(clean_edits).eq('id', target_id).execute()
                                            else:
                                                raise update_err


                                st.toast("✅ Saved interview changes!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error saving: {e}")
                    else:
                        st.info("No changes to save.")
        else:
            st.info("No Interviewing applications found.")
            
    st.markdown("---")
    st.subheader("Recent Activity")
    st.caption("💡 Deduplicates historical events and groups them by company to show the latest, most actionable status.")
    if events_df is not None and not events_df.empty:
        # Filter options
        filter_option = st.selectbox(
            "Filter Activity", 
            ["All Activity", "Interviewing Only", "Positive Signals Only"],
            index=1
        )
        
        # Try to find standard columns dynamically
        date_col = next((c for c in ['created_at', 'event_date', 'date', 'timestamp'] if c in events_df.columns), None)
        desc_col = next((c for c in ['description', 'event_type', 'body', 'message', 'type'] if c in events_df.columns), None)
        
        if date_col and desc_col:
            events_view = events_df.sort_values(by=date_col, ascending=False).copy()
            
            # Collapse sprawl by keeping only the most recent update per application
            if 'application_id' in events_view.columns:
                events_view = events_view.drop_duplicates(subset=['application_id'], keep='first')
            
            # Normalize company casing for grouping (Rule: Categorical Data Casing)
            events_view['company_clean'] = events_view['company'].astype(str).str.strip().str.title()
            
            # Apply filter
            if filter_option == "Interviewing Only":
                events_view = events_view[events_view[desc_col].astype(str).str.lower() == 'interviewing']
            elif filter_option == "Positive Signals Only":
                events_view = events_view[events_view[desc_col].astype(str).str.lower().isin(['interviewing', 'offer', 'offer received', 'hired'])]
                
            events_view = events_view.head(20)
            
            if events_view.empty:
                st.info(f"No events match the filter: {filter_option}")
            else:
                # Hierarchical pandas groupby by Company
                grouped_events = events_view.groupby('company_clean', sort=False)
                
                for company_name, group in grouped_events:
                    # Clean Streamlit typography token header for Company
                    st.markdown(f"#### 🏢 {company_name}")
                    
                    group_rows = []
                    for idx, (_, event) in enumerate(group.iterrows(), 1):
                        raw_status = str(event[desc_col]).lower()
                        
                        # Determine Badge
                        if raw_status == 'interviewing':
                            badge = "🟢 Interviewing"
                        elif raw_status in ['rejected', 'rejection']:
                            badge = "🔴 Rejected"
                        elif raw_status in ['applied', 'pending']:
                            badge = "🔵 Applied"
                        elif raw_status in ['offer', 'offer received']:
                            badge = "🟡 Offer"
                        else:
                            badge = f"⚪ {raw_status.title()}"
                            
                        date_val = event[date_col]
                        data_age_badge = format_staleness(date_val)
                        
                        evidence = event.get('evidence_snippet', '')
                        if pd.isna(evidence):
                            evidence = ''
                            
                        group_rows.append({
                            "Sr No": idx,
                            "Role": str(event.get('role_title', 'Unknown')).title(),
                            "Status": badge,
                            "Data Age": data_age_badge,
                            "Notes": evidence
                        })
                    
                    group_df = pd.DataFrame(group_rows)
                    st.dataframe(
                        group_df,
                        hide_index=True,
                        width="stretch",
                        column_config={
                            "Data Age": st.column_config.TextColumn(
                                "Data Age",
                                help="Elapsed time since last activity update"
                            ),
                            "Status": st.column_config.TextColumn("Status"),
                            "Notes": st.column_config.TextColumn("Notes / Evidence")
                        }
                    )
        else:
            st.dataframe(events_df.head(10), width="stretch", hide_index=True)
    else:
        st.info("No recent historical events available.")
