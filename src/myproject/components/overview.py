import streamlit as st
import pandas as pd

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
    st.subheader("Job Pipeline Overview")

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
    else:
        total_interviews = len(df[df['status'].str.lower().isin(['interviewing', 'offer', 'offer received', 'hired'])]) if 'status' in df.columns else 0

    # Custom HTML Flexbox KPI Cards
    kpi_html = f"""
    <style>
    .kpi-container {{ display: flex; gap: 10px; margin-bottom: 20px; }}
    .kpi-card {{ 
        flex: 1; padding: 15px; border-radius: 8px; color: white; 
        text-align: center; font-family: sans-serif;
    }}
    .kpi-card .kpi-title {{ font-size: 0.9em; opacity: 0.9; margin-bottom: 5px; }}
    .kpi-card .kpi-value {{ font-size: 1.8em; font-weight: bold; margin-bottom: 5px; line-height: 1.2; }}
    .kpi-card .kpi-desc {{ font-size: 0.75em; opacity: 0.8; line-height: 1.2; }}
    
    .bg-indigo {{ background-color: #6366f1; }}
    .bg-rose {{ background-color: #f43f5e; }}
    .bg-amber {{ background-color: #f59e0b; }}
    .bg-blue {{ background-color: #3b82f6; }}
    .bg-emerald {{ background-color: #10b981; }}
    </style>
    <div class="kpi-container">
        <div class="kpi-card bg-indigo">
            <div class="kpi-title">📊 Total Jobs</div>
            <div class="kpi-value">{total_tracked}</div>
            <div class="kpi-desc">Tracked in pipeline</div>
        </div>
        <div class="kpi-card bg-rose">
            <div class="kpi-title">🎯 Avg Match</div>
            <div class="kpi-value">{avg_match:.1f}%</div>
            <div class="kpi-desc">ATS screen pass rate</div>
        </div>
        <div class="kpi-card bg-amber">
            <div class="kpi-title">🏢 Companies</div>
            <div class="kpi-value">{total_companies}</div>
            <div class="kpi-desc">Distinct employers</div>
        </div>
        <div class="kpi-card bg-blue">
            <div class="kpi-title">⏳ Active/Pending</div>
            <div class="kpi-value">{pending_count}</div>
            <div class="kpi-desc">Awaiting decision</div>
        </div>
        <div class="kpi-card bg-emerald">
            <div class="kpi-title">🎤 Interviews</div>
            <div class="kpi-value">{total_interviews}</div>
            <div class="kpi-desc">Reached interview stage</div>
        </div>
    </div>
    """
    st.markdown(kpi_html, unsafe_allow_html=True)
    # KPI Drilldown using st.pills
    drilldown_options = ["Hide Table", "💼 View All Jobs", "🏢 View Unique Companies", "👀 View Active / Pending", "🎤 View Interviews"]
    selected_drilldown = st.pills("Drill down into KPIs:", drilldown_options, default="Hide Table")
    
    if selected_drilldown == "💼 View All Jobs":
        import urllib.parse
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
                        "Job Link": st.column_config.LinkColumn("Job Link"),
                        "Gmail": st.column_config.LinkColumn("Gmail Search", display_text="📧 Search Gmail")
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
                                    client.table(row['_source_table']).delete().eq('id', row['_id']).execute()

                                # Updates
                                for idx, edits in changes.get("edited_rows", {}).items():
                                    row = display_df.iloc[idx]
                                    source_tbl = row['_source_table']
                                    
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
                                        client.table(source_tbl).update(clean_edits).eq('id', row['_id']).execute()
                                
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
                
                display_rows.append({
                    'Company': app.get('company', 'Unknown'),
                    'Role': app.get('role_title', 'Unknown'),
                    'Status': str(app.get('status', 'Unknown')).title(),
                    'Applied Date': fmt_date,
                    'Days Since Applied': days_since,
                    'Job Link': job_link
                })
                
        if display_rows:
            display_df = pd.DataFrame(display_rows)
            
            # Overwrite Status for ghosted applications
            # Handle empty strings by converting to numeric and coercing errors to NaN
            display_df['numeric_days'] = pd.to_numeric(display_df['Days Since Applied'], errors='coerce')
            display_df.loc[display_df['numeric_days'] > 20, 'Status'] = 'Ghosted'
            
            # Default Sort: Oldest applications first (most days since applied)
            display_df = display_df.sort_values('numeric_days', ascending=False, na_position='last').drop(columns=['numeric_days'])
            
            display_df.insert(0, 'Sr No', range(1, len(display_df) + 1))
            cols = ['Sr No', 'Company', 'Role', 'Status', 'Applied Date', 'Days Since Applied', 'Job Link']
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
                    "Job Link": st.column_config.LinkColumn("Job Link")
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
                    
                    display_rows.append({
                        'Company': company,
                        'Role': role,
                        'Status': status,
                        'Round': app.get('round_level', 1),
                        'Interview Date': fmt_date,
                        'Rejection Reason': rejection_reason,
                        'Job Link': job_link
                    })
        
        # 2. Append any live interviews that might not have historical events (e.g. manually added)
        live_interviews = df[df['status'].str.lower().isin(['interviewing', 'offer', 'offer received', 'hired'])]
        processed_companies = [r['Company'] for r in display_rows]
        for _, job in live_interviews.iterrows():
            company = job.get('company', 'Unknown')
            if company not in processed_companies:
                job_link = job.get('job_url', '')
                if pd.isna(job_link): job_link = ''
                
                display_rows.append({
                    'Company': company,
                    'Role': job.get('job_title', 'Unknown'),
                    'Status': str(job.get('status', 'Unknown')).title(),
                    'Round': 'Manual',
                    'Interview Date': '',
                    'Rejection Reason': '',
                    'Job Link': job_link
                })
                
        if display_rows:
            display_df = pd.DataFrame(display_rows)
            
            # Default Sort: Newest interviews first
            display_df['sort_date'] = pd.to_datetime(display_df['Interview Date'], errors='coerce')
            display_df = display_df.sort_values('sort_date', ascending=False, na_position='last').drop(columns=['sort_date'])
            
            display_df.insert(0, 'Sr No', range(1, len(display_df) + 1))
            cols = ['Sr No', 'Company', 'Role', 'Status', 'Round', 'Interview Date', 'Rejection Reason', 'Job Link']
            display_cols = [c for c in cols if c in display_df.columns]
            
            st.dataframe(
                display_df[display_cols],
                hide_index=True,
                width="stretch",
                column_config={
                    "Job Link": st.column_config.LinkColumn("Job Link")
                }
            )
        else:
            st.info("No Interviewing applications found.")
            
    st.markdown("---")
    st.subheader("Recent Activity")
    st.caption("💡 Deduplicates historical events to show the latest, most actionable status for each application.")
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
            events_view = events_df.sort_values(by=date_col, ascending=False)
            
            # Collapse sprawl by keeping only the most recent update per application
            if 'application_id' in events_view.columns:
                events_view = events_view.drop_duplicates(subset=['application_id'], keep='first')
            
            # Apply filter
            if filter_option == "Interviewing Only":
                events_view = events_view[events_view[desc_col].astype(str).str.lower() == 'interviewing']
            elif filter_option == "Positive Signals Only":
                events_view = events_view[events_view[desc_col].astype(str).str.lower().isin(['interviewing', 'offer', 'offer received', 'hired'])]
                
            events_view = events_view.head(15)
            
            if events_view.empty:
                st.info(f"No events match the filter: {filter_option}")
            else:
                table_data = []
                for idx, (_, event) in enumerate(events_view.iterrows(), 1):
                    # Build context string
                    company = event.get('company', 'Unknown')
                    role = event.get('role_title', 'Unknown')
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
                        
                    date_val = pd.to_datetime(event[date_col])
                    now = pd.Timestamp.now('UTC') if date_val.tzinfo is not None else pd.Timestamp.now()
                    days_ago = (now - date_val).days
                    staleness = f"⏳ {days_ago}d" if days_ago > 0 else "⏳ Today"
                    
                    evidence = event.get('evidence_snippet', '')
                    if pd.isna(evidence):
                        evidence = ''
                        
                    table_data.append({
                        "Sr No": idx,
                        "Staleness": staleness,
                        "Company": company,
                        "Role": role,
                        "Status": badge,
                        "Notes": evidence
                    })
                
                st.dataframe(pd.DataFrame(table_data), hide_index=True, width="stretch")
        else:
            st.dataframe(events_df.head(10), width="stretch", hide_index=True)
    else:
        st.info("No recent historical events available.")
