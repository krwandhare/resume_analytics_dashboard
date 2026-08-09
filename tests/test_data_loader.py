import pytest
import pandas as pd
import os
from myproject.data_loader import (
    is_valid_supabase_config,
    sanitize_job_data,
    get_mock_job_data,
    load_job_data,
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
