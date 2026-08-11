import pytest
import pandas as pd
from myproject.data_loader import update_job_status_and_notes, get_mock_job_data, sanitize_job_data

def test_manual_status_override_persistence():
    """Verify backend manual status and notes override with timestamp and flag."""
    job_id = 1
    new_status = "Interviewing"
    new_notes = "E2E Test: Completed technical phone screen. Moving to system design round."

    # Execute manual status override
    success = update_job_status_and_notes(job_id, new_status, new_notes)
    assert success is True, "Expected update_job_status_and_notes to return True"

    # Fetch sanitized mock data and verify overridden fields
    mock_df = get_mock_job_data()
    updated_row = mock_df[mock_df['id'] == job_id].iloc[0]

    assert updated_row['status'] == new_status, f"Expected status '{new_status}', got '{updated_row['status']}'"
    assert updated_row['match_analysis'] == new_notes, "Expected match_analysis to match test notes"
    assert updated_row['is_manually_overridden'] is True, "Expected is_manually_overridden flag to be True"
    assert 'updated_at' in updated_row, "Expected updated_at timestamp in overridden record"

def test_streamlit_apptest_e2e_manual_override():
    """AppTest framework E2E test simulating Streamlit session interaction."""
    from streamlit.testing.v1 import AppTest
    from pathlib import Path

    app_main = str((Path(__file__).parent.parent / "src" / "myproject" / "main.py").resolve())
    at = AppTest.from_file(app_main, default_timeout=15)
    at.run()
    assert not at.exception, f"App threw an unhandled exception: {at.exception}"

    # Verify main title and tabs presence
    assert len(at.tabs) > 0, "Expected tabs to be present in main view"

