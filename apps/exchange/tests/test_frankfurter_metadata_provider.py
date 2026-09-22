import json
from datetime import UTC, datetime
from http.client import HTTPException
from io import BytesIO
from unittest.mock import patch
from urllib.error import HTTPError, URLError

import pytest

from apps.exchange.providers.frankfurter_metadata import (
    MAX_METADATA_RESPONSE_BYTES,
    FrankfurterMetadataClient,
    FrankfurterMetadataError,
    build_currency_coverage_snapshots,
)

FETCHED_AT = datetime(2026, 9, 22, 8, tzinfo=UTC)


class FakeResponse(BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
        return False


class FailingReadResponse:
    def __init__(self, error):
        self.error = error

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self, size=-1):
        raise self.error


def _json_response(payload) -> FakeResponse:
    return FakeResponse(json.dumps(payload).encode())


def _currency(code: str, name: str, *, start="1999-01-04", end="2026-09-18"):
    return {
        "iso_code": code,
        "name": name,
        "symbol": code,
        "start_date": start,
        "end_date": end,
    }


def test_metadata_client_fetches_active_and_all_with_expected_headers():
    active = [_currency("EUR", "Euro")]
    all_rows = [*active, _currency("FIM", "Finnish Markka", start="1972-01-03", end="2001-12-28")]
    requests = []
    responses = iter([_json_response(active), _json_response(all_rows)])

    def fake_urlopen(request, *, timeout):
        requests.append((request, timeout))
        return next(responses)

    client = FrankfurterMetadataClient(
        base_url="https://fx.example.test/v2/",
        timeout_seconds=4.5,
    )
    with patch("apps.exchange.providers.frankfurter_metadata.urlopen", side_effect=fake_urlopen):
        snapshots = client.fetch_currency_coverage()

    assert [item.code for item in snapshots] == ["EUR", "FIM"]
    assert snapshots[0].coverage_to_is_terminal is False
    assert snapshots[1].coverage_to_is_terminal is True
    assert [request.full_url for request, _ in requests] == [
        "https://fx.example.test/v2/currencies",
        "https://fx.example.test/v2/currencies?scope=all",
    ]
    assert all(timeout == 4.5 for _, timeout in requests)
    assert all(request.get_header("Accept") == "application/json" for request, _ in requests)
    assert all(
        request.get_header("User-agent") == "cultural-currency-converter/0.1"
        for request, _ in requests
    )


def test_metadata_client_requires_positive_timeout():
    with pytest.raises(ValueError, match="timeout must be positive"):
        FrankfurterMetadataClient(timeout_seconds=0)


@pytest.mark.parametrize(
    "error",
    [
        URLError("dns"),
        HTTPException("incomplete response"),
        TimeoutError("timeout"),
        ConnectionResetError("reset by peer"),
    ],
)
def test_metadata_client_normalizes_transport_and_read_failures(error):
    client = FrankfurterMetadataClient()

    if isinstance(error, (HTTPException, ConnectionResetError)):
        mocked = patch(
            "apps.exchange.providers.frankfurter_metadata.urlopen",
            return_value=FailingReadResponse(error),
        )
    else:
        mocked = patch(
            "apps.exchange.providers.frankfurter_metadata.urlopen",
            side_effect=error,
        )

    with mocked, pytest.raises(FrankfurterMetadataError, match="request failed"):
        client._fetch_json("https://fx.example.test/currencies")


def test_metadata_client_maps_http_error_separately():
    client = FrankfurterMetadataClient()
    error = HTTPError(
        "https://fx.example.test/currencies",
        503,
        "Unavailable",
        hdrs=None,
        fp=None,
    )

    with (
        patch("apps.exchange.providers.frankfurter_metadata.urlopen", side_effect=error),
        pytest.raises(FrankfurterMetadataError, match="HTTP 503"),
    ):
        client._fetch_json("https://fx.example.test/currencies")


def test_metadata_client_rejects_response_over_size_limit():
    client = FrankfurterMetadataClient()
    oversized = FakeResponse(b"x" * (MAX_METADATA_RESPONSE_BYTES + 1))

    with (
        patch("apps.exchange.providers.frankfurter_metadata.urlopen", return_value=oversized),
        pytest.raises(FrankfurterMetadataError, match="exceeded the size limit"),
    ):
        client._fetch_json("https://fx.example.test/currencies")


@pytest.mark.parametrize("payload", [b"{not-json", b"\xff"])
def test_metadata_client_rejects_malformed_json_and_unicode(payload):
    client = FrankfurterMetadataClient()

    with (
        patch(
            "apps.exchange.providers.frankfurter_metadata.urlopen",
            return_value=FakeResponse(payload),
        ),
        pytest.raises(FrankfurterMetadataError, match="malformed JSON"),
    ):
        client._fetch_json("https://fx.example.test/currencies")


@pytest.mark.parametrize(
    ("active_payload", "all_payload", "message"),
    [
        ({}, [], "must be an array"),
        ([None], [], "row must be an object"),
        ([{"iso_code": "EU", "name": "Euro"}], [], "missing canonical identity"),
        ([{"iso_code": "€€€", "name": "Euro"}], [], "missing canonical identity"),
        ([{"iso_code": "EUR", "name": ""}], [], "missing canonical identity"),
        (
            [],
            [
                {"iso_code": "EUR", "name": "Euro"},
                {"iso_code": "eur", "name": "Euro duplicate"},
            ],
            "duplicate code EUR",
        ),
    ],
)
def test_metadata_parser_rejects_invalid_row_shapes(active_payload, all_payload, message):
    with pytest.raises(FrankfurterMetadataError, match=message):
        build_currency_coverage_snapshots(
            active_payload,
            all_payload,
            fetched_at=FETCHED_AT,
        )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("start_date", "not-a-date"),
        ("end_date", "2026-13-99"),
    ],
)
def test_metadata_parser_rejects_invalid_coverage_dates(field, value):
    row = _currency("EUR", "Euro")
    row[field] = value

    with pytest.raises(FrankfurterMetadataError, match=f"invalid {field}"):
        build_currency_coverage_snapshots([], [row], fetched_at=FETCHED_AT)


def test_metadata_parser_accepts_missing_optional_dates_and_symbol():
    snapshots = build_currency_coverage_snapshots(
        [],
        [{"iso_code": "FIM", "name": "Finnish Markka"}],
        fetched_at=FETCHED_AT,
    )

    assert len(snapshots) == 1
    snapshot = snapshots[0]
    assert snapshot.coverage_from is None
    assert snapshot.coverage_to is None
    assert snapshot.symbol == ""
    assert snapshot.coverage_to_is_terminal is True
