import streamlit as st
from myproject.resume_parser import parse_resume
from myproject.analytics import generate_analytics
import time

def main():
    st.set_page_config(
        page_title="Resume Analytics Dashboard", 
        layout="wide",
        page_icon="📊"
    )
    
    # Sidebar
    with st.sidebar:
        st.title("📊 Resume Analytics")
        st.markdown("""
        **Upload your resume** to get detailed analytics and insights.
        Supported formats: PDF, DOCX
        """)
        
        st.markdown("---")
        st.markdown("### Filters")
        experience_level = st.selectbox(
            "Experience Level",
            ["All", "Entry", "Mid", "Senior"]
        )
        skills_filter = st.multiselect(
            "Skills to Highlight",
            ["Python", "JavaScript", "SQL", "Machine Learning", "Cloud Computing"]
        )
        
        st.markdown("---")
        st.markdown("Made with ❤️ by Resume Analytics Team")
    
    # Main content
    st.title("Resume Analytics Dashboard")
    
    uploaded_file = st.file_uploader(
        "Upload Resume (PDF or DOCX)", 
        type=["pdf", "docx"],
        help="Select your resume file to analyze"
    )
    
    if uploaded_file:
        with st.spinner("Analyzing your resume..."):
            try:
                start_time = time.time()
                resume_data = parse_resume(uploaded_file)
                processing_time = time.time() - start_time
                
                st.success(f"Resume processed successfully in {processing_time:.2f} seconds!")
                
                # Create tabs for different views
                tab1, tab2, tab3 = st.tabs(["📊 Overview", "📝 Details", "📈 Insights"])
                
                with tab1:
                    st.subheader("Resume Overview")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Total Experience", "5 years")
                        st.metric("Skills Count", "12")
                    with col2:
                        st.metric("Education Level", "Master's")
                        st.metric("Certifications", "3")
                    
                with tab2:
                    st.subheader("Detailed Analysis")
                    generate_analytics(resume_data)
                    
                with tab3:
                    st.subheader("Career Insights")
                    st.write("Coming soon...")
                    
            except Exception as e:
                st.error(f"Error processing resume: {str(e)}")
                st.exception(e)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center;">
        <p>Resume Analytics Dashboard v1.0</p>
        <p>© 2026 Resume Analytics Inc. All rights reserved.</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
