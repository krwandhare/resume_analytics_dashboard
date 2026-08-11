import pytest
import pandas as pd
from datetime import datetime, timedelta, timezone

from myproject.pending_diagnostics import (
    categorize_pending_record,
    build_pending_diagnostics_df
)
from myproject.data_loader import get_mock_job_data

def test_categorize_pending_record():
    """Verify diagnostic categorization rules by application date age."""
    now = datetime.now(timezone.utc)

    # 1. Stale > 14 Days
    stale_date = (now - timedelta(days=18)).isoformat()
    diag_stale = categorize_pending_record(stale_date)
    assert diag_stale['category'] == "🔴 Stale (> 14 Days)"
    assert "No recruiter response" in diag_stale['reason']
    assert diag_stale['action'] == "📧 Send Follow-up Email"

    # 2. Follow-up Needed (7-14 Days)
    followup_date = (now - timedelta(days=10)).isoformat()
    diag_followup = categorize_pending_record(followup_date)
    assert diag_followup['category'] == "🟡 Follow-up Needed (7-14 Days)"
    assert "Pending initial screen" in diag_followup['reason']
    assert diag_followup['action'] == "📧 Send Follow-up Email"

    # 3. Recently Applied (< 7 Days)
    recent_date = (now - timedelta(days=2)).isoformat()
    diag_recent = categorize_pending_record(recent_date)
    assert diag_recent['category'] == "🟢 Recently Applied (< 7 Days)"
    assert "within review window" in diag_recent['reason']
    assert diag_recent['action'] == "⏳ Awaiting Review"

def test_build_pending_diagnostics_df():
    """Verify building sanitized pending diagnostics dataframe with actions and links."""
    mock_df = get_mock_job_data()
    diag_df = build_pending_diagnostics_df(mock_df)

    assert not diag_df.empty, "Expected non-empty pending diagnostics dataframe"
    expected_cols = [
        'Sr No', 'Company', 'Role', 'Status', 'Applied Date', 'Days Pending',
        'Diagnostic Category', 'Diagnostic Reason', 'Recommended Action', 'Job Link', 'Gmail'
    ]
    for col in expected_cols:
        assert col in diag_df.columns, f"Expected column '{col}' in diagnostics dataframe"

    # Verify that action suggestions are present
    actions = diag_df['Recommended Action'].tolist()
    assert any("Follow-up" in act or "Awaiting" in act for act in actions)

def test_streamlit_apptest_pending_diagnostics_e2e():
    """Execute Streamlit AppTest framework simulation for pending diagnostics rendering."""
    from streamlit.testing.v1 import AppTest
    from pathlib import Path

    app_main = str((Path(__file__).parent.parent / "src" / "myproject" / "main.py").resolve())
    at = AppTest.from_file(app_main, default_timeout=15)
    at.run()
    assert not at.exception, f"App threw unhandled exception: {at.exception}"

    # Select Overview sub-tab if present
    assert len(at.tabs) > 0, "Expected tabs in main view"
