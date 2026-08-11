"""
myproject/logger.py
-------------------
Centralised logging configuration for the Streamlit dashboard.

Why this module exists
~~~~~~~~~~~~~~~~~~~~~~
Streamlit runs inside a subprocess whose stdout/stderr can close while the
Python process is still running (e.g. during a page rerun or when the
browser disconnects).  A plain ``print(..., flush=True)`` call on a closed
pipe raises ``BrokenPipeError: [Errno 32] Broken pipe`` and, if not caught,
crashes the Streamlit rerun loop.

This module provides:
  • ``get_logger(name)``  — returns a named Logger that is safe to use in
    any Streamlit component or data-loading module.
  • ``SafeStreamHandler`` — a custom StreamHandler that swallows
    ``BrokenPipeError`` / ``OSError(32)`` without crashing.
  • ``configure_root_logging()`` — call once from ``main.py`` at startup to
    bootstrap the root logger with the correct level, format, and handler.

Usage
~~~~~
    from myproject.logger import get_logger

    logger = get_logger(__name__)

    logger.debug("=== SAVE BUTTON CLICKED ===")
    logger.warning("No changes detected.")
    logger.error("Supabase update error: %s", exc)
"""

import logging
import sys
from typing import Optional


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S"
_DEFAULT_LEVEL = logging.DEBUG


# ---------------------------------------------------------------------------
# BrokenPipe-safe stream handler
# ---------------------------------------------------------------------------
class SafeStreamHandler(logging.StreamHandler):
    """A StreamHandler that silently drops records when the stream is broken.

    On macOS/Linux, writing to a closed stdout/stderr raises::

        BrokenPipeError: [Errno 32] Broken pipe

    The built-in ``StreamHandler.emit()`` calls ``self.handleError(record)``
    which *also* tries to write to stderr, potentially looping or crashing.

    On Python 3.14+, ``logging.Handler.handle()`` propagates exceptions raised
    inside ``emit()`` without catching them (CPython gh-107603).  This subclass
    therefore reimplements ``handle()`` from scratch — directly managing the
    handler lock and calling our safe ``emit()`` — so BrokenPipeError can
    never reach the Streamlit run loop regardless of Python version.
    """

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a record, swallowing broken-pipe errors silently."""
        try:
            msg = self.format(record)
            stream = self.stream
            # Use terminator from StreamHandler; fallback to newline.
            terminator = getattr(self, "terminator", "\n")
            try:
                stream.write(msg + terminator)
                self.flush()
            except (BrokenPipeError, OSError) as exc:
                if isinstance(exc, BrokenPipeError) or getattr(exc, "errno", None) == 32:
                    return  # Silently discard — stream is gone.
                raise
        except RecursionError:
            raise
        except Exception:
            self.handleError(record)

    def handle(self, record: logging.LogRecord) -> bool:  # type: ignore[override]
        """Dispatch a record, holding the handler lock and swallowing pipe errors.

        Re-implements ``logging.Handler.handle()`` from scratch so that we own
        the full try/except around ``emit()``.  This is necessary on Python
        3.14+ where ``Handler.handle()`` no longer wraps ``emit()`` in a
        try/except (CPython gh-107603).
        """
        rv = self.filter(record)
        if rv:
            self.acquire()
            try:
                self.emit(record)
            except (BrokenPipeError, OSError) as exc:
                # Belt-and-suspenders: if emit() somehow re-raises after our
                # internal guard (e.g. during format()), catch it here too.
                if not (isinstance(exc, BrokenPipeError) or getattr(exc, "errno", None) == 32):
                    raise
            finally:
                self.release()
        return rv  # type: ignore[return-value]



# ---------------------------------------------------------------------------
# Module-level bootstrap state
# ---------------------------------------------------------------------------
_logging_configured: bool = False


def configure_root_logging(
    level: int = _DEFAULT_LEVEL,
    stream=None,
    fmt: Optional[str] = None,
    datefmt: Optional[str] = None,
) -> None:
    """Configure the root logger with a ``SafeStreamHandler``.

    Call this **once** from ``main.py`` before the first ``get_logger()``
    call.  Subsequent calls are no-ops (idempotent).

    Parameters
    ----------
    level:
        Logging level for the root logger (default ``DEBUG``).
    stream:
        Output stream (default ``sys.stderr``).  stderr is preferred over
        stdout for logging so that Streamlit's own stdout pipeline is not
        polluted.
    fmt:
        Log record format string (default: ``_LOG_FORMAT``).
    datefmt:
        Date/time format string (default: ``_DATE_FORMAT``).
    """
    global _logging_configured
    if _logging_configured:
        return

    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Avoid adding duplicate handlers when Streamlit hot-reloads the module.
    if not any(isinstance(h, SafeStreamHandler) for h in root_logger.handlers):
        handler = SafeStreamHandler(stream or sys.stderr)
        handler.setLevel(level)
        formatter = logging.Formatter(
            fmt=fmt or _LOG_FORMAT,
            datefmt=datefmt or _DATE_FORMAT,
        )
        handler.setFormatter(formatter)
        root_logger.addHandler(handler)

    _logging_configured = True


def get_logger(name: str = "myproject") -> logging.Logger:
    """Return a named logger, ensuring root logging is bootstrapped.

    If ``configure_root_logging()`` has not been called yet (e.g. in a
    test or when a component is imported directly), this function performs
    a lazy bootstrap with default settings so that log messages are never
    silently discarded.

    Parameters
    ----------
    name:
        Logger name.  Pass ``__name__`` from the calling module so log
        records include the originating module path.

    Returns
    -------
    logging.Logger
    """
    if not _logging_configured:
        configure_root_logging()
    return logging.getLogger(name)
