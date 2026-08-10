import pytest
from myproject.email_ingestion import parse_job_email, process_email_webhook_payload

def test_parse_job_email_interview():
    subject = "Interview Invitation - Senior AI Engineer at TechCorp Solutions"
    body = "We would like to invite you for a 45-minute technical interview next week."
    sender = "recruiting@techcorp.com"

    res = parse_job_email(body, subject=subject, sender=sender)
    assert res["detected_status"] == "Interviewing"
    assert res["detected_company"] == "TechCorp Solutions"
    assert res["detected_role"] == "Senior Ai Engineer"
    assert res["confidence"] >= 85.0

def test_parse_job_email_rejection():
    subject = "Update on your Data Scientist application at Innovate Analytics"
    body = "Thank you for applying. We regret to inform you that we have decided to move forward with other candidates."
    sender = "careers@innovateanalytics.io"

    res = parse_job_email(body, subject=subject, sender=sender)
    assert res["detected_status"] == "Rejected"
    assert res["detected_company"] == "Innovate Analytics"
    assert res["confidence"] >= 80.0

def test_parse_job_email_offer():
    subject = "Job Offer - CloudNative Systems"
    body = "We are pleased to offer you employment as Backend Engineer."
    sender = "hr@cloudnative.io"

    res = parse_job_email(body, subject=subject, sender=sender)
    assert res["detected_status"] == "Offer"
    assert res["detected_company"] == "CloudNative Systems"
    assert res["confidence"] >= 90.0

def test_process_email_webhook_payload():
    payload = {
        "sender": "jobs@google.com",
        "subject": "Application Submitted for Software Engineer",
        "body": "Thank you for applying to Google!"
    }
    success, msg, parsed = process_email_webhook_payload(payload)
    assert success is True
    assert "Google" in parsed["detected_company"] or "Google" in msg
    assert parsed["detected_status"] == "Applied"
