import streamlit as st
from myproject.analytics import generate_analytics
from supabase import create_client, Client
import os
import time
import pandas as pd

# Initialize Supabase client
@st.cache_resource
def init_supabase():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    return create_client(url, key)

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
        **Resume analytics** powered by Supabase data.
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
    
    # Initialize Supabase
    supabase = init_supabase()
    
    with st.spinner("Fetching resume data..."):
        try:
            start_time = time.time()
            
            # Fetch data from Supabase
            response = supabase.table('resumes').select("*").execute()
            resume_data = pd.DataFrame(response.data)
            
            processing_time = time.time() - start_time
            st.success(f"Fetched {len(resume_data)} resumes in {processing_time:.2f} seconds!")
            
            # Create tabs for different views
            tab1, tab2, tab3 = st.tabs(["📊 Overview", "📝 Details", "📈 Insights"])
            
            with tab1:
                st.subheader("Resume Overview")
                col1, col2 = st.columns(2)
                with col1:
                    total_experience = resume_data['total_experience'].sum()
                    st.metric("Total Experience", f"{total_experience} years")
                    st.metric("Total Resumes", len(resume_data))
                with col2:
                    avg_skills = resume_data['skills'].apply(len).mean()
                    st.metric("Avg Skills Count", f"{avg_skills:.1f}")
                    st.metric("Total Certifications", resume_data['certifications'].sum())
                    
            with tab2:
                st.subheader("Detailed Analysis")
                generate_analytics(resume_data)
                
            with tab3:
                st.subheader("Career Insights")
                st.write("Coming soon...")
                
        except Exception as e:
            st.error(f"Error fetching resume data: {str(e)}")
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
