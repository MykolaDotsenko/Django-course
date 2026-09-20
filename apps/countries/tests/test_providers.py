from datetime import UTC, datetime

import pytest

from apps.countries.providers import CountrySourceError, parse_country_object


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
