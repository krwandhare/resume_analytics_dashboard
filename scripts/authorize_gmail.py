#!/usr/bin/env python3
"""Authorize Gmail send-only access and save the local OAuth token."""

from __future__ import annotations

from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from myproject.weekly_digest import authorize_gmail  # noqa: E402


def main() -> int:
    client_path = PROJECT_ROOT / ".local" / "google-oauth-client.json"
    token_path = PROJECT_ROOT / ".local" / "gmail-token.json"
    authorize_gmail(client_path, token_path)
    print(f"Gmail OAuth token saved to {token_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
