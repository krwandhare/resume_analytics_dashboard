import streamlit as st
import pandas as pd
from myproject.components.resume_scorer import render_resume_scorer

def render_ats_scorer_view(filtered_data: pd.DataFrame) -> None:
    """Render the ATS Scorer tab view."""
    st.markdown("## 🎯 ATS Resume Match Engine")
    st.caption("Upload your resume and benchmark your skill alignment against target job descriptions.")

    render_resume_scorer(filtered_data)
