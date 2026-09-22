from __future__ import annotations

import pytest

from apps.culture.provenance import (
    ProvenanceUrlError,
    is_valid_provenance_url,
    validate_provenance_url,
)


@pytest.mark.parametrize(
    "value",
    (
        "http://example.org/source",
        "https://user:secret@example.org/source",
        "https:///missing-host",
        " https://example.org/source",
        "javascript:alert(1)",
    ),
)
def test_provenance_url_rejects_non_publishable_links(value: str) -> None:
    with pytest.raises(ProvenanceUrlError, match="credential-free HTTPS"):
        validate_provenance_url(value)

    assert is_valid_provenance_url(value) is False


def test_provenance_url_accepts_absolute_https_source_page() -> None:
    value = "https://example.org/source?id=42#methodology"

    assert validate_provenance_url(value) == value
    assert is_valid_provenance_url(value) is True
