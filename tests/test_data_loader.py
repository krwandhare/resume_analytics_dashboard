import pytest
import pandas as pd
import os
from myproject.data_loader import (
    is_valid_supabase_config,
    sanitize_job_data,
    get_mock_job_data,
    load_job_data,
    format_staleness,
    log_torc_diagnostics,
    log_staleness_diagnostics,
    REQUIRED_COLUMNS
)

def test_is_valid_supabase_config_default_placeholder(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://your-project.supabase.co")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "your-anon-public-key")
    is_valid, msg = is_valid_supabase_config()
    assert is_valid is False
    assert "default placeholders" in msg

def test_is_valid_supabase_config_missing_env(monkeypatch):
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_ANON_KEY", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)
    is_valid, msg = is_valid_supabase_config()
    assert is_valid is False
    assert "missing" in msg

def test_sanitize_job_data_empty_df():
    empty_df = pd.DataFrame()
    sanitized = sanitize_job_data(empty_df)
    assert not sanitized.empty == False or len(sanitized) == 0
    for col in ['company', 'status', 'match_score', 'job_title']:
        assert col in sanitized.columns

def test_sanitize_job_data_missing_columns():
    incomplete_df = pd.DataFrame([{"company": "Google"}])
    sanitized = sanitize_job_data(incomplete_df)
    assert sanitized.loc[0, "company"] == "Google"
    assert sanitized.loc[0, "status"] == "Pending"
    assert sanitized.loc[0, "match_score"] == 0.0
    assert sanitized.loc[0, "job_title"] == "Untitled Job"

def test_sanitize_job_data_invalid_numeric_score():
    df = pd.DataFrame([{"company": "Meta", "match_score": "not_a_number"}])
    sanitized = sanitize_job_data(df)
    assert sanitized.loc[0, "match_score"] == 0.0

def test_get_mock_job_data():
    mock_df = get_mock_job_data()
    assert isinstance(mock_df, pd.DataFrame)
    assert len(mock_df) >= 5
    for col in ['company', 'status', 'match_score', 'job_title']:
        assert col in mock_df.columns

def test_load_job_data_fallback(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://your-project.supabase.co")
    df, is_live, msg = load_job_data()
    assert is_live is False
    assert "Demo Data" in msg
    assert len(df) > 0

def test_format_staleness_fresh():
    assert "Just now" in format_staleness(10)
    assert "m ago" in format_staleness(300)

def test_format_staleness_day_boundaries():
    assert "1d old" in format_staleness(86400)
    assert "Stale" in format_staleness(86400 * 5)
    assert "Unknown" in format_staleness(None)

# Dynamic timestamps for testing full pipeline staleness ranges
_now_ts = pd.Timestamp.now()
_fresh_date = (_now_ts - pd.Timedelta(seconds=30)).strftime('%Y-%m-%dT%H:%M:%SZ')
_hours_date = (_now_ts - pd.Timedelta(hours=4)).strftime('%Y-%m-%dT%H:%M:%SZ')
_moderate_date = (_now_ts - pd.Timedelta(days=1, hours=12)).strftime('%Y-%m-%dT%H:%M:%SZ')
_stale_date = (_now_ts - pd.Timedelta(days=10)).strftime('%Y-%m-%dT%H:%M:%SZ')
_future_date = (_now_ts + pd.Timedelta(days=2)).strftime('%Y-%m-%dT%H:%M:%SZ')

@pytest.mark.parametrize("company,event_date", [
    ("Torc Technologies", _fresh_date),
    ("TechCorp Solutions", _hours_date),
    ("DataFlow Inc", _moderate_date),
    ("Innovate Analytics", _stale_date),
    ("CloudNative Systems", _future_date),
    ("Meta", None),
    ("Google", ""),
    ("Acme Corp", "invalid-timestamp-string")
])
def test_staleness_diagnostics(caplog, company, event_date):
    import logging
    events_data = pd.DataFrame([
        {
            "application_id": 999,
            "company": company,
            "role_title": "Senior Engineer",
            "event_date": event_date
        }
    ])
    with caplog.at_level(logging.INFO):
        log_staleness_diagnostics(events_data)
        
    assert "DIAGNOSTIC - Event" in caplog.text
    assert company in caplog.text
    assert "Staleness Days" in caplog.text


