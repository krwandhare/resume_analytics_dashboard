import streamlit as st
from myproject.resume_parser import parse_resume
from myproject.analytics import generate_analytics

def main():
    st.set_page_config(page_title="Resume Analytics Dashboard", layout="wide")
    st.title("Resume Analytics Dashboard")
    
    uploaded_file = st.file_uploader("Upload Resume (PDF or DOCX)", type=["pdf", "docx"])
    
    if uploaded_file:
        resume_data = parse_resume(uploaded_file)
        generate_analytics(resume_data)

if __name__ == "__main__":
    main()
