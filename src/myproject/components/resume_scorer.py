import streamlit as st
import pandas as pd
from myproject.resume_scorer import (
    extract_text_from_pdf,
    extract_text_from_docx,
    calculate_resume_match_score
)

def render_resume_scorer(job_data: pd.DataFrame) -> None:
    """Render the PDF resume upload & ATS Skill Match Scorer component."""
    st.subheader("📄 Resume Match Scorer & ATS Keyword Analyzer")
    st.caption("Upload your resume (PDF/DOCX) or paste resume text, and calculate your ATS match score against target job descriptions.")

    col1, col2 = st.columns([1, 1])

    resume_text = ""
    with col1:
        st.markdown("### 1. Upload Resume")
        input_mode = st.radio("Input Format", ["File Upload (PDF/DOCX)", "Paste Text"], horizontal=True)

        if input_mode == "File Upload (PDF/DOCX)":
            uploaded_file = st.file_uploader("Upload Resume File", type=["pdf", "docx"])
            if uploaded_file is not None:
                try:
                    if uploaded_file.name.lower().endswith(".pdf"):
                        resume_text = extract_text_from_pdf(uploaded_file)
                    elif uploaded_file.name.lower().endswith(".docx"):
                        resume_text = extract_text_from_docx(uploaded_file)
                    
                    if resume_text:
                        st.success(f"✅ Extracted {len(resume_text.split())} words from `{uploaded_file.name}`")
                        with st.expander("👁️ View Extracted Resume Text"):
                            st.text_area("Resume Content", resume_text, height=200, disabled=True)
                    else:
                        st.warning("Could not extract readable text from the uploaded file.")
                except Exception as e:
                    st.error(f"Error reading file: {str(e)}")
        else:
            resume_text = st.text_area("Paste your resume text here:", height=250, placeholder="Paste resume text...")

    job_description = ""
    target_job_title = "Selected Job"
    
    with col2:
        st.markdown("### 2. Target Job Description")
        jd_source = st.radio("Job Target Source", ["Select Existing Tracked Job", "Custom Job Description"], horizontal=True)

        if jd_source == "Select Existing Tracked Job" and not job_data.empty:
            job_options = {f"{row['job_title']} @ {row['company']}": idx for idx, row in job_data.iterrows()}
            selected_label = st.selectbox("Select Tracked Job", list(job_options.keys()))
            selected_idx = job_options[selected_label]
            selected_job = job_data.loc[selected_idx]
            
            target_job_title = f"{selected_job['job_title']} at {selected_job['company']}"
            desc = selected_job.get('description', '')
            analysis = selected_job.get('match_analysis', '')
            
            job_description = f"{desc}\n{analysis}"
            if not job_description.strip():
                st.warning("No description available for this tracked job. You can paste custom description text below.")
                job_description = st.text_area("Enter Job Description", height=200)
            else:
                with st.expander("👁️ View Target Job Description"):
                    st.markdown(f"**Title:** {selected_job['job_title']}")
                    st.markdown(f"**Company:** {selected_job['company']}")
                    st.text_area("Target Description", job_description, height=150, disabled=True)
        else:
            job_description = st.text_area("Paste target job description here:", height=250, placeholder="Paste job description text...")

    st.markdown("---")
    
    if st.button("⚡ Calculate ATS Match Score", type="primary", use_container_width=True):
        if not resume_text.strip():
            st.error("Please upload or paste a resume first.")
            return
        if not job_description.strip():
            st.error("Please select or paste a target job description.")
            return
            
        with st.spinner("Analyzing resume against job qualifications..."):
            result = calculate_resume_match_score(resume_text, job_description)

        st.markdown("## 📊 Analysis Results")
        
        m_col1, m_col2, m_col3 = st.columns(3)
        score = result["score"]
        
        with m_col1:
            if score >= 80:
                st.metric("ATS Match Score", f"{score}%", delta="High Match", delta_color="normal")
            elif score >= 50:
                st.metric("ATS Match Score", f"{score}%", delta="Medium Match", delta_color="off")
            else:
                st.metric("ATS Match Score", f"{score}%", delta="Low Match", delta_color="inverse")

        with m_col2:
            st.metric("Matched Skills Found", len(result["matched_skills"]))

        with m_col3:
            st.metric("Missing Skills Identified", len(result["missing_skills"]))

        st.progress(int(score) / 100.0)

        # Tailoring Advice
        if result["recommendations"]:
            st.markdown("### 💡 Actionable Coaching & Recommendations")
            for rec in result["recommendations"]:
                st.info(rec)

        res_col1, res_col2 = st.columns(2)
        
        with res_col1:
            st.markdown("#### ✅ Matched Skills & Keywords")
            if result["matched_skills"]:
                badges = " ".join([f"`{s}`" for s in result["matched_skills"]])
                st.markdown(badges)
            else:
                st.caption("No matching key technical terms found.")

        with res_col2:
            st.markdown("#### ⚠️ Missing Skills to Add")
            if result["missing_skills"]:
                badges = " ".join([f"`{s}`" for s in result["missing_skills"]])
                st.markdown(badges)
            else:
                st.success("🎉 No key skills missing!")
