from datetime import UTC, datetime
from io import BytesIO
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

import pytest

from apps.countries.providers import (
    CountrySourceError,
    RestCountriesV5Client,
    parse_country_object,
)


def test_rest_countries_v5_object_normalizes_owned_fields_only():
    snapshot = parse_country_object(
        {
            "names": {"common": "Finland", "official": "Republic of Finland"},
            "codes": {"alpha_2": "FI", "alpha_3": "FIN"},
            "capitals": [{"name": "Helsinki", "primary": True}],
            "region": "Europe",
            "subregion": "Northern Europe",
            "currencies": [{"code": "EUR", "name": "Euro", "symbol": "€", "minor_units": 2}],
            "flag": {"url_svg": "https://example.test/fi.svg"},
            "population": 999999999,
        },
        fetched_at=datetime(2026, 9, 20, tzinfo=UTC),
    )

    assert snapshot.iso2 == "FI"
    assert snapshot.iso3 == "FIN"
    assert snapshot.capital == "Helsinki"
    assert snapshot.currencies[0].code == "EUR"
    assert not hasattr(snapshot, "population")


def test_rest_countries_v5_object_rejects_missing_identity():
    with pytest.raises(CountrySourceError):
        parse_country_object({}, fetched_at=datetime(2026, 9, 20, tzinfo=UTC))


class FakeResponse(BytesIO):
    def __init__(self, payload: bytes, *, status: int = 200):
        super().__init__(payload)
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()
        return False


def _page(objects, *, more=False, count=None):
    import json

    meta = {"more": more}
    if count is not None:
        meta["count"] = count
    return FakeResponse(json.dumps({"data": {"objects": objects, "meta": meta}}).encode())


def _finland_payload():
    return {
        "names": {"common": "Finland", "official": "Republic of Finland"},
        "codes": {"alpha_2": "FI", "alpha_3": "FIN"},
        "capitals": [{"name": "Helsinki"}],
        "region": "Europe",
        "subregion": "Northern Europe",
        "currencies": [
            {"code": "EUR", "name": "Euro", "symbol": "€", "minor_units": 2},
            {"code": "TOOLONG", "name": "Invalid"},
            {"code": "JPY", "name": "Japanese yen", "minor_units": 99},
        ],
        "flag": {"url_svg": "https://example.test/fi.svg"},
    }


def test_rest_countries_v5_client_sends_bearer_fields_and_paginates():
    first = _page([_finland_payload()], more=True, count=1)
    second = _page(
        [
            {
                "names": {"common": "Japan", "official": "Japan"},
                "codes": {"alpha_2": "JP", "alpha_3": "JPN"},
                "currencies": {"JPY": {"name": "Japanese yen", "symbol": "¥", "decimal_digits": 0}},
            }
        ],
        more=False,
    )
    requests = []

    def fake_urlopen(request, *, timeout):
        requests.append((request, timeout))
        return first if len(requests) == 1 else second

    client = RestCountriesV5Client(
        api_key="secret",
        base_url="https://countries.example.test/v5/",
        timeout_seconds=3.5,
    )
    with patch("apps.countries.providers.urlopen", side_effect=fake_urlopen):
        snapshots = client.fetch_all()

    assert [snapshot.iso2 for snapshot in snapshots] == ["FI", "JP"]
    assert [snapshot.currencies[0].code for snapshot in snapshots] == ["EUR", "JPY"]
    assert snapshots[0].currencies[1].code == "JPY"
    assert snapshots[0].currencies[1].minor_units == 2
    assert all(timeout == 3.5 for _, timeout in requests)

    first_request = requests[0][0]
    assert first_request.get_header("Authorization") == "Bearer secret"
    assert first_request.get_header("Accept") == "application/json"
    assert first_request.get_header("User-agent") == "cultural-currency-converter/0.1"
    first_query = parse_qs(urlparse(first_request.full_url).query)
    second_query = parse_qs(urlparse(requests[1][0].full_url).query)
    assert first_query["limit"] == ["100"]
    assert first_query["offset"] == ["0"]
    assert "names.common" in first_query["response_fields"][0]
    assert second_query["offset"] == ["1"]


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        (b"[]", "response shape is invalid"),
        (
            b'{"data":{"objects":[],"meta":{"more":true,"count":"bad"}}}',
            "pagination count is invalid",
        ),
        (b'{"data":{"objects":[],"meta":{"more":true,"count":0}}}', "pagination made no progress"),
    ],
)
def test_rest_countries_v5_client_normalizes_invalid_provider_payloads(payload, message):
    client = RestCountriesV5Client(api_key="secret")

    with (
        patch("apps.countries.providers.urlopen", return_value=FakeResponse(payload)),
        pytest.raises(CountrySourceError, match=message),
    ):
        client.fetch_all()


def test_rest_countries_v5_client_normalizes_http_and_transport_failures():
    client = RestCountriesV5Client(api_key="secret")

    with (
        patch(
            "apps.countries.providers.urlopen",
            return_value=FakeResponse(b"{}", status=503),
        ),
        pytest.raises(CountrySourceError, match="HTTP 503"),
    ):
        client.fetch_all()

    with (
        patch("apps.countries.providers.urlopen", side_effect=TimeoutError("timeout")),
        pytest.raises(CountrySourceError, match="request failed"),
    ):
        client.fetch_all()


def test_rest_countries_v5_client_rejects_malformed_json():
    client = RestCountriesV5Client(api_key="secret")

    with (
        patch(
            "apps.countries.providers.urlopen",
            return_value=FakeResponse(b"{not-json"),
        ),
        pytest.raises(CountrySourceError, match="request failed"),
    ):
        client.fetch_all()


def test_rest_countries_v5_client_bounds_runaway_pagination():
    client = RestCountriesV5Client(api_key="secret")

    with (
        patch(
            "apps.countries.providers.urlopen",
            side_effect=lambda *args, **kwargs: _page([], more=True, count=1),
        ) as mocked_urlopen,
        pytest.raises(CountrySourceError, match="pagination exceeded the safety limit"),
    ):
        client.fetch_all()

    assert mocked_urlopen.call_count == 10


def test_rest_countries_v5_client_requires_api_key():
    with pytest.raises(ValueError, match="API key is required"):
        RestCountriesV5Client(api_key="")
