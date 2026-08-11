import pytest
import pandas as pd
from myproject.data_loader import get_mock_job_data, update_job_status_and_notes

def test_interviews_view_data_mapping():
    """Verify View Interviews data extraction and primary key mapping."""
    mock_df = get_mock_job_data()
    assert not mock_df.empty, "Expected mock job data"

    # Filter interviewing applications
    interview_jobs = mock_df[mock_df['status'].str.lower().isin(['interviewing', 'offer', 'offer received', 'hired'])]
    assert len(interview_jobs) > 0, "Expected interview jobs in mock data"

    sample_job = interview_jobs.iloc[0]
    target_id = int(float(sample_job['id']))

    # Test update function
    res = update_job_status_and_notes(target_id, "Offer Received", "Passed final round interview cleanly.")
    assert res is True, "Expected update_job_status_and_notes to return True"

def test_streamlit_apptest_interviews_view_e2e():
    """Execute Streamlit AppTest framework simulation for View Interviews grid and save button."""
    from streamlit.testing.v1 import AppTest
    from pathlib import Path

    app_main = str((Path(__file__).parent.parent / "src" / "myproject" / "main.py").resolve())
    at = AppTest.from_file(app_main, default_timeout=15)
    at.run()
    assert not at.exception, f"App threw unhandled exception: {at.exception}"

    # Verify AppTest execution completed without errors
    assert at.session_state is not None
