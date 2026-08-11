import streamlit as st
import pandas as pd
import urllib.parse

def render_insights(df: pd.DataFrame, apps_df: pd.DataFrame = None, key_prefix: str = "insights") -> None:
    """Render Master-Detail job insights with tabbed inspector card."""
    st.subheader(":material/insights: Job Details & Match Inspector")
    st.caption("Inspect application status, AI coaching notes, email evidence, and job descriptions in a compact master-detail view.")

    if df.empty:
        st.info("No job records available.")
        return

    # Master-Detail Split: Left selection panel (1), Right inspector card (2)
    left_col, right_col = st.columns([1, 2])

    with left_col:
        st.markdown("### 📋 Select Application")
        search_q = st.text_input("🔍 Quick Search", "", placeholder="Search company or title...", key=f"{key_prefix}_search")
        
        filtered_view = df.copy()
        if search_q.strip():
            sq = search_q.strip().lower()
            mask = (
                filtered_view['job_title'].astype(str).str.lower().str.contains(sq) |
                filtered_view['company'].astype(str).str.lower().str.contains(sq)
            )
            filtered_view = filtered_view[mask]

        if not filtered_view.empty:
            job_options = {f"{row['company']} - {row['job_title']}": idx for idx, row in filtered_view.iterrows()}
            selected_job_label = st.radio(
                "Select job to inspect:",
                list(job_options.keys()),
                label_visibility="collapsed",
                key=f"{key_prefix}_radio"
            )
            selected_idx = job_options[selected_job_label]
            selected_job = filtered_view.loc[selected_idx]


        else:
            st.warning("No applications match your search.")
            selected_job = None

    with right_col:
        if selected_job is not None:
            with st.container(border=True):
                st.markdown(f"### 📌 {selected_job['job_title']} at {selected_job['company']}")
                
                ic1, ic2, ic3 = st.columns(3)
                with ic1:
                    st.markdown(f"**Status:** `{selected_job['status']}`")
                with ic2:
                    st.markdown(f"**Match Score:** `{selected_job['match_score']}%`")
                with ic3:
                    st.markdown(f"**Location:** `{selected_job.get('location', 'N/A')}`")

                # Lookup Gmail Thread ID, Message ID, Job URL, and Evidence Snippet from historical apps
                gmail_thread_id = None
                gmail_message_id = None
                evidence_snippet = None
                job_url = selected_job.get('job_url')

                if apps_df is not None and not apps_df.empty:
                    app_matches = pd.DataFrame()
                    if 'id' in apps_df.columns:
                        app_matches = apps_df[apps_df['id'] == selected_job['id']]
                    if app_matches.empty and 'job_id' in apps_df.columns:
                        app_matches = apps_df[apps_df['job_id'] == selected_job['id']]
                        
                    if not app_matches.empty:
                        matched_row = app_matches.iloc[0]
                        gmail_thread_id = matched_row.get('gmail_thread_id')
                        gmail_message_id = matched_row.get('gmail_message_id')
                        evidence_snippet = matched_row.get('evidence_snippet')
                        if not job_url or pd.isna(job_url):
                            job_url = matched_row.get('job_posting_url')

                # Construct Native Gmail App Deep Link & Web Link
                if gmail_thread_id and pd.notna(gmail_thread_id) and str(gmail_thread_id).strip():
                    tid = str(gmail_thread_id).strip()
                    gmail_web_url = f"https://mail.google.com/mail/u/0/#all/{tid}"
                    gmail_app_url = f"googlegmail:///thread/{tid}"
                    app_btn_label = "📱 Native Gmail"
                    web_btn_label = "🌐 Web Gmail"
                elif gmail_message_id and pd.notna(gmail_message_id) and str(gmail_message_id).strip():
                    mid = str(gmail_message_id).strip()
                    gmail_web_url = f"https://mail.google.com/mail/u/0/#search/rfc822msgid%3A{mid}"
                    gmail_app_url = f"googlegmail:///search?q=rfc822msgid%3A{mid}"
                    app_btn_label = "📱 Native Gmail"
                    web_btn_label = "🌐 Web Gmail"
                else:
                    query = f"{selected_job['company']} {selected_job['job_title']}"
                    encoded_query = urllib.parse.quote_plus(query)
                    gmail_web_url = f"https://mail.google.com/mail/u/0/#search/{encoded_query}"
                    gmail_app_url = f"googlegmail:///co?q={encoded_query}"
                    app_btn_label = "📱 Search App"
                    web_btn_label = "🌐 Search Web"

                st.write("")
                btn_col1, btn_col2, btn_col3 = st.columns(3)
                with btn_col1:
                    st.link_button(app_btn_label, gmail_app_url, type="primary", width="stretch")
                with btn_col2:
                    st.link_button(web_btn_label, gmail_web_url, type="secondary", width="stretch")
                with btn_col3:
                    if job_url and pd.notna(job_url) and str(job_url).strip():
                        st.link_button("🔗 Job Posting", str(job_url).strip(), type="secondary", width="stretch")
                    else:
                        st.caption("No direct posting URL.")

                st.write("")
                # Manual Status Override Edit Drawer
                with st.expander("✏️ Manual Status Override & Interview Notes", expanded=False):
                    with st.form(key=f"{key_prefix}_inline_edit_form_{selected_job['id']}"):

                        status_options = ["Applied", "Reviewing", "Interviewing", "Offer Received", "Rejected", "Hired"]
                        curr_status = str(selected_job.get('status', 'Applied')).title()
                        curr_idx = status_options.index(curr_status) if curr_status in status_options else 0

                        new_status = st.selectbox("Update Status", status_options, index=curr_idx, key=f"{key_prefix}_override_status_{selected_job['id']}")
                        new_notes = st.text_area("Interview Summary Notes", value=str(selected_job.get('match_analysis', '')), height=120, placeholder="Enter interview feedback, outcome, or next steps...", key=f"{key_prefix}_override_notes_{selected_job['id']}")

                        es_col1, es_col2 = st.columns(2)
                        with es_col1:
                            save_clicked = st.form_submit_button("💾 Save Changes", type="primary", width="stretch")
                        with es_col2:
                            cancel_clicked = st.form_submit_button("❌ Cancel", width="stretch")

                        if save_clicked:
                            from myproject.data_loader import update_job_status_and_notes
                            success = update_job_status_and_notes(selected_job['id'], new_status, new_notes)
                            if success:
                                st.toast(f"✅ Status updated to '{new_status}'!")
                                st.rerun()
                            else:
                                st.error("Failed to update database.")

                st.write("")
                # Tabbed Inspector Details (Coaching Notes, Email Evidence, Job Description)
                det_tab1, det_tab2, det_tab3 = st.tabs([
                    "💡 Coaching Notes",
                    "✉️ Email Evidence",
                    "📄 Job Description"
                ])

                analysis_text = selected_job.get('match_analysis', '')
                desc = selected_job.get('description', '')

                with det_tab1:
                    if pd.notna(analysis_text) and str(analysis_text).strip():
                        st.info(f"**How to Improve Your Score:**\n\n{analysis_text}")
                    else:
                        st.warning("No coaching notes currently saved for this application.")

                with det_tab2:
                    if evidence_snippet and pd.notna(evidence_snippet) and str(evidence_snippet).strip():
                        st.success(f"**Latest Email Evidence:**\n\n\"{evidence_snippet}\"")
                    else:
                        st.caption("No historical email proof snippets attached to this record.")

                with det_tab3:
                    if pd.notna(desc) and str(desc).strip():
                        st.text_area("Full Description Text", desc, height=180, disabled=True, label_visibility="collapsed", key=f"{key_prefix}_desc_area_{selected_job['id']}")
                    else:
                        st.caption("No description text provided.")

        else:
            st.info("Select an application from the left panel to inspect details.")


