import logging

from myproject.components.add_job_form import insert_new_job
from myproject.data_loader import DEFAULT_MOCK_DATA


SYNTHETIC_SECRET = "synthetic-service-role-secret-123456"
PRIVATE_COMPANY = "Private Payload Company"


class FailingInsertQuery:
    def insert(self, _payload):
        return self

    def execute(self):
        raise RuntimeError(f"apikey={SYNTHETIC_SECRET}")


class FailingClient:
    def table(self, _table_name):
        return FailingInsertQuery()

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


def test_insert_new_job_failure_does_not_expose_secret_or_payload(
    monkeypatch,
    caplog,
):
    monkeypatch.setattr(
        "myproject.components.add_job_form.is_valid_supabase_config",
        lambda: (True, "Valid configuration."),
    )
    monkeypatch.setattr(
        "myproject.components.add_job_form.get_supabase_client",
        lambda: FailingClient(),
    )
    payload = {
        "job_title": "Private Role",
        "company": PRIVATE_COMPANY,
        "description": "Private job description",
        "match_analysis": "Private coaching notes",
    }

    with caplog.at_level(logging.ERROR):
        success, message = insert_new_job(payload)

    assert success is False
    assert message == "Unable to save the job to the database right now."
    assert SYNTHETIC_SECRET not in message
    assert PRIVATE_COMPANY not in message
    assert SYNTHETIC_SECRET not in caplog.text
    assert PRIVATE_COMPANY not in caplog.text
    assert "field_count=4" in caplog.text
    assert "error_type=RuntimeError" in caplog.text
