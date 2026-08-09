import streamlit as st
import pandas as pd
import urllib.parse

def render_insights(df: pd.DataFrame, apps_df: pd.DataFrame = None) -> None:
    """Render details table and job insights."""
    st.subheader("Match Analysis & Job Details")
    st.caption("💡 **Data Source:** A raw, filterable view into the `jobs` table.")

    if df.empty:
        st.info("No job records available.")
        return

    with st.expander("📖 How to read this data", expanded=False):
        st.markdown("""
        **Using AI Match Scores to Improve:**
        - Click on any job in the list below to reveal its AI Match Analysis.
        - Use the specific coaching tips to tailor your resume's keywords and bullet points before you apply to similar roles.
        """)

    # Select columns to display
    display_cols = [c for c in ['job_title', 'company', 'status', 'match_score', 'location', 'posted_at'] if c in df.columns]

    st.write("### Applications Data")
    search_query = st.text_input("🔍 Quick Search (Title or Company)", "")

    filtered_view = df.copy()
    if search_query.strip():
        q = search_query.strip().lower()
        mask = (
            filtered_view['job_title'].astype(str).str.lower().str.contains(q) |
            filtered_view['company'].astype(str).str.lower().str.contains(q)
        )
        filtered_view = filtered_view[mask]

    st.dataframe(
        filtered_view[display_cols],
        width="stretch",
        hide_index=True
    )

    # Detailed inspector expander
    st.markdown("---")
    st.write("### Inspect Application Details")
    if not filtered_view.empty:
        job_options = {f"{row['job_title']} @ {row['company']} (ID: {row['id']})": idx for idx, row in filtered_view.iterrows()}
        selected_job_label = st.selectbox("Select job to inspect:", list(job_options.keys()))

        selected_idx = job_options[selected_job_label]
        selected_job = filtered_view.loc[selected_idx]

        with st.expander(f"📌 {selected_job['job_title']} at {selected_job['company']}", expanded=True):
            ic1, ic2, ic3 = st.columns(3)
            with ic1:
                st.write(f"**Status:** {selected_job['status']}")
            with ic2:
                st.write(f"**Match Score:** {selected_job['match_score']}%")
            with ic3:
                st.write(f"**Location:** {selected_job.get('location', 'N/A')}")

            # Lookup Job URL
            job_url = None
            if apps_df is not None and not apps_df.empty and 'job_id' in apps_df.columns:
                app_matches = apps_df[apps_df['job_id'] == selected_job['id']]
                if not app_matches.empty and 'job_posting_url' in app_matches.columns:
                    job_url = app_matches.iloc[0]['job_posting_url']

            # Construct Gmail Search URL
            query = f"{selected_job['company']} {selected_job['job_title']}"
            encoded_query = urllib.parse.quote_plus(query)
            gmail_url = f"https://mail.google.com/mail/u/0/#search/{encoded_query}"

            # Render action links
            links_html = f"""
            <div style="margin-bottom: 1rem; margin-top: 0.5rem;">
                <a href="{gmail_url}" target="_blank" style="text-decoration: none; padding: 5px 10px; background-color: #f0f2f6; border-radius: 5px; margin-right: 10px; color: #31333F; font-size: 0.9em; border: 1px solid #e0e0e0;">📧 Search Gmail</a>
            """
            if job_url and pd.notna(job_url):
                links_html += f"""
                <a href="{job_url}" target="_blank" style="text-decoration: none; padding: 5px 10px; background-color: #f0f2f6; border-radius: 5px; color: #31333F; font-size: 0.9em; border: 1px solid #e0e0e0;">🔗 View Original Job Posting</a>
                """
            links_html += "</div>"
            st.markdown(links_html, unsafe_allow_html=True)

            # AI Analysis and Coaching Block
            analysis_text = selected_job.get('match_analysis', '')
            desc = selected_job.get('description', '')
            
            is_missing_analysis = pd.isna(analysis_text) or not str(analysis_text).strip()
            is_missing_desc = pd.isna(desc) or not str(desc).strip()
            
            if is_missing_analysis or is_missing_desc:
                st.warning("⚠️ Some details are missing for this job. You can update them below.")
                with st.form(key=f"update_job_{selected_job['id']}"):
                    new_analysis = st.text_area("Match Analysis & Coaching Notes", value=str(analysis_text) if not is_missing_analysis else "", height=150)
                    new_desc = st.text_area("Job Description", value=str(desc) if not is_missing_desc else "", height=150)
                    
                    submit = st.form_submit_button("Save to Database")
                    if submit:
                        from myproject.data_loader import update_job_details
                        success = update_job_details(selected_job['id'], new_analysis, new_desc)
                        if success:
                            st.toast("✅ Job details updated successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to update job details. Check logs.")
            else:
                st.info(f"**💡 How to Improve Your Score for Upcoming Jobs:**\n\n{analysis_text}")
                st.markdown("**Job Description:**")
                st.text_area("Description", desc, height=120, disabled=True, label_visibility="collapsed")
