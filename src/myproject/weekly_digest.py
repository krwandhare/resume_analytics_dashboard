"""Weekly job-search analytics digest generation and optional email delivery."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
import smtplib
from typing import Iterable

import pandas as pd

from myproject.statuses import INTERVIEW_STATUSES, OFFER_STATUSES, PRE_APPLICATION_STATUSES


@dataclass(frozen=True)
class WeeklyDigest:
    week_start: datetime
    week_end: datetime
    applications: int
    previous_applications: int
    status_changes: int
    interviews: int
    offers: int
    interview_rate: float
    offer_rate: float
    top_companies: tuple[tuple[str, int], ...]

    @property
    def application_delta(self) -> int:
        return self.applications - self.previous_applications


def _utc_timestamp(value: datetime | str | pd.Timestamp | None = None) -> pd.Timestamp:
    timestamp = pd.Timestamp(value or datetime.now(timezone.utc))
    if timestamp.tzinfo is None:
        return timestamp.tz_localize("UTC")
    return timestamp.tz_convert("UTC")


def _week_bounds(reference: datetime | str | pd.Timestamp | None) -> tuple[pd.Timestamp, pd.Timestamp]:
    current = _utc_timestamp(reference).normalize()
    start = current - pd.Timedelta(days=current.weekday())
    return start, start + pd.Timedelta(days=7)


def _dated_rows(
    frame: pd.DataFrame | None,
    date_columns: Iterable[str],
    start: pd.Timestamp,
    end: pd.Timestamp,
) -> pd.DataFrame:
    if frame is None or frame.empty:
        return pd.DataFrame()
    date_column = next((column for column in date_columns if column in frame.columns), None)
    if date_column is None:
        return pd.DataFrame(columns=frame.columns)
    dated = frame.copy()
    dated["_digest_date"] = pd.to_datetime(dated[date_column], errors="coerce", utc=True)
    return dated[dated["_digest_date"].ge(start) & dated["_digest_date"].lt(end)].copy()


def _application_rows(
    jobs_df: pd.DataFrame | None,
    apps_df: pd.DataFrame | None,
    start: pd.Timestamp,
    end: pd.Timestamp,
) -> pd.DataFrame:
    source_jobs = jobs_df
    if (
        source_jobs is not None
        and not source_jobs.empty
        and apps_df is not None
        and not apps_df.empty
        and "_source_table" in source_jobs.columns
    ):
        source_jobs = source_jobs[
            source_jobs["_source_table"].astype(str).ne("job_applications")
        ]
    jobs = _dated_rows(source_jobs, ("first_seen_at", "posted_at", "created_at"), start, end)
    apps = _dated_rows(apps_df, ("applied_at", "created_at", "updated_at"), start, end)
    frames = []
    for frame in (jobs, apps):
        if frame.empty:
            continue
        filtered = frame
        if "status" in filtered.columns:
            filtered = filtered[~filtered["status"].astype(str).str.lower().isin(PRE_APPLICATION_STATUSES)]
        frames.append(filtered)
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True, sort=False)


def build_weekly_digest(
    jobs_df: pd.DataFrame | None,
    apps_df: pd.DataFrame | None = None,
    events_df: pd.DataFrame | None = None,
    reference: datetime | str | pd.Timestamp | None = None,
) -> WeeklyDigest:
    """Summarize the current Monday-to-Monday UTC window and compare it to the prior week."""
    week_start, week_end = _week_bounds(reference)
    previous_start = week_start - pd.Timedelta(days=7)

    current_apps = _application_rows(jobs_df, apps_df, week_start, week_end)
    previous_apps = _application_rows(jobs_df, apps_df, previous_start, week_start)
    current_events = _dated_rows(
        events_df,
        ("event_date", "created_at", "updated_at", "date", "timestamp"),
        week_start,
        week_end,
    )

    event_statuses = (
        current_events["event_type"].astype(str).str.lower()
        if "event_type" in current_events.columns
        else pd.Series(dtype="object")
    )
    application_ids = (
        current_events["application_id"]
        if "application_id" in current_events.columns
        else pd.Series(current_events.index, index=current_events.index)
    )
    interviews = int(application_ids[event_statuses.isin(INTERVIEW_STATUSES)].nunique())
    offers = int(application_ids[event_statuses.isin(OFFER_STATUSES)].nunique())
    application_count = len(current_apps)

    company_column = next(
        (column for column in ("company", "company_name") if column in current_apps.columns),
        None,
    )
    top_companies: tuple[tuple[str, int], ...] = ()
    if company_column:
        counts = (
            current_apps[company_column]
            .dropna()
            .astype(str)
            .str.strip()
            .replace("", pd.NA)
            .dropna()
            .value_counts()
            .head(5)
        )
        top_companies = tuple((str(company), int(count)) for company, count in counts.items())

    return WeeklyDigest(
        week_start=week_start.to_pydatetime(),
        week_end=week_end.to_pydatetime(),
        applications=application_count,
        previous_applications=len(previous_apps),
        status_changes=len(current_events),
        interviews=interviews,
        offers=offers,
        interview_rate=(interviews / application_count * 100) if application_count else 0.0,
        offer_rate=(offers / interviews * 100) if interviews else 0.0,
        top_companies=top_companies,
    )


def render_digest_markdown(digest: WeeklyDigest) -> str:
    """Render a portable Markdown digest for download, email, or archival."""
    direction = "+" if digest.application_delta > 0 else ""
    companies = "\n".join(
        f"- {company}: {count}" for company, count in digest.top_companies
    ) or "- No applications recorded"
    return f"""# Weekly job-search digest

**Period:** {digest.week_start:%b %d, %Y}–{(digest.week_end - timedelta(days=1)):%b %d, %Y} (UTC)

## Pipeline activity

- Applications: **{digest.applications}** ({direction}{digest.application_delta} vs previous week)
- Status changes: **{digest.status_changes}**
- Interviews reached: **{digest.interviews}**
- Offers reached: **{digest.offers}**
- Application → interview: **{digest.interview_rate:.1f}%**
- Interview → offer: **{digest.offer_rate:.1f}%**

## Top companies

{companies}
"""


def send_digest_email(
    digest: WeeklyDigest,
    *,
    smtp_host: str,
    smtp_port: int,
    smtp_username: str,
    smtp_password: str,
    sender: str,
    recipient: str,
    use_starttls: bool = True,
) -> None:
    """Deliver a digest through an explicitly configured SMTP account."""
    message = EmailMessage()
    message["Subject"] = f"Weekly job-search digest — {digest.week_start:%b %d, %Y}"
    message["From"] = sender
    message["To"] = recipient
    message.set_content(render_digest_markdown(digest))

    with smtplib.SMTP(smtp_host, int(smtp_port), timeout=30) as smtp:
        if use_starttls:
            smtp.starttls()
        if smtp_username:
            smtp.login(smtp_username, smtp_password)
        smtp.send_message(message)
