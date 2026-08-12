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


def main() -> int:
    sender = os.environ.get("WEEKLY_DIGEST_SENDER", "").strip()
    if not sender:
        raise RuntimeError("WEEKLY_DIGEST_SENDER must be set in .env.")
    recipient = os.environ.get("WEEKLY_DIGEST_RECIPIENT", "").strip()
    if not recipient:
        raise RuntimeError("WEEKLY_DIGEST_RECIPIENT must be set in .env.")
    token_path = PROJECT_ROOT / ".local" / "gmail-token.json"
    if not token_path.is_file():
        raise RuntimeError(
            f"Gmail OAuth token not found at {token_path}. "
            "Run scripts/authorize_gmail.py first."
        )

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
        token_path=token_path,
        sender=sender,
        recipient=recipient,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
