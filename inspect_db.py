#!/usr/bin/env python3
"""Multi-table Supabase schema + data snapshot for the resume analytics dashboard.

Discovers the four tables written by the n8n ATS Job Intelligence pipeline:
  jobs, job_sources, job_review_queue, application_packages

Usage:
  python inspect_db.py
  python inspect_db.py --json schema_snapshot.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from datetime import datetime, timezone
from typing import Any

from dotenv import load_dotenv
from supabase import Client, create_client

# Tables owned by n8n_workflow migrations 001–003
DEFAULT_TABLES = (
    "jobs",
    "job_sources",
    "job_review_queue",
    "application_packages",
)

# Documented columns from migrations (used when tables are empty)
MIGRATION_COLUMNS: dict[str, list[dict[str, str]]] = {
    "jobs": [
        {"name": "id", "type": "bigint"},
        {"name": "job_url", "type": "text"},
        {"name": "job_title", "type": "text"},
        {"name": "company", "type": "text"},
        {"name": "processed_at", "type": "timestamptz"},
        {"name": "source", "type": "text"},
        {"name": "source_job_id", "type": "text"},
        {"name": "canonical_url", "type": "text"},
        {"name": "job_fingerprint", "type": "text"},
        {"name": "location", "type": "text"},
        {"name": "workplace_type", "type": "text"},
        {"name": "posted_at", "type": "timestamptz"},
        {"name": "description", "type": "text"},
        {"name": "match_score", "type": "integer"},
        {"name": "match_analysis", "type": "jsonb"},
        {"name": "gmail_message_id", "type": "text"},
        {"name": "status", "type": "text"},
        {"name": "first_seen_at", "type": "timestamptz"},
        {"name": "last_seen_at", "type": "timestamptz"},
    ],
    "job_sources": [
        {"name": "id", "type": "bigint"},
        {"name": "job_id", "type": "bigint"},
        {"name": "source", "type": "text"},
        {"name": "source_job_id", "type": "text"},
        {"name": "source_url", "type": "text"},
        {"name": "gmail_message_id", "type": "text"},
        {"name": "gmail_thread_id", "type": "text"},
        {"name": "seen_at", "type": "timestamptz"},
    ],
    "job_review_queue": [
        {"name": "id", "type": "bigint"},
        {"name": "source", "type": "text"},
        {"name": "source_url", "type": "text"},
        {"name": "gmail_message_id", "type": "text"},
        {"name": "gmail_thread_id", "type": "text"},
        {"name": "title", "type": "text"},
        {"name": "company", "type": "text"},
        {"name": "reason", "type": "text"},
        {"name": "resolved_at", "type": "timestamptz"},
        {"name": "discovered_at", "type": "timestamptz"},
    ],
    "application_packages": [
        {"name": "id", "type": "bigint"},
        {"name": "job_id", "type": "bigint"},
        {"name": "resume_path", "type": "text"},
        {"name": "cover_letter_path", "type": "text"},
        {"name": "metadata_path", "type": "text"},
        {"name": "status", "type": "text"},
        {"name": "generated_at", "type": "timestamptz"},
        {"name": "updated_at", "type": "timestamptz"},
    ],
}

# Dimensions requested for the dashboard that are NOT in migrations 001–003
MISSING_DIMENSIONS = (
    "is_consultancy / consultancy flags",
    "company_tier",
    "h1b_sponsorship metadata",
)


def get_client() -> Client:
    load_dotenv()
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get(
        "SUPABASE_ANON_KEY"
    )
    if not url or not key:
        print(
            "Error: SUPABASE_URL and (SUPABASE_SERVICE_ROLE_KEY or SUPABASE_ANON_KEY) "
            "must be set in the environment or .env file.",
            file=sys.stderr,
        )
        sys.exit(1)
    return create_client(url, key)


def python_type_name(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "bool"
    if isinstance(value, int):
        return "int"
    if isinstance(value, float):
        return "float"
    if isinstance(value, dict):
        return "dict/json"
    if isinstance(value, list):
        return "list/json"
    return type(value).__name__


def fetch_sample(client: Client, table: str, limit: int = 5) -> list[dict[str, Any]]:
    response = client.table(table).select("*").limit(limit).execute()
    return list(response.data or [])


def estimate_count(client: Client, table: str) -> int | None:
    """Best-effort row count via PostgREST. Returns None if unavailable."""
    try:
        response = client.table(table).select("*", count="exact").limit(0).execute()
        if response.count is not None:
            return int(response.count)
    except Exception:
        pass
    try:
        # Fallback: pull a larger page and report sample size only
        response = client.table(table).select("id").limit(1000).execute()
        n = len(response.data or [])
        return n if n < 1000 else None  # unknown if capped
    except Exception:
        return None


def inspect_table(client: Client, table: str) -> dict[str, Any]:
    result: dict[str, Any] = {
        "table": table,
        "ok": False,
        "row_count": None,
        "columns_from_sample": [],
        "columns_from_migration": MIGRATION_COLUMNS.get(table, []),
        "status_values": {},
        "match_analysis_keys": [],
        "sample_row_keys": [],
        "error": None,
    }
    try:
        result["row_count"] = estimate_count(client, table)
        samples = fetch_sample(client, table, limit=5)
        result["ok"] = True

        if not samples:
            result["note"] = "Table is empty or returned no rows; using migration columns."
            return result

        # Union of keys across samples
        key_types: dict[str, set[str]] = {}
        status_counter: Counter[str] = Counter()
        analysis_keys: set[str] = set()

        for row in samples:
            for col, val in row.items():
                key_types.setdefault(col, set()).add(python_type_name(val))
            if "status" in row and row["status"] is not None:
                status_counter[str(row["status"])] += 1
            analysis = row.get("match_analysis")
            if isinstance(analysis, dict):
                analysis_keys.update(analysis.keys())
            elif isinstance(analysis, str):
                try:
                    parsed = json.loads(analysis)
                    if isinstance(parsed, dict):
                        analysis_keys.update(parsed.keys())
                except json.JSONDecodeError:
                    pass

        result["columns_from_sample"] = [
            {"name": name, "sample_types": sorted(types)}
            for name, types in sorted(key_types.items())
        ]
        result["sample_row_keys"] = sorted(key_types.keys())
        result["status_values"] = dict(status_counter)

        # Broader status distribution if column exists
        if "status" in key_types:
            try:
                status_rows = (
                    client.table(table).select("status").limit(1000).execute().data or []
                )
                result["status_values"] = dict(
                    Counter(
                        str(r["status"])
                        for r in status_rows
                        if r.get("status") is not None
                    )
                )
            except Exception:
                pass

        if analysis_keys:
            result["match_analysis_keys"] = sorted(analysis_keys)

        # Redacted sample: first row keys + non-sensitive scalars only
        first = samples[0]
        redacted = {}
        for k, v in first.items():
            if k in {"description", "resume_path", "cover_letter_path", "metadata_path"}:
                redacted[k] = f"<{type(v).__name__} len={len(v) if isinstance(v, str) else 'n/a'}>"
            elif isinstance(v, dict):
                redacted[k] = {ik: type(iv).__name__ for ik, iv in v.items()}
            elif isinstance(v, str) and len(v) > 120:
                redacted[k] = v[:80] + "…"
            else:
                redacted[k] = v
        result["sample_row_redacted"] = redacted

    except Exception as exc:
        result["error"] = str(exc)
        result["ok"] = False

    return result


def print_report(snapshot: dict[str, Any]) -> None:
    print("=" * 72)
    print("Resume Analytics — Supabase inspection")
    print(f"Inspected at: {snapshot['inspected_at']}")
    print(f"Key mode:     {snapshot['key_mode']}")
    print("=" * 72)

    for table_result in snapshot["tables"]:
        name = table_result["table"]
        print(f"\n### {name}")
        if not table_result["ok"]:
            print(f"  ERROR: {table_result.get('error')}")
            continue

        count = table_result.get("row_count")
        count_s = str(count) if count is not None else "unknown (or ≥1000)"
        print(f"  Row count: {count_s}")

        if table_result.get("note"):
            print(f"  Note: {table_result['note']}")

        cols = table_result.get("columns_from_sample") or []
        if cols:
            print("  Columns (from sample):")
            for col in cols:
                types = ", ".join(col["sample_types"])
                print(f"    - {col['name']}: {types}")
        else:
            print("  Columns (from migration contract):")
            for col in table_result.get("columns_from_migration") or []:
                print(f"    - {col['name']}: {col['type']}")

        if table_result.get("status_values"):
            print(f"  status values (sample/page): {table_result['status_values']}")
        if table_result.get("match_analysis_keys"):
            print(
                f"  match_analysis keys: {', '.join(table_result['match_analysis_keys'])}"
            )

    print("\n" + "=" * 72)
    print("Schema gaps vs original dashboard brief")
    print("=" * 72)
    print("Available today:")
    print("  - processing stage ≈ jobs.status / application_packages.status")
    print("  - company name     = jobs.company")
    print("  - match scores     = jobs.match_score + jobs.match_analysis")
    print("  - sources          = jobs.source / job_sources")
    print("  - packages         = application_packages")
    print("Not in migrations 001–003 (defer to v0.2 / n8n scorer enrichment):")
    for dim in MISSING_DIMENSIONS:
        print(f"  - {dim}")
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--json",
        metavar="PATH",
        help="Write full snapshot JSON to PATH (e.g. schema_snapshot.json)",
    )
    parser.add_argument(
        "--tables",
        nargs="+",
        default=list(DEFAULT_TABLES),
        help="Tables to inspect (default: all four pipeline tables)",
    )
    args = parser.parse_args()

    load_dotenv()
    key_mode = (
        "service_role"
        if os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        else "anon"
        if os.environ.get("SUPABASE_ANON_KEY")
        else "none"
    )

    client = get_client()
    tables = [inspect_table(client, t) for t in args.tables]
    snapshot = {
        "inspected_at": datetime.now(timezone.utc).isoformat(),
        "key_mode": key_mode,
        "tables": tables,
        "missing_dimensions": list(MISSING_DIMENSIONS),
        "migration_source": "n8n_workflow/supabase/migrations/001-003",
    }

    print_report(snapshot)

    if args.json:
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(snapshot, f, indent=2, default=str)
        print(f"Wrote snapshot → {args.json}")

    # Non-zero exit if every table failed
    if tables and all(not t["ok"] for t in tables):
        sys.exit(2)


if __name__ == "__main__":
    main()
