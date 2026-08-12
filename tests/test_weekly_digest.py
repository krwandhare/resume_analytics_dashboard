from datetime import datetime, timezone
from email import message_from_bytes
import base64
import stat

import pandas as pd
import pytest

from myproject.weekly_digest import (
    GMAIL_SEND_SCOPE,
    authorize_gmail,
    build_weekly_digest,
    render_digest_markdown,
    send_digest_email,
)


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


def test_digest_normalizes_status_whitespace():
    jobs = pd.DataFrame([
        {
            "id": 1,
            "company": "Alpha",
            "status": " Saved For Later ",
            "first_seen_at": "2026-08-11T10:00:00Z",
        },
        {
            "id": 2,
            "company": "Beta",
            "status": " Applied ",
            "first_seen_at": "2026-08-11T11:00:00Z",
        },
    ])
    events = pd.DataFrame([
        {
            "application_id": 2,
            "event_type": " Interviewing ",
            "event_date": "2026-08-12T12:00:00Z",
        },
        {
            "application_id": 2,
            "event_type": " Offer Received ",
            "event_date": "2026-08-13T12:00:00Z",
        },
    ])

    digest = build_weekly_digest(jobs, events_df=events, reference=REFERENCE)

    assert digest.applications == 1
    assert digest.interviews == 1
    assert digest.offers == 1


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


def test_send_digest_email_uses_gmail_api(monkeypatch, tmp_path):
    sent = {}
    token_path = tmp_path / "gmail-token.json"
    token_path.write_text("{}", encoding="utf-8")
    credentials = type("Credentials", (), {"valid": True})()
    monkeypatch.setattr(
        "myproject.weekly_digest.Credentials.from_authorized_user_file",
        lambda path, scopes: sent.update(token=(path, scopes)) or credentials,
    )

    class Execute:
        def execute(self):
            return {"id": "message-id"}

    class Messages:
        def send(self, **kwargs):
            sent["request"] = kwargs
            return Execute()

    class Users:
        def messages(self):
            return Messages()

    class Service:
        def users(self):
            return Users()

    monkeypatch.setattr(
        "myproject.weekly_digest.build",
        lambda *args, **kwargs: sent.update(build=(args, kwargs)) or Service(),
    )
    digest = build_weekly_digest(pd.DataFrame(), reference=REFERENCE)

    result = send_digest_email(
        digest,
        token_path=token_path,
        sender="sender@example.com",
        recipient="digest@example.com",
    )

    assert result == {"id": "message-id"}
    assert sent["token"] == (str(token_path), [GMAIL_SEND_SCOPE])
    assert sent["request"]["userId"] == "me"
    message = message_from_bytes(base64.urlsafe_b64decode(sent["request"]["body"]["raw"]))
    assert message["From"] == "sender@example.com"
    assert message["To"] == "digest@example.com"
    assert "Weekly job-search digest" in message.get_payload()


def test_send_digest_email_requires_recipient(tmp_path):
    token_path = tmp_path / "gmail-token.json"
    token_path.write_text("{}", encoding="utf-8")

    with pytest.raises(RuntimeError, match="recipient email address is required"):
        send_digest_email(
            build_weekly_digest(pd.DataFrame(), reference=REFERENCE),
            token_path=token_path,
            sender="sender@example.com",
            recipient=" ",
        )


def test_send_digest_email_refreshes_and_persists_token(monkeypatch, tmp_path):
    token_path = tmp_path / "gmail-token.json"
    token_path.write_text("{}", encoding="utf-8")

    class FakeCredentials:
        valid = False
        expired = True
        refresh_token = "refresh-token"

        def refresh(self, request):
            self.valid = True

        def to_json(self):
            return '{"refreshed": true}'

    credentials = FakeCredentials()
    monkeypatch.setattr(
        "myproject.weekly_digest.Credentials.from_authorized_user_file",
        lambda *_args: credentials,
    )
    monkeypatch.setattr("myproject.weekly_digest.Request", lambda: object())

    class Service:
        def users(self):
            return self

        def messages(self):
            return self

        def send(self, **_kwargs):
            return self

        def execute(self):
            return {"id": "sent"}

    monkeypatch.setattr("myproject.weekly_digest.build", lambda *_args, **_kwargs: Service())

    send_digest_email(
        build_weekly_digest(pd.DataFrame(), reference=REFERENCE),
        token_path=token_path,
        sender="sender@example.com",
        recipient="digest@example.com",
    )

    assert token_path.read_text(encoding="utf-8") == '{"refreshed": true}'


def test_send_digest_email_reports_missing_and_revoked_tokens(monkeypatch, tmp_path):
    digest = build_weekly_digest(pd.DataFrame(), reference=REFERENCE)
    token_path = tmp_path / "gmail-token.json"
    with pytest.raises(RuntimeError, match="not found"):
        send_digest_email(
            digest,
            token_path=token_path,
            sender="sender@example.com",
            recipient="digest@example.com",
        )

    token_path.write_text("{}", encoding="utf-8")
    credentials = type(
        "Credentials", (), {"valid": False, "expired": False, "refresh_token": None}
    )()
    monkeypatch.setattr(
        "myproject.weekly_digest.Credentials.from_authorized_user_file",
        lambda *_args: credentials,
    )
    with pytest.raises(RuntimeError, match="missing or revoked"):
        send_digest_email(
            digest,
            token_path=token_path,
            sender="sender@example.com",
            recipient="digest@example.com",
        )


@pytest.mark.parametrize("error_type", ["refresh", "transport"])
def test_send_digest_email_reports_failed_token_refresh(monkeypatch, tmp_path, error_type):
    token_path = tmp_path / "gmail-token.json"
    token_path.write_text("{}", encoding="utf-8")

    class FakeCredentials:
        valid = False
        expired = True
        refresh_token = "revoked-token"

        def refresh(self, _request):
            from google.auth.exceptions import RefreshError, TransportError

            error_class = RefreshError if error_type == "refresh" else TransportError
            raise error_class("refresh failed")

    monkeypatch.setattr(
        "myproject.weekly_digest.Credentials.from_authorized_user_file",
        lambda *_args: FakeCredentials(),
    )
    monkeypatch.setattr("myproject.weekly_digest.Request", lambda: object())

    with pytest.raises(RuntimeError, match="token refresh failed"):
        send_digest_email(
            build_weekly_digest(pd.DataFrame(), reference=REFERENCE),
            token_path=token_path,
            sender="sender@example.com",
            recipient="digest@example.com",
        )


@pytest.mark.parametrize("error_type", ["api", "transport", "os"])
def test_send_digest_email_reports_api_failure(monkeypatch, tmp_path, error_type):
    token_path = tmp_path / "gmail-token.json"
    token_path.write_text("{}", encoding="utf-8")
    credentials = type("Credentials", (), {"valid": True})()
    monkeypatch.setattr(
        "myproject.weekly_digest.Credentials.from_authorized_user_file",
        lambda *_args: credentials,
    )

    class FakeHttpError(Exception):
        pass

    class FakeTransportError(Exception):
        pass

    monkeypatch.setattr("myproject.weekly_digest.HttpError", FakeHttpError)
    monkeypatch.setattr("myproject.weekly_digest.HttpLib2Error", FakeTransportError)
    error_class = {
        "api": FakeHttpError,
        "transport": FakeTransportError,
        "os": OSError,
    }[error_type]
    monkeypatch.setattr(
        "myproject.weekly_digest.build",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(error_class("denied")),
    )
    with pytest.raises(RuntimeError, match="Gmail API send failed"):
        send_digest_email(
            build_weekly_digest(pd.DataFrame(), reference=REFERENCE),
            token_path=token_path,
            sender="sender@example.com",
            recipient="digest@example.com",
        )


def test_authorize_gmail_saves_send_only_token(monkeypatch, tmp_path):
    client_path = tmp_path / "google-oauth-client.json"
    token_path = tmp_path / "tokens" / "gmail-token.json"
    client_path.write_text("{}", encoding="utf-8")
    observed = {}

    class Flow:
        def run_local_server(self, port, prompt):
            observed["port"] = port
            observed["prompt"] = prompt
            return type("Credentials", (), {"to_json": lambda self: '{"token": "local"}'})()

    monkeypatch.setattr(
        "myproject.weekly_digest.InstalledAppFlow.from_client_secrets_file",
        lambda path, scopes: observed.update(path=path, scopes=scopes) or Flow(),
    )

    assert authorize_gmail(client_path, token_path) == token_path
    assert observed == {
        "path": str(client_path),
        "scopes": [GMAIL_SEND_SCOPE],
        "port": 0,
        "prompt": "consent",
    }
    assert token_path.read_text(encoding="utf-8") == '{"token": "local"}'
    assert stat.S_IMODE(token_path.stat().st_mode) == 0o600


def test_authorize_gmail_reports_missing_client_credentials(tmp_path):
    with pytest.raises(RuntimeError, match="client credentials not found"):
        authorize_gmail(tmp_path / "missing.json", tmp_path / "token.json")
