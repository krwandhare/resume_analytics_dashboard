"""
Centralised, credential-safe logging for the Streamlit dashboard.

Streamlit can close stdout/stderr during a page rerun or browser disconnect.
``SafeStreamHandler`` drops those broken-pipe writes instead of crashing the
rerun loop. The logging bootstrap also redacts credentials before records
reach handlers and limits verbose third-party transport logging.
"""

from collections.abc import Mapping
from functools import lru_cache
import logging
import os
import re
import sys
import traceback
from typing import Optional


_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"
_DEFAULT_LEVEL = logging.INFO
_REDACTED = "[REDACTED]"

_SENSITIVE_KEY_NAMES = {
    "SUPABASE_ANON_KEY",
    "SUPABASE_KEY",
    "SUPABASE_SERVICE_ROLE_KEY",
    "GOOGLE_CLIENT_SECRET",
    "GOOGLE_OAUTH_CLIENT_SECRET",
    "GMAIL_OAUTH_TOKEN",
    "ACCESS_TOKEN",
    "REFRESH_TOKEN",
    "CLIENT_SECRET",
}
_DEPENDENCY_LOG_LEVELS = {
    "httpx": logging.WARNING,
    "httpcore": logging.WARNING,
    "postgrest": logging.WARNING,
    "supabase": logging.WARNING,
    "gotrue": logging.WARNING,
    "storage3": logging.WARNING,
    "realtime": logging.WARNING,
    "google": logging.WARNING,
    "google.auth": logging.WARNING,
    "googleapiclient": logging.WARNING,
    "urllib3": logging.WARNING,
}

_FIELD_VALUE = r"(\[REDACTED\]|[^\s,;\"'{}\[\]]+)"
_AUTH_FIELD_PATTERN = re.compile(
    rf"(?i)\b(authorization|proxy-authorization)\b"
    rf"([\"']?\s*[:=]\s*[\"']?)(?:bearer\s+)?{_FIELD_VALUE}([\"']?)"
)
_SECRET_FIELD_PATTERN = re.compile(
    rf"(?i)\b(apikey|api[_-]?key|access[_-]?token|refresh[_-]?token|"
    rf"client[_-]?secret|service[_-]?role[_-]?key)\b"
    rf"([\"']?\s*[:=]\s*[\"']?){_FIELD_VALUE}([\"']?)"
)
_BEARER_PATTERN = re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/=-]+")
_JWT_PATTERN = re.compile(
    r"(?<![A-Za-z0-9_-])eyJ[A-Za-z0-9_-]{6,}\.[A-Za-z0-9_-]{6,}\."
    r"[A-Za-z0-9_-]{6,}(?![A-Za-z0-9_-])"
)
_SUPABASE_KEY_PATTERN = re.compile(r"\bsb_(?:secret|publishable)_[A-Za-z0-9_-]{12,}\b")


def _replace_named_field(match: re.Match[str]) -> str:
    """Preserve a credential field name and delimiter while redacting its value."""
    return f"{match.group(1)}{match.group(2)}{_REDACTED}{match.group(4)}"


def _collect_nested_secret_values(value, parent_key: str = "") -> set[str]:
    """Collect recognized secret values from a nested Streamlit secrets map."""
    values: set[str] = set()
    if isinstance(value, Mapping):
        for key, nested_value in value.items():
            normalized_key = str(key).upper()
            values.update(_collect_nested_secret_values(nested_value, normalized_key))
        return values

    if parent_key in _SENSITIVE_KEY_NAMES or any(
        marker in parent_key
        for marker in ("TOKEN", "SECRET", "API_KEY", "APIKEY", "SERVICE_ROLE_KEY")
    ):
        secret = str(value).strip()
        if len(secret) >= 8:
            values.add(secret)
    return values


@lru_cache(maxsize=1)
def _streamlit_secret_values() -> tuple[str, ...]:
    """Read recognized Streamlit secret values once without surfacing errors."""
    try:
        import streamlit as st

        return tuple(_collect_nested_secret_values(st.secrets.to_dict()))
    except Exception:
        return ()


def _known_secret_values() -> set[str]:
    """Return current recognized environment and Streamlit credential values."""
    values = set(_streamlit_secret_values())
    for key, value in os.environ.items():
        normalized_key = key.upper()
        if normalized_key in _SENSITIVE_KEY_NAMES or any(
            marker in normalized_key
            for marker in ("TOKEN", "SECRET", "API_KEY", "APIKEY", "SERVICE_ROLE_KEY")
        ):
            clean_value = value.strip()
            if len(clean_value) >= 8:
                values.add(clean_value)
    return values


def sanitize_log_text(value) -> str:
    """Redact credentials and credential-bearing fields from arbitrary text."""
    text = str(value)
    for secret in sorted(_known_secret_values(), key=len, reverse=True):
        text = text.replace(secret, _REDACTED)

    text = _AUTH_FIELD_PATTERN.sub(_replace_named_field, text)
    text = _SECRET_FIELD_PATTERN.sub(_replace_named_field, text)
    text = _BEARER_PATTERN.sub(f"Bearer {_REDACTED}", text)
    text = _JWT_PATTERN.sub(_REDACTED, text)
    return _SUPABASE_KEY_PATTERN.sub(_REDACTED, text)


def _sanitize_record(record: logging.LogRecord) -> None:
    """Mutate a record so every downstream handler receives safe text."""
    try:
        message = record.getMessage()
    except Exception:
        message = str(record.msg)
    record.msg = sanitize_log_text(message)
    record.args = ()

    if record.exc_info:
        exception_text = "".join(traceback.format_exception(*record.exc_info))
        record.exc_text = sanitize_log_text(exception_text)
        record.exc_info = None
    elif record.exc_text:
        record.exc_text = sanitize_log_text(record.exc_text)

    if record.stack_info:
        record.stack_info = sanitize_log_text(record.stack_info)


def _install_safe_record_factory() -> None:
    """Install one process-wide record factory that sanitizes before handlers."""
    current_factory = logging.getLogRecordFactory()
    if getattr(current_factory, "_myproject_credential_safe", False):
        return

    def credential_safe_factory(*args, **kwargs):
        record = current_factory(*args, **kwargs)
        _sanitize_record(record)
        return record

    credential_safe_factory._myproject_credential_safe = True  # type: ignore[attr-defined]
    logging.setLogRecordFactory(credential_safe_factory)


class CredentialSafeFormatter(logging.Formatter):
    """Apply final-output redaction, including custom fields and tracebacks."""

    def format(self, record: logging.LogRecord) -> str:
        _sanitize_record(record)
        return sanitize_log_text(super().format(record))


class SafeStreamHandler(logging.StreamHandler):
    """A StreamHandler that silently drops records when the stream is broken."""

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a record, swallowing broken-pipe errors silently."""
        try:
            msg = self.format(record)
            stream = self.stream
            terminator = getattr(self, "terminator", "\n")
            try:
                stream.write(msg + terminator)
                self.flush()
            except (BrokenPipeError, OSError) as exc:
                if isinstance(exc, BrokenPipeError) or getattr(exc, "errno", None) == 32:
                    return
                raise
        except RecursionError:
            raise
        except Exception:
            self.handleError(record)

    def handle(self, record: logging.LogRecord) -> bool:  # type: ignore[override]
        """Dispatch a record while ensuring pipe errors cannot escape."""
        rv = self.filter(record)
        if rv:
            self.acquire()
            try:
                self.emit(record)
            except (BrokenPipeError, OSError) as exc:
                if not (
                    isinstance(exc, BrokenPipeError)
                    or getattr(exc, "errno", None) == 32
                ):
                    raise
            finally:
                self.release()
        return rv  # type: ignore[return-value]


_logging_configured: bool = False


def configure_root_logging(
    level: int = _DEFAULT_LEVEL,
    stream=None,
    fmt: Optional[str] = None,
    datefmt: Optional[str] = None,
) -> None:
    """Configure credential-safe root logging once for the current process."""
    global _logging_configured
    if _logging_configured:
        return

    _install_safe_record_factory()

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    if not any(isinstance(handler, SafeStreamHandler) for handler in root_logger.handlers):
        handler = SafeStreamHandler(stream or sys.stderr)
        handler.setLevel(level)
        handler.setFormatter(
            CredentialSafeFormatter(
                fmt=fmt or _LOG_FORMAT,
                datefmt=datefmt or _DATE_FORMAT,
            )
        )
        root_logger.addHandler(handler)

    for logger_name, dependency_level in _DEPENDENCY_LOG_LEVELS.items():
        logging.getLogger(logger_name).setLevel(dependency_level)

    _logging_configured = True


def get_logger(name: str = "myproject") -> logging.Logger:
    """Return a named logger, lazily bootstrapping safe root logging."""
    if not _logging_configured:
        configure_root_logging()
    return logging.getLogger(name)
