import io
import logging

import pytest

import myproject.logger as project_logger


SYNTHETIC_SECRET = "synthetic-service-role-secret-123456"
SYNTHETIC_JWT = (
    "eyJhbGciOiJIUzI1NiJ9."
    "eyJzdWIiOiJzeW50aGV0aWMtdXNlciJ9."
    "syntheticSignature123"
)


@pytest.fixture(autouse=True)
def restore_logging_state():
    root_logger = logging.getLogger()
    original_handlers = root_logger.handlers[:]
    original_level = root_logger.level
    original_factory = logging.getLogRecordFactory()
    dependency_levels = {
        name: logging.getLogger(name).level
        for name in project_logger._DEPENDENCY_LOG_LEVELS
    }
    original_configured = project_logger._logging_configured
    project_logger._streamlit_secret_values.cache_clear()
    yield
    root_logger.handlers[:] = original_handlers
    root_logger.setLevel(original_level)
    logging.setLogRecordFactory(original_factory)
    for name, level in dependency_levels.items():
        logging.getLogger(name).setLevel(level)
    project_logger._logging_configured = original_configured
    project_logger._streamlit_secret_values.cache_clear()


@pytest.mark.parametrize(
    "unsafe_text",
    [
        f"Authorization: Bearer {SYNTHETIC_SECRET}",
        f"'Authorization': 'Bearer {SYNTHETIC_SECRET}'",
        f"apikey={SYNTHETIC_SECRET}",
        f"'access_token': '{SYNTHETIC_SECRET}'",
        f'"refresh-token": "{SYNTHETIC_SECRET}"',
        f"client_secret={SYNTHETIC_SECRET}",
        f"token={SYNTHETIC_JWT}",
        "Supabase key sb_secret_synthetic1234567890",
    ],
)
def test_sanitize_log_text_redacts_credential_patterns(unsafe_text):
    sanitized = project_logger.sanitize_log_text(unsafe_text)

    assert SYNTHETIC_SECRET not in sanitized
    assert SYNTHETIC_JWT not in sanitized
    assert "sb_secret_synthetic1234567890" not in sanitized
    assert project_logger._REDACTED in sanitized


def test_sanitize_log_text_redacts_known_environment_secret(monkeypatch):
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", SYNTHETIC_SECRET)

    sanitized = project_logger.sanitize_log_text(
        f"Request failed while using {SYNTHETIC_SECRET}"
    )

    assert SYNTHETIC_SECRET not in sanitized
    assert sanitized.endswith(project_logger._REDACTED)


def test_sanitize_log_text_preserves_non_sensitive_message():
    message = "Updated jobs record 42 with 3 changed fields"

    assert project_logger.sanitize_log_text(message) == message


def test_formatter_redacts_interpolated_arguments_and_exception_text(monkeypatch):
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", SYNTHETIC_SECRET)
    stream = io.StringIO()
    handler = project_logger.SafeStreamHandler(stream)
    handler.setFormatter(project_logger.CredentialSafeFormatter("%(message)s"))
    logger = logging.getLogger("tests.credential-safe-formatter")
    logger.handlers = [handler]
    logger.propagate = False
    logger.setLevel(logging.DEBUG)

    try:
        raise RuntimeError(f"backend rejected apikey={SYNTHETIC_SECRET}")
    except RuntimeError:
        logger.exception("Request Authorization: Bearer %s", SYNTHETIC_SECRET)

    output = stream.getvalue()
    assert SYNTHETIC_SECRET not in output
    assert "Authorization:" in output
    assert "RuntimeError" in output
    assert output.count(project_logger._REDACTED) >= 2


def test_configure_root_logging_sets_safe_defaults_and_is_idempotent():
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    project_logger._logging_configured = False
    stream = io.StringIO()

    project_logger.configure_root_logging(stream=stream)
    project_logger.configure_root_logging(stream=io.StringIO())

    safe_handlers = [
        handler
        for handler in root_logger.handlers
        if isinstance(handler, project_logger.SafeStreamHandler)
    ]
    assert root_logger.level == logging.INFO
    assert len(safe_handlers) == 1
    assert safe_handlers[0].stream is stream
    assert isinstance(safe_handlers[0].formatter, project_logger.CredentialSafeFormatter)
    for logger_name in project_logger._DEPENDENCY_LOG_LEVELS:
        assert logging.getLogger(logger_name).level == logging.WARNING


def test_configure_root_logging_allows_explicit_debug_level():
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    project_logger._logging_configured = False

    project_logger.configure_root_logging(level=logging.DEBUG, stream=io.StringIO())

    assert root_logger.level == logging.DEBUG
    safe_handler = next(
        handler
        for handler in root_logger.handlers
        if isinstance(handler, project_logger.SafeStreamHandler)
    )
    assert safe_handler.level == logging.DEBUG


class BrokenPipeStream:
    def write(self, _value):
        raise BrokenPipeError()

    def flush(self):
        raise BrokenPipeError()


def test_safe_stream_handler_swallows_broken_pipe():
    handler = project_logger.SafeStreamHandler(BrokenPipeStream())
    handler.setFormatter(project_logger.CredentialSafeFormatter("%(message)s"))
    record = logging.LogRecord(
        name="tests.broken-pipe",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="safe diagnostic",
        args=(),
        exc_info=None,
    )

    assert handler.handle(record)
