import os
import pandas as pd
from typing import Tuple, Dict, Any, Optional
from supabase import create_client, Client

REQUIRED_COLUMNS = ['id', 'company', 'status', 'match_score', 'job_title', 'location', 'posted_at', 'description']

DEFAULT_MOCK_DATA = [
    {
        "id": 1,
        "job_title": "Senior AI Engineer",
        "company": "TechCorp Solutions",
        "status": "Applied",
        "match_score": 92,
        "location": "San Francisco, CA",
        "posted_at": "2026-08-01T10:00:00Z",
        "description": "Building scalable LLM pipelines and agentic systems."
    },
    {
        "id": 2,
        "job_title": "Full Stack Developer",
        "company": "DataFlow Inc",
        "status": "Interviewing",
        "match_score": 85,
        "location": "Remote",
        "posted_at": "2026-08-02T14:30:00Z",
        "description": "React, TypeScript, and Python FastAPI backend development."
    },
    {
        "id": 3,
        "job_title": "Data Scientist",
        "company": "Innovate Analytics",
        "status": "Applied",
        "match_score": 78,
        "location": "New York, NY",
        "posted_at": "2026-08-03T09:15:00Z",
        "description": "Predictive modeling, data visualizations, and SQL database management."
    },
    {
        "id": 4,
        "job_title": "Backend Engineer",
        "company": "CloudNative Systems",
        "status": "Offer Received",
        "match_score": 95,
        "location": "Austin, TX",
        "posted_at": "2026-07-28T16:00:00Z",
        "description": "Distributed microservices in Go and Python on Kubernetes."
    },
    {
        "id": 5,
        "job_title": "Machine Learning Engineer",
        "company": "TechCorp Solutions",
        "status": "Rejected",
        "match_score": 64,
        "location": "San Francisco, CA",
        "posted_at": "2026-07-25T11:20:00Z",
        "description": "Model training, evaluation, and edge inference optimization."
    }
]

def _get_secret_or_env(key_name: str, default: str = "") -> str:
    """Helper to fetch secret from Streamlit Cloud st.secrets or os.environ."""
    val = ""
    try:
        import streamlit as st
        # Direct key lookup (exact or lowercase)
        if key_name in st.secrets:
            val = str(st.secrets[key_name])
        elif key_name.lower() in st.secrets:
            val = str(st.secrets[key_name.lower()])
        # Section lookup [supabase]
        elif "supabase" in st.secrets:
            sec = st.secrets["supabase"]
            short_key = key_name.replace("SUPABASE_", "").lower()
            if short_key in sec:
                val = str(sec[short_key])
            elif key_name.lower() in sec:
                val = str(sec[key_name.lower()])
    except Exception:
        pass

    if not val:
        val = os.environ.get(key_name, default)

    if val and isinstance(val, str):
        # Strip accidental line breaks or quotes when pasted into cloud secrets
        val = val.strip().strip('"').strip("'").replace("\n", "").replace("\r", "").replace(" ", "")

    return val

def is_valid_supabase_config() -> Tuple[bool, str]:
    """Verify if Supabase environment variables are present and not default placeholders."""
    url = _get_secret_or_env("SUPABASE_URL")
    key = _get_secret_or_env("SUPABASE_SERVICE_ROLE_KEY") or _get_secret_or_env("SUPABASE_ANON_KEY")

    if not url or not key:
        return False, "SUPABASE_URL and SUPABASE_KEY environment variables are missing."
    if "your-project.supabase.co" in url or "your-anon-public-key" in key:
        return False, "Supabase environment variables contain default placeholders."
    return True, "Valid configuration."

def get_supabase_client() -> Optional[Client]:
    """Helper to initialize Supabase client if config is valid."""
    is_valid, _ = is_valid_supabase_config()
    if not is_valid:
        return None
    url = _get_secret_or_env("SUPABASE_URL")
    key = _get_secret_or_env("SUPABASE_SERVICE_ROLE_KEY") or _get_secret_or_env("SUPABASE_ANON_KEY")
    return create_client(url, key)

def update_job_details(job_id: int, match_analysis: str, description: str) -> bool:
    """Updates the match_analysis and description fields for a specific job."""
    client = get_supabase_client()
    if not client:
        return False
    try:
        client.table('jobs').update({
            'match_analysis': match_analysis,
            'description': description
        }).eq('id', job_id).execute()
        return True
    except Exception as e:
        print(f"Error updating job {job_id}: {e}")
        return False

def sync_table_changes(table_name: str, original_df: pd.DataFrame, changes_dict: dict) -> Tuple[bool, str]:
    """Applies edited, added, and deleted rows from st.data_editor to Supabase."""
    client = get_supabase_client()
    if not client:
        return False, "Not connected to Supabase."
    try:
        # Deletes
        for idx in changes_dict.get("deleted_rows", []):
            row_id = original_df.iloc[idx]['id']
            client.table(table_name).delete().eq('id', row_id).execute()

        # Updates
        for idx, edits in changes_dict.get("edited_rows", {}).items():
            row_id = original_df.iloc[idx]['id']
            # Convert any potential numpy/pandas types to standard Python types before sending to Supabase
            clean_edits = {k: (None if pd.isna(v) else v) for k, v in edits.items()}
            client.table(table_name).update(clean_edits).eq('id', row_id).execute()

        # Inserts
        for row in changes_dict.get("added_rows", []):
            clean_row = {k: (None if pd.isna(v) else v) for k, v in row.items()}
            # Remove 'id' if it's there as it's auto-generated
            clean_row.pop('id', None)
            client.table(table_name).insert(clean_row).execute()

        return True, "Synced successfully!"
    except Exception as e:
        return False, f"Sync error: {str(e)}"

def migrate_historical_to_live() -> Tuple[bool, str, int]:
    """Migrates all records from job_applications to jobs."""
    client = get_supabase_client()
    if not client:
        return False, "Not connected to Supabase.", 0
    try:
        # 1. Fetch all historical applications
        response = client.table('job_applications').select('*').execute()
        historical_apps = response.data
        
        if not historical_apps:
            return True, "No historical data to migrate.", 0
            
        # 2. Map and insert into jobs table
        migrated_count = 0
        for app in historical_apps:
            new_job = {
                'company': app.get('company'),
                'job_title': app.get('role_title'),
                'status': app.get('status'),
                'first_seen_at': app.get('applied_at'),
                'job_url': app.get('job_posting_url'),
                'match_analysis': app.get('match_analysis'),
                'description': app.get('description'),
                # We do not copy the 'id' so Supabase generates a new PK for 'jobs'
            }
            # Clean out None values just in case
            new_job = {k: v for k, v in new_job.items() if v is not None}
            client.table('jobs').insert(new_job).execute()
            
            # 3. Delete the migrated record from historical
            client.table('job_applications').delete().eq('id', app['id']).execute()
            migrated_count += 1
            
        return True, f"Successfully migrated {migrated_count} records.", migrated_count
    except Exception as e:
        return False, f"Migration failed: {str(e)}", 0

def sanitize_job_data(df: pd.DataFrame) -> pd.DataFrame:
    """Sanitize job dataframe to guarantee required columns and expected data types."""
    if df is None or not isinstance(df, pd.DataFrame):
        df = pd.DataFrame()

    df = df.copy()

    # Inject missing columns with default fallbacks
    defaults = {
        'id': None,
        'company': 'Unknown',
        'status': 'Pending',
        'match_score': 0.0,
        'job_title': 'Untitled Job',
        'location': 'Unspecified',
        'posted_at': None,
        'description': ''
    }

    for col, default_val in defaults.items():
        if col not in df.columns:
            df[col] = default_val

    # Clean null / NaN values in essential columns
    df['company'] = df['company'].fillna('Unknown').astype(str)
    df['status'] = df['status'].fillna('Pending').astype(str)
    df['job_title'] = df['job_title'].fillna('Untitled Job').astype(str)
    df['match_score'] = pd.to_numeric(df['match_score'], errors='coerce').fillna(0.0)

    return df

def get_mock_job_data() -> pd.DataFrame:
    """Returns fallback sample job data when Supabase is unconfigured or unreachable."""
    return sanitize_job_data(pd.DataFrame(DEFAULT_MOCK_DATA))

def load_job_data() -> Tuple[pd.DataFrame, bool, str]:
    """
    Fetch and sanitize job data from Supabase.
    Returns: (DataFrame, is_live_data: bool, status_message: str)
    """
    is_valid, msg = is_valid_supabase_config()
    if not is_valid:
        return get_mock_job_data(), False, f"Using Demo Data: {msg}"

    try:
        supabase = get_supabase_client()
        if not supabase:
            return get_mock_job_data(), False, "Using Demo Data: Supabase client init failed."

        response = supabase.table('jobs').select("*").execute()
        raw_data = pd.DataFrame(response.data or [])

        if raw_data.empty:
            return get_mock_job_data(), False, "Using Demo Data: Connected to Supabase, but 'jobs' table is empty."

        sanitized = sanitize_job_data(raw_data)
        return sanitized, True, f"Successfully loaded {len(sanitized)} live job records from Supabase."
    except Exception as e:
        error_msg = f"Using Demo Data: Failed to fetch from Supabase ({str(e)})."
        return get_mock_job_data(), False, error_msg

def fuzzy_match_applications(jobs_df: pd.DataFrame, apps_df: pd.DataFrame) -> pd.DataFrame:
    """Fuzzy match job_applications to jobs based on company and title."""
    if jobs_df.empty or apps_df.empty:
        return apps_df

    company_col = 'company' if 'company' in apps_df.columns else None
    title_col = next((c for c in ['title', 'role', 'role_title', 'job_title'] if c in apps_df.columns), None)
    
    if not company_col or not title_col:
        apps_df['job_id'] = None
        return apps_df

    jobs_copy = jobs_df.copy()
    apps_copy = apps_df.copy()
    
    jobs_copy['norm_company'] = jobs_copy['company'].astype(str).str.lower().str.strip()
    jobs_copy['norm_title'] = jobs_copy['job_title'].astype(str).str.lower().str.strip()
    
    apps_copy['norm_company'] = apps_copy[company_col].astype(str).str.lower().str.strip()
    apps_copy['norm_title'] = apps_copy[title_col].astype(str).str.lower().str.strip()
    
    if 'posted_at' in jobs_copy.columns:
        jobs_copy = jobs_copy.sort_values('posted_at', ascending=False)
        
    match_dict = {}
    company_only_dict = {}
    for _, job in jobs_copy.iterrows():
        key = (job['norm_company'], job['norm_title'])
        if key not in match_dict:
            match_dict[key] = job['id']
        if job['norm_company'] not in company_only_dict:
            company_only_dict[job['norm_company']] = job['id']
            
    def get_match(row):
        key = (row.get('norm_company'), row.get('norm_title'))
        if key in match_dict:
            return match_dict[key]
        return company_only_dict.get(row.get('norm_company'), None)

    apps_copy['job_id'] = apps_copy.apply(get_match, axis=1)
    apps_copy = apps_copy.drop(columns=['norm_company', 'norm_title'], errors='ignore')
    return apps_copy

def load_historical_data(jobs_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Fetch job_applications and job_application_events and link them."""
    is_valid, _ = is_valid_supabase_config()
    if not is_valid:
        return pd.DataFrame(), pd.DataFrame()
        
    try:
        supabase = get_supabase_client()
        if not supabase:
            return pd.DataFrame(), pd.DataFrame()
        
        apps_res = supabase.table('job_applications').select('*').execute()
        events_res = supabase.table('job_application_events').select('*').execute()
        
        apps_df = pd.DataFrame(apps_res.data or [])
        events_df = pd.DataFrame(events_res.data or [])
        
        if not apps_df.empty and not jobs_df.empty:
            apps_df = fuzzy_match_applications(jobs_df, apps_df)
            
        if not events_df.empty and not apps_df.empty:
            merge_cols = [c for c in ['id', 'company', 'role_title', 'job_id', 'status', 'job_posting_url', 'rejection_reason'] if c in apps_df.columns]
            events_df = events_df.merge(
                apps_df[merge_cols], 
                left_on='application_id', 
                right_on='id', 
                how='left',
                suffixes=('', '_app')
            )
            log_staleness_diagnostics(events_df)
            
        return apps_df, events_df
    except Exception as e:
        return pd.DataFrame(), pd.DataFrame()

def log_staleness_diagnostics(events_df: pd.DataFrame, company_filter: Optional[str] = None) -> None:
    """Diagnostic logger for application events to trace raw event_date and calculated staleness_days."""
    if events_df is None or not isinstance(events_df, pd.DataFrame) or events_df.empty or 'company' not in events_df.columns:
        return
    
    if company_filter:
        mask = events_df['company'].astype(str).str.lower().str.contains(company_filter.lower())
        target_events = events_df[mask]
    else:
        target_events = events_df
        
    if target_events.empty:
        return

    import logging
    date_col = next((c for c in ['created_at', 'event_date', 'date', 'timestamp'] if c in target_events.columns), None)
    
    for idx, row in target_events.iterrows():
        raw_date = row.get(date_col) if date_col else None
        formatted_age = format_staleness(raw_date)
        staleness_days = None
        
        if pd.notnull(raw_date):
            try:
                dt = pd.to_datetime(raw_date)
                now = pd.Timestamp.now(tz=dt.tz) if dt.tzinfo is not None else pd.Timestamp.now()
                staleness_days = (now - dt).total_seconds() / 86400.0
            except Exception:
                staleness_days = None
                
        days_str = f"{staleness_days:.2f}d" if staleness_days is not None else "N/A"
        logging.info(
            f"[DIAGNOSTIC - Event] App ID: {row.get('application_id')}, "
            f"Company: '{row.get('company')}', Raw Date: '{raw_date}', "
            f"Staleness Days: {days_str}, Formatted Age: '{formatted_age}'"
        )

def log_torc_diagnostics(events_df: pd.DataFrame) -> None:
    """Backwards compatible wrapper for Torc events diagnostic logging."""
    log_staleness_diagnostics(events_df, company_filter='torc')

def unify_job_statuses(jobs_df: pd.DataFrame, apps_df: pd.DataFrame) -> pd.DataFrame:
    """Unify the status of jobs_df with the true historical status from apps_df."""
    if jobs_df.empty or apps_df.empty or 'job_id' not in apps_df.columns or 'status' not in apps_df.columns:
        return jobs_df
    
    # Create mapping of job_id -> status from historical applications
    valid_apps = apps_df.dropna(subset=['job_id', 'status'])
    status_map = dict(zip(valid_apps['job_id'], valid_apps['status']))
    
    # Apply mapping
    jobs_df['status'] = jobs_df.apply(
        lambda row: status_map.get(row['id'], row['status']),
        axis=1
    )
    
    # Normalize string casing to ensure title case for UI 
    jobs_df['status'] = jobs_df['status'].astype(str).str.title()
    
    return jobs_df

def format_staleness(raw_value) -> str:
    """Transform raw timestamps, datetimes, or seconds into clean human-readable data age strings with UI Pro accent tokens."""
    if pd.isna(raw_value) or raw_value is None or raw_value == '':
        return "⚪ Unknown"
    
    try:
        if isinstance(raw_value, (int, float)):
            seconds = float(raw_value)
        else:
            dt = pd.to_datetime(raw_value)
            now = pd.Timestamp.now(tz=dt.tz) if dt.tzinfo is not None else pd.Timestamp.now()
            seconds = (now - dt).total_seconds()
        
        if seconds < 0:
            seconds = 0
            
        mins = int(seconds // 60)
        hours = int(seconds // 3600)
        days = int(seconds // 86400)
        
        if seconds < 60:
            return "🟢 Just now"
        elif mins < 60:
            return f"🟢 {mins}m ago"
        elif hours < 24:
            return f"🟢 {hours}h ago"
        elif days <= 2:
            return f"🟡 {days}d old"
        else:
            return f"🔴 Stale: {days}d old"
    except Exception:
        return "⚪ Unknown"

