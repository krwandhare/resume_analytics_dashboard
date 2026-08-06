import streamlit as st
import pandas as pd
import plotly.express as px

def generate_analytics(resume_data):
    """Generate visual analytics from Supabase resume data"""
    if isinstance(resume_data, pd.DataFrame) and not resume_data.empty:
        # Experience Distribution
        st.subheader("Experience Distribution")
        fig = px.histogram(resume_data, x='total_experience', 
                          nbins=10, 
                          labels={'total_experience': 'Years of Experience'},
                          color_discrete_sequence=['#636EFA'])
        st.plotly_chart(fig, use_container_width=True)
        
        # Skills Analysis
        st.subheader("Top Skills")
        all_skills = [skill for sublist in resume_data['skills'] for skill in sublist]
        skills_count = pd.Series(all_skills).value_counts().head(10)
        fig = px.bar(skills_count, 
                    orientation='h',
                    labels={'index': 'Skill', 'value': 'Count'},
                    color_discrete_sequence=['#00CC96'])
        st.plotly_chart(fig, use_container_width=True)
        
        # Education Level Distribution
        st.subheader("Education Levels")
        education_counts = resume_data['education_level'].value_counts()
        fig = px.pie(education_counts, 
                    names=education_counts.index,
                    values=education_counts.values,
                    color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No resume data available for analysis")
