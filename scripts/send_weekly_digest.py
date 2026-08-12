#!/usr/bin/env python3
"""Generate and email the current weekly job-search digest."""

from __future__ import annotations

import os
from pathlib import Path
import sys

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))
load_dotenv(PROJECT_ROOT / ".env")

from myproject.data_loader import load_historical_data, load_job_data  # noqa: E402
from myproject.weekly_digest import build_weekly_digest, render_digest_markdown, send_digest_email  # noqa: E402


def _required_environment(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def main() -> int:
    jobs_df, is_live, message = load_job_data()
    if not is_live:
        raise RuntimeError(f"Live job data is required: {message}")
    apps_df, events_df = load_historical_data(jobs_df)
    digest = build_weekly_digest(jobs_df, apps_df, events_df)

    output_path = os.environ.get("WEEKLY_DIGEST_OUTPUT", "").strip()
    if output_path:
        Path(output_path).write_text(render_digest_markdown(digest), encoding="utf-8")

    send_digest_email(
        digest,
        smtp_host=_required_environment("SMTP_HOST"),
        smtp_port=int(os.environ.get("SMTP_PORT") or "587"),
        smtp_username=os.environ.get("SMTP_USERNAME", "").strip(),
        smtp_password=os.environ.get("SMTP_PASSWORD", ""),
        sender=_required_environment("WEEKLY_DIGEST_FROM"),
        recipient=_required_environment("WEEKLY_DIGEST_TO"),
        use_starttls=os.environ.get("SMTP_STARTTLS", "true").lower() not in {"0", "false", "no"},
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
