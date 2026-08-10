import datetime
import streamlit as st
import pandas as pd
from typing import Tuple
from myproject.data_loader import get_supabase_client, is_valid_supabase_config, DEFAULT_MOCK_DATA

def insert_new_job(job_data_dict: dict) -> Tuple[bool, str]:
    """
    Inserts a new job record into Supabase or session state fallback.
    """
    is_valid, _ = is_valid_supabase_config()
    
    if is_valid:
        client = get_supabase_client()
        if client:
            try:
                # Remove empty optional fields
                clean_dict = {k: v for k, v in job_data_dict.items() if v is not None and v != ''}
                client.table('jobs').insert(clean_dict).execute()
                return True, "✅ Job application saved successfully to Supabase!"
            except Exception as e:
                return False, f"Database error saving job: {str(e)}"

    # Local fallback update for demo mode
    new_id = max([j.get('id', 0) for j in DEFAULT_MOCK_DATA] + [0]) + 1
    job_data_dict['id'] = new_id
    DEFAULT_MOCK_DATA.insert(0, job_data_dict)
    
    return True, f"✅ Job application '{job_data_dict['job_title']} at {job_data_dict['company']}' added (Demo Mode)."

def render_add_job_form() -> None:
    """Renders the interactive Add New Job Application form component."""
    with st.expander("➕ Add New Job Application", expanded=False):
        st.markdown("### Record a New Job Application")
        st.caption("Fill out the details below to track a new job application in real time.")

        with st.form(key="add_new_job_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                job_title = st.text_input("Job Title*", placeholder="e.g. Senior Software Engineer")
                company = st.text_input("Company Name*", placeholder="e.g. Google")
                location = st.text_input("Location", value="Remote")
                status = st.selectbox("Application Status", ["Applied", "Interviewing", "Offer Received", "Pending", "Rejected"])
                
            with col2:
                match_score = st.slider("ATS Match Score (%)", min_value=0, max_value=100, value=80)
                job_url = st.text_input("Job Posting URL", placeholder="https://...")
                posted_at = st.date_input("Applied Date", value=datetime.date.today())

            description = st.text_area("Job Description", placeholder="Paste key responsibilities or requirements...")
            match_analysis = st.text_area("AI Match Notes / Coaching", placeholder="Notes on resume tailoring or interview prep...")

            submit_button = st.form_submit_button("💾 Save Job Application", type="primary", use_container_width=True)

            if submit_button:
                if not job_title.strip():
                    st.error("Please enter a Job Title.")
                elif not company.strip():
                    st.error("Please enter a Company Name.")
                else:
                    new_job_payload = {
                        "job_title": job_title.strip(),
                        "company": company.strip(),
                        "location": location.strip() if location.strip() else "Unspecified",
                        "status": status,
                        "match_score": float(match_score),
                        "job_url": job_url.strip() if job_url.strip() else None,
                        "posted_at": posted_at.isoformat(),
                        "description": description.strip() if description.strip() else None,
                        "match_analysis": match_analysis.strip() if match_analysis.strip() else None
                    }
                    
                    success, msg = insert_new_job(new_job_payload)
                    if success:
                        st.success(msg)
                        st.toast("🎉 Job application saved!")
                        st.rerun()
                    else:
                        st.error(msg)
