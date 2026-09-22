from datetime import date

import pytest

from apps.countries.models import Country, CountryCurrency, Currency
from apps.exchange.queries import search_currency_options


@pytest.fixture
def picker_reference_data(db):
    fi = Country.objects.create(iso2="FI", iso3="FIN", name="Finland")
    jp = Country.objects.create(iso2="JP", iso3="JPN", name="Japan")
    eur = Currency.objects.create(code="EUR", name="Euro")
    jpy = Currency.objects.create(code="JPY", name="Japanese yen", minor_units=0)
    fim = Currency.objects.create(
        code="FIM",
        name="Finnish markka",
        is_active=False,
        active_to=date(2001, 12, 31),
    )

    CountryCurrency.objects.create(
        country=fi,
        currency=fim,
        is_primary=True,
        valid_to=date(2001, 12, 31),
        source="test",
    )
    CountryCurrency.objects.create(
        country=fi,
        currency=eur,
        is_primary=True,
        valid_from=date(2002, 1, 1),
        source="test",
    )
    CountryCurrency.objects.create(
        country=jp,
        currency=jpy,
        is_primary=True,
        source="test",
    )
    return {"fi": fi, "jp": jp, "eur": eur, "jpy": jpy, "fim": fim}


@pytest.mark.django_db
def test_picker_prioritizes_current_selection_when_query_is_empty(picker_reference_data):
    options = search_currency_options(
        query="",
        historical_mode=False,
        preferred_country_code="JP",
        preferred_currency_code="JPY",
    )

    assert options[0].country_code == "JP"
    assert options[0].currency_code == "JPY"
    assert options[0].country_context is True
    assert options[1].country_context is False
    assert options[1].currency_code == "JPY"


@pytest.mark.django_db
def test_picker_exact_currency_code_keeps_currency_only_before_country_context(
    picker_reference_data,
):
    options = search_currency_options(query="JPY", historical_mode=False)

    assert [(option.country_code, option.currency_code) for option in options] == [
        ("", "JPY"),
        ("JP", "JPY"),
    ]


@pytest.mark.django_db
def test_historical_picker_exposes_archived_currency_and_date_valid_country_link(
    picker_reference_data,
):
    options = search_currency_options(
        query="FIM",
        historical_mode=True,
        selected_date=date(1998, 6, 15),
    )

    assert [(option.country_code, option.currency_code) for option in options] == [
        ("", "FIM"),
        ("FI", "FIM"),
    ]
    assert all(option.historical for option in options)


@pytest.mark.django_db
def test_picker_result_limit_is_hard_bounded(picker_reference_data):
    options = search_currency_options(query="", historical_mode=False, limit=1)

    assert len(options) == 1
