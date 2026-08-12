import pandas as pd

from myproject.statuses import (
    ACTIVE_STATUSES,
    INTERVIEW_STATUSES,
    PRE_APPLICATION_STATUSES,
    STATUS_COLORS,
    STATUS_OPTIONS,
    canonicalize_status,
)


def test_status_options_are_unique_and_have_colors():
    assert len(STATUS_OPTIONS) == len(set(STATUS_OPTIONS))
    assert set(STATUS_OPTIONS).issubset(STATUS_COLORS)


def test_canonicalize_status_preserves_special_spelling():
    assert canonicalize_status("not h1b friendly") == "Not H1B Friendly"
    assert canonicalize_status("irejected") == "Irejected"
    assert canonicalize_status("saved for later") == "Saved For Later"


def test_pipeline_groups_cover_recruiter_calls_and_exclude_pre_application():
    statuses = pd.Series(["Saved For Later", "Not Applied", "Applied", "Recruiter Call"])
    normalized = statuses.str.lower()

    assert normalized.isin(PRE_APPLICATION_STATUSES).sum() == 2
    assert normalized.isin(ACTIVE_STATUSES).sum() == 2
    assert normalized.isin(INTERVIEW_STATUSES).sum() == 1
