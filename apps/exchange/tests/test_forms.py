from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from apps.countries.models import Country, CountryCurrency, Currency
from apps.exchange.forms import CurrentConversionForm, parse_amount_text


@pytest.mark.parametrize(
    ("raw", "minor_units", "expected"),
    [
        ("12.50", 2, Decimal("12.50")),
        ("12,50", 2, Decimal("12.50")),
        ("0", 2, Decimal("0")),
        ("100.00", 0, Decimal("100.00")),
        ("12.500", 2, Decimal("12.500")),
        ("1.234", 3, Decimal("1.234")),
    ],
)
def test_amount_parser_accepts_unambiguous_decimal_input(raw, minor_units, expected):
    assert parse_amount_text(raw, minor_units=minor_units) == expected


@pytest.mark.parametrize("raw", ["-1", "100 euros", "1,234.56"])
def test_amount_parser_rejects_invalid_or_grouped_input(raw):
    with pytest.raises(ValidationError):
        parse_amount_text(raw, minor_units=2)


def test_amount_parser_rejects_ambiguous_three_digit_fraction_for_eur():
    with pytest.raises(ValidationError, match="ambiguous"):
        parse_amount_text("1.234", minor_units=2)


def test_amount_parser_rejects_excess_precision():
    with pytest.raises(ValidationError, match="at most 2 decimal places"):
        parse_amount_text("12.3456", minor_units=2)


@pytest.fixture
def reference_data(db):
    fi = Country.objects.create(iso2="FI", iso3="FIN", name="Finland")
    jp = Country.objects.create(iso2="JP", iso3="JPN", name="Japan")
    eur = Currency.objects.create(code="EUR", name="Euro", symbol="€", minor_units=2)
    jpy = Currency.objects.create(code="JPY", name="Japanese yen", symbol="¥", minor_units=0)
    CountryCurrency.objects.create(
        country=fi,
        currency=eur,
        is_primary=True,
        source="test",
    )
    CountryCurrency.objects.create(
        country=jp,
        currency=jpy,
        is_primary=True,
        source="test",
    )
    return fi, jp, eur, jpy


@pytest.mark.django_db
def test_form_rejects_country_currency_mismatch_before_provider(reference_data):
    form = CurrentConversionForm(
        {
            "amount": "100",
            "source_country": "FI",
            "source_currency": "JPY",
            "destination_country": "JP",
            "destination_currency": "JPY",
        }
    )

    assert not form.is_valid()
    assert "source_currency" in form.errors


@pytest.mark.django_db
def test_form_normalizes_decimal_comma_to_decimal(reference_data):
    form = CurrentConversionForm(
        {
            "amount": "12,50",
            "source_country": "FI",
            "source_currency": "EUR",
            "destination_country": "JP",
            "destination_currency": "JPY",
        }
    )

    assert form.is_valid(), form.errors
    assert form.cleaned_data["amount_decimal"] == Decimal("12.50")


def test_amount_parser_rejects_value_above_product_bound():
    with pytest.raises(ValidationError, match="1,000,000,000"):
        parse_amount_text("1000000000.01", minor_units=2)
