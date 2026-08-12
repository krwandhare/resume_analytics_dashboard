import pytest
from myproject.components.add_job_form import insert_new_job
from myproject.data_loader import DEFAULT_MOCK_DATA

def test_insert_new_job_fallback(monkeypatch):
    monkeypatch.setattr(
        "myproject.components.add_job_form.is_valid_supabase_config",
        lambda: (False, "Test demo mode"),
    )
    initial_count = len(DEFAULT_MOCK_DATA)
    payload = {
        "job_title": "Test Engineer",
        "company": "Pytest Inc",
        "location": "Remote",
        "status": "Applied",
        "match_score": 88.0,
        "job_url": "https://example.com/job",
        "posted_at": "2026-08-10",
        "description": "Test job description",
        "match_analysis": "Test coaching notes"
    }

    try:
        success, msg = insert_new_job(payload)
        assert success is True
        assert "Pytest Inc" in msg
        assert len(DEFAULT_MOCK_DATA) == initial_count + 1
        assert DEFAULT_MOCK_DATA[0]["job_title"] == "Test Engineer"
        assert DEFAULT_MOCK_DATA[0]["company"] == "Pytest Inc"
    finally:
        del DEFAULT_MOCK_DATA[: len(DEFAULT_MOCK_DATA) - initial_count]
