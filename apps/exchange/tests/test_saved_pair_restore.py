from datetime import date

import pytest

from apps.countries.models import Country, CountryCurrency, Currency


@pytest.fixture
def saved_pair_reference_data(db):
    finland = Country.objects.create(iso2="FI", iso3="FIN", name="Finland")
    japan = Country.objects.create(iso2="JP", iso3="JPN", name="Japan")
    eur = Currency.objects.create(code="EUR", name="Euro", symbol="€", minor_units=2)
    jpy = Currency.objects.create(code="JPY", name="Japanese yen", symbol="¥", minor_units=0)
    CountryCurrency.objects.create(
        country=finland,
        currency=eur,
        is_primary=True,
        valid_from=date(2002, 1, 1),
        source="test",
    )
    CountryCurrency.objects.create(
        country=japan,
        currency=jpy,
        is_primary=True,
        source="test",
    )
    return finland, japan, eur, jpy


@pytest.mark.django_db
def test_load_saved_pair_restores_context_without_conversion(
    client,
    saved_pair_reference_data,
    monkeypatch,
):
    def unexpected_quote(*args, **kwargs):
        raise AssertionError("Loading a saved pair must not request an FX quote.")

    monkeypatch.setattr("apps.exchange.views.quote_conversion", unexpected_quote)

    response = client.get(
        "/",
        {
            "load": "1",
            "source_country": "FI",
            "source_currency": "EUR",
            "destination_country": "JP",
            "destination_currency": "JPY",
        },
    )

    assert response.status_code == 200
    form = response.context["form"]
    assert form.initial["amount"] == ""
    assert form.initial["source_country"] == "FI"
    assert form.initial["source_currency"] == "EUR"
    assert form.initial["destination_country"] == "JP"
    assert form.initial["destination_currency"] == "JPY"
    assert response.context["result_component"] is None


@pytest.mark.django_db
def test_load_saved_pair_drops_invalid_country_currency_association(
    client,
    saved_pair_reference_data,
):
    response = client.get(
        "/",
        {
            "load": "1",
            "source_country": "JP",
            "source_currency": "EUR",
            "destination_country": "JP",
            "destination_currency": "JPY",
        },
    )

    assert response.status_code == 200
    form = response.context["form"]
    assert form.initial["source_currency"] == "EUR"
    assert form.initial["source_country"] == ""
    assert form.initial["destination_country"] == "JP"
