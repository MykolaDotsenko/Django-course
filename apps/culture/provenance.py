from __future__ import annotations

from urllib.parse import urlsplit

from django.core.exceptions import ValidationError
from django.core.validators import URLValidator


class ProvenanceUrlError(ValueError):
    """Raised when a user-visible provenance link is not safe to publish."""


_HTTPS_URL_VALIDATOR = URLValidator(schemes=("https",))
_ERROR_MESSAGE = "Source URL must be an absolute credential-free HTTPS URL."


def validate_provenance_url(value: str) -> str:
    """Validate a provenance link before it can enter a user-visible published surface."""

    if not isinstance(value, str):
        raise ProvenanceUrlError(_ERROR_MESSAGE)

    normalized = value.strip()
    if not normalized or normalized != value:
        raise ProvenanceUrlError(_ERROR_MESSAGE)

    try:
        _HTTPS_URL_VALIDATOR(normalized)
        parsed = urlsplit(normalized)
        hostname = parsed.hostname
        # Accessing port also validates malformed bracket/port syntax.
        _ = parsed.port
    except (ValidationError, ValueError) as exc:
        raise ProvenanceUrlError(_ERROR_MESSAGE) from exc

    if (
        parsed.scheme.lower() != "https"
        or not hostname
        or parsed.username is not None
        or parsed.password is not None
    ):
        raise ProvenanceUrlError(_ERROR_MESSAGE)

    return normalized


def is_valid_provenance_url(value: str) -> bool:
    try:
        validate_provenance_url(value)
    except ProvenanceUrlError:
        return False
    return True
