from __future__ import annotations

import json
import logging
import os
import re
from contextvars import ContextVar, Token
from datetime import UTC, datetime
from uuid import uuid4

_REQUEST_ID = ContextVar("request_id", default=None)
_REQUEST_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")
_SERVICE_NAME = "cultural-currency-converter"

_LOG_FIELDS = (
    "method",
    "path",
    "route",
    "status_code",
    "duration_ms",
    "error_code",
    "provider",
    "cache_status",
)


def normalize_request_id(value: str | None) -> str:
    """Return a validated client request ID or generate a new opaque UUID."""

    if value is not None and _REQUEST_ID_PATTERN.fullmatch(value):
        return value
    return str(uuid4())


def bind_request_id(request_id: str) -> Token[str | None]:
    """Bind a request ID to the current execution context."""

    return _REQUEST_ID.set(request_id)


def reset_request_id(token: Token[str | None]) -> None:
    """Restore the previous request correlation context."""

    _REQUEST_ID.reset(token)


def get_request_id() -> str | None:
    """Return the request ID bound to the current execution context."""

    return _REQUEST_ID.get()


class JsonFormatter(logging.Formatter):
    """Emit a small stable JSON log envelope without serializing request data."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "timestamp": datetime.now(UTC).isoformat(timespec="milliseconds"),
            "level": record.levelname,
            "logger": record.name,
            "environment": os.environ.get("APP_ENV", "local"),
            "service": _SERVICE_NAME,
            "request_id": getattr(record, "request_id", None) or get_request_id(),
            "event": record.getMessage(),
        }

        for field_name in _LOG_FIELDS:
            value = getattr(record, field_name, None)
            if value is not None:
                payload[field_name] = value

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
