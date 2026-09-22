import json
from datetime import UTC, datetime
from unittest.mock import patch

import pytest

from apps.countries.providers import (
    MAX_RESPONSE_BYTES,
    CountrySourceError,
    RestCountriesV5Client,
    parse_country_object,
)

FETCHED_AT = datetime(2026, 9, 20, tzinfo=UTC)


class FakeResponse:
    def __init__(self, payload: bytes, *, status: int = 200):
        self.payload = payload
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self, size=-1):
        return self.payload if size < 0 else self.payload[:size]


def country_payload(
    iso2="FI",
    iso3="FIN",
    name="Finland",
    *,
    currencies=None,
):
    return {
        "names": {"common": name, "official": f"Republic of {name}"},
        "codes": {"alpha_2": iso2, "alpha_3": iso3},
        "capitals": [{"name": "Helsinki", "primary": True}],
        "region": {"name": "Europe"},
        "subregion": {"value": "Northern Europe"},
        "currencies": currencies
        if currencies is not None
        else [{"code": "EUR", "name": "Euro", "symbol": "€", "minor_units": 2}],
        "flag": {"url_svg": "https://example.test/fi.svg"},
        "population": 999999999,
    }


def paged_payload(objects, *, more=False, count=None):
    meta = {"more": more}
    if count is not None:
        meta["count"] = count
    return json.dumps({"data": {"objects": objects, "meta": meta}}).encode()


def test_rest_countries_v5_object_normalizes_owned_fields_only():
    snapshot = parse_country_object(country_payload(), fetched_at=FETCHED_AT)

    assert snapshot.iso2 == "FI"
    assert snapshot.iso3 == "FIN"
    assert snapshot.capital == "Helsinki"
    assert snapshot.region == "Europe"
    assert snapshot.subregion == "Northern Europe"
    assert snapshot.currencies[0].code == "EUR"
    assert not hasattr(snapshot, "population")


@pytest.mark.parametrize(
    ("iso2", "iso3"),
    [
        ("", "FIN"),
        ("F1", "FIN"),
        ("FÍ", "FIN"),
        ("FI", "F1N"),
        ("FI", "FÍN"),
    ],
)
def test_rest_countries_v5_object_rejects_noncanonical_identity(iso2, iso3):
    with pytest.raises(CountrySourceError, match="canonical country identity"):
        parse_country_object(country_payload(iso2=iso2, iso3=iso3), fetched_at=FETCHED_AT)


def test_rest_countries_currency_parser_filters_bad_codes_and_bounds_minor_units():
    snapshot = parse_country_object(
        country_payload(
            currencies=[
                {"code": "EUR", "name": "Euro", "symbol": "€", "minor_units": 2},
                {"code": "U1D", "name": "Invalid"},
                {"code": "ÅAA", "name": "Unicode invalid"},
                {"code": "JPY", "name": "Yen", "minor_units": -1},
                {"code": "KWD", "name": "Kuwaiti dinar", "decimal_digits": "3"},
                {"code": "BHD", "name": "Bahraini dinar", "minor_units": "bad"},
                "not-an-object",
            ]
        ),
        fetched_at=FETCHED_AT,
    )

    assert [item.code for item in snapshot.currencies] == ["BHD", "EUR", "JPY", "KWD"]
    assert {item.code: item.minor_units for item in snapshot.currencies} == {
        "BHD": 2,
        "EUR": 2,
        "JPY": 2,
        "KWD": 3,
    }


@pytest.mark.parametrize("timeout", [0, -1])
def test_rest_countries_client_requires_positive_timeout(timeout):
    with pytest.raises(ValueError, match="timeout must be positive"):
        RestCountriesV5Client(api_key="secret", timeout_seconds=timeout)


def test_rest_countries_client_requires_api_key():
    with pytest.raises(ValueError, match="API key"):
        RestCountriesV5Client(api_key="")


def test_rest_countries_client_fetches_all_pages_with_bounded_offsets_and_headers():
    first = FakeResponse(paged_payload([country_payload()], more=True, count=1))
    second = FakeResponse(
        paged_payload(
            [country_payload(iso2="JP", iso3="JPN", name="Japan")],
            more=False,
            count=1,
        )
    )
    client = RestCountriesV5Client(
        api_key="test-key",
        base_url="https://countries.example.test/v5/",
        timeout_seconds=7,
    )

    with patch("apps.countries.providers.urlopen", side_effect=[first, second]) as mocked:
        snapshots = client.fetch_all()

    assert [item.iso2 for item in snapshots] == ["FI", "JP"]
    assert mocked.call_count == 2
    first_request = mocked.call_args_list[0].args[0]
    second_request = mocked.call_args_list[1].args[0]
    assert "limit=100" in first_request.full_url
    assert "offset=0" in first_request.full_url
    assert "offset=1" in second_request.full_url
    assert first_request.get_header("Authorization") == "Bearer test-key"
    assert first_request.get_header("User-agent") == "cultural-currency-converter/0.1"
    assert mocked.call_args_list[0].kwargs["timeout"] == 7


def test_rest_countries_client_rejects_non_200_response():
    client = RestCountriesV5Client(api_key="test-key")
    with patch(
        "apps.countries.providers.urlopen",
        return_value=FakeResponse(b"{}", status=503),
    ):
        with pytest.raises(CountrySourceError, match="HTTP 503"):
            client.fetch_all()


def test_rest_countries_client_normalizes_network_failure():
    client = RestCountriesV5Client(api_key="test-key")
    with patch("apps.countries.providers.urlopen", side_effect=OSError("network down")):
        with pytest.raises(CountrySourceError, match="request failed"):
            client.fetch_all()


def test_rest_countries_client_rejects_oversized_response_before_json_parsing():
    client = RestCountriesV5Client(api_key="test-key")
    response = FakeResponse(b"x" * (MAX_RESPONSE_BYTES + 1))

    with patch("apps.countries.providers.urlopen", return_value=response):
        with pytest.raises(CountrySourceError, match="size limit"):
            client.fetch_all()


@pytest.mark.parametrize("payload", [b"{broken", b'{"data": {"objects": [], "meta": '])
def test_rest_countries_client_rejects_malformed_json(payload):
    client = RestCountriesV5Client(api_key="test-key")

    with patch("apps.countries.providers.urlopen", return_value=FakeResponse(payload)):
        with pytest.raises(CountrySourceError, match="malformed JSON"):
            client.fetch_all()


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"data": None},
        {"data": {"objects": {}, "meta": {}}},
        {"data": {"objects": [], "meta": []}},
    ],
)
def test_rest_countries_client_rejects_malformed_response_shape(payload):
    client = RestCountriesV5Client(api_key="test-key")

    with patch(
        "apps.countries.providers.urlopen",
        return_value=FakeResponse(json.dumps(payload).encode()),
    ):
        with pytest.raises(CountrySourceError, match="response shape is invalid"):
            client.fetch_all()


@pytest.mark.parametrize(
    ("count", "message"),
    [
        (0, "made no progress"),
        ("bad", "metadata is invalid"),
    ],
)
def test_rest_countries_client_rejects_invalid_pagination_metadata(count, message):
    client = RestCountriesV5Client(api_key="test-key")
    response = FakeResponse(paged_payload([], more=True, count=count))

    with patch("apps.countries.providers.urlopen", return_value=response):
        with pytest.raises(CountrySourceError, match=message):
            client.fetch_all()
