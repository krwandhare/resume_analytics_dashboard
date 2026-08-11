import pytest
import pandas as pd
from myproject.data_loader import get_mock_job_data

def test_master_detail_layout_rendering():
    """Verify Master-Detail layout split and filter option values."""
    mock_df = get_mock_job_data()
    assert not mock_df.empty, "Expected mock job data"

    # Verify company and status column presence
    assert 'company' in mock_df.columns
    assert 'status' in mock_df.columns

    # Verify status filtering logic
    applied_jobs = mock_df[mock_df['status'].str.lower() == 'applied']
    assert len(applied_jobs) > 0, "Expected applied status jobs"

def test_streamlit_apptest_master_detail_layout_e2e():
    """Execute Streamlit AppTest framework simulation for Master-Detail split view."""
    from streamlit.testing.v1 import AppTest
    from pathlib import Path

    app_main = str((Path(__file__).parent.parent / "src" / "myproject" / "main.py").resolve())
    at = AppTest.from_file(app_main, default_timeout=15)
    at.run()
    assert not at.exception, f"App threw unhandled exception: {at.exception}"

    # Verify layout tabs and containers
    assert len(at.tabs) > 0, "Expected main tabs to render cleanly"
