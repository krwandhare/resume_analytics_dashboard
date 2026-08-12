"""Canonical job status vocabulary and pipeline groupings."""

STATUS_OPTIONS = (
    "Saved For Later",
    "Not Applied",
    "Applied",
    "Reviewing",
    "Recruiter Call",
    "Interviewing",
    "Offer Received",
    "Hired",
    "Rejected",
    "Cancelled",
    "Not H1B Friendly",
    "Ghosted",
    "Irejected",
    "Withdrew",
    "Consultancy",
)

STATUS_COLORS = {
    "Saved For Later": "#D8B4E2",
    "Not Applied": "#F97316",
    "Applied": "#3B82F6",
    "Reviewing": "#60A5FA",
    "Recruiter Call": "#93C5FD",
    "Interviewing": "#F59E0B",
    "Offer Received": "#34D399",
    "Offer": "#34D399",
    "Pending": "#93C5FD",
    "Hired": "#10B981",
    "Rejected": "#EF4444",
    "Cancelled": "#DC2626",
    "Not H1B Friendly": "#B91C1C",
    "Ghosted": "#9CA3AF",
    "Irejected": "#F97316",
    "Withdrew": "#F87171",
    "Consultancy": "#FBBF24",
    "Unknown": "#6B7280",
}

PRE_APPLICATION_STATUSES = frozenset({"saved for later", "not applied"})
ACTIVE_STATUSES = frozenset({"applied", "pending", "reviewing", "recruiter call"})
INTERVIEW_STATUSES = frozenset(
    {"recruiter call", "interviewing", "offer", "offer received", "hired"}
)
OFFER_STATUSES = frozenset({"offer", "offer received", "hired"})

_CANONICAL_BY_KEY = {status.casefold(): status for status in STATUS_OPTIONS}
_CANONICAL_BY_KEY.update({"offer": "Offer Received", "pending": "Pending"})


def canonicalize_status(value: object) -> str:
    """Return a stable display label without corrupting acronyms such as H1B."""
    raw = str(value or "Unknown").strip()
    return _CANONICAL_BY_KEY.get(raw.casefold(), raw.title())
