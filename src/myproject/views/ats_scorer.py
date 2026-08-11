import sys
import os

_this_dir = os.path.dirname(os.path.abspath(__file__))
_myproject_dir = os.path.dirname(_this_dir)
_src_dir = os.path.dirname(_myproject_dir)

for _p in [_src_dir, _myproject_dir, _this_dir]:
    if _p and _p not in sys.path:
        sys.path.insert(0, _p)

import streamlit as st
import pandas as pd

try:
    from myproject.components.resume_scorer import render_resume_scorer
except ImportError:
    from ..components.resume_scorer import render_resume_scorer

def render_ats_scorer_view(filtered_data: pd.DataFrame) -> None:
    """Render the ATS Scorer tab view."""
    st.markdown("## 🎯 ATS Resume Match Engine")
    st.caption("Upload your resume and benchmark your skill alignment against target job descriptions.")

    render_resume_scorer(filtered_data)
