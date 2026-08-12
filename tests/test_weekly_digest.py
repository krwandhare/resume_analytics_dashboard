from datetime import datetime, timezone
from email.message import EmailMessage

import pandas as pd
import pytest

from myproject.weekly_digest import build_weekly_digest, render_digest_markdown, send_digest_email


REFERENCE = datetime(2026, 8, 12, 12, tzinfo=timezone.utc)


def test_build_weekly_digest_compares_weeks_and_excludes_pre_application():
    jobs = pd.DataFrame([
        {"id": 1, "company": "Alpha", "status": "Applied", "first_seen_at": "2026-08-10T10:00:00Z"},
        {"id": 2, "company": "Alpha", "status": "Applied", "first_seen_at": "2026-08-11T10:00:00Z"},
        {"id": 3, "company": "Beta", "status": "Saved For Later", "first_seen_at": "2026-08-11T11:00:00Z"},
        {"id": 4, "company": "Gamma", "status": "Applied", "first_seen_at": "2026-08-04T10:00:00Z"},
    ])
    events = pd.DataFrame([
        {"application_id": 1, "event_type": "Recruiter Call", "event_date": "2026-08-11T12:00:00Z"},
        {"application_id": 1, "event_type": "Interviewing", "event_date": "2026-08-12T12:00:00Z"},
        {"application_id": 2, "event_type": "Offer Received", "event_date": "2026-08-13T12:00:00Z"},
    ])

    digest = build_weekly_digest(jobs, events_df=events, reference=REFERENCE)

    assert digest.applications == 2
    assert digest.previous_applications == 1
    assert digest.application_delta == 1
    assert digest.status_changes == 3
    assert digest.interviews == 2
    assert digest.offers == 1
    assert digest.interview_rate == 100.0
    assert digest.offer_rate == 50.0
    assert digest.top_companies == (("Alpha", 2),)


def test_digest_handles_missing_dates_and_empty_frames():
    digest = build_weekly_digest(pd.DataFrame([{"company": "Alpha", "status": "Applied"}]), reference=REFERENCE)

    assert digest.applications == 0
    assert digest.status_changes == 0
    assert digest.interview_rate == 0.0
    assert digest.top_companies == ()


def test_digest_does_not_recount_tagged_historical_rows():
    combined = pd.DataFrame([
        {
            "id": 1,
            "company": "Alpha",
            "status": "Applied",
            "first_seen_at": "2026-08-11T10:00:00Z",
            "_source_table": "jobs",
        },
        {
            "id": 20,
            "company": "Beta",
            "status": "Applied",
            "applied_at": "2026-08-12T10:00:00Z",
            "_source_table": "job_applications",
        },
    ])
    apps = pd.DataFrame([
        {
            "id": 20,
            "company": "Beta",
            "status": "Applied",
            "applied_at": "2026-08-12T10:00:00Z",
        }
    ])

    digest = build_weekly_digest(combined, apps_df=apps, reference=REFERENCE)

    assert digest.applications == 2
    assert dict(digest.top_companies) == {"Alpha": 1, "Beta": 1}


def test_render_digest_markdown_contains_portable_summary():
    jobs = pd.DataFrame([
        {"company": "Alpha", "status": "Applied", "posted_at": "2026-08-11T10:00:00Z"}
    ])
    markdown = render_digest_markdown(build_weekly_digest(jobs, reference=REFERENCE))

    assert "# Weekly job-search digest" in markdown
    assert "Applications: **1**" in markdown
    assert "Alpha: 1" in markdown


def test_send_digest_email_uses_tls_login_and_message(monkeypatch):
    sent = {}

    class FakeSMTP:
        def __init__(self, host, port, timeout):
            sent["connection"] = (host, port, timeout)

        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def starttls(self):
            sent["tls"] = True

        def login(self, username, password):
            sent["login"] = (username, password)

        def send_message(self, message: EmailMessage):
            sent["message"] = message

    monkeypatch.setattr("myproject.weekly_digest.smtplib.SMTP", FakeSMTP)
    digest = build_weekly_digest(pd.DataFrame(), reference=REFERENCE)

    send_digest_email(
        digest,
        smtp_host="smtp.example.com",
        smtp_port=587,
        smtp_username="user",
        smtp_password="secret",
        sender="from@example.com",
        recipient="to@example.com",
    )

    assert sent["connection"] == ("smtp.example.com", 587, 30)
    assert sent["tls"] is True
    assert sent["login"] == ("user", "secret")
    assert sent["message"]["To"] == "to@example.com"
    assert "Weekly job-search digest" in sent["message"].get_content()
