from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.countries.models import Country, Currency
from apps.culture.models import (
    CulturalProfile,
    TypicalPrice,
    TypicalPriceCategory,
    TypicalPriceConfidence,
)
from apps.culture.presentation import build_destination_context_component
from apps.culture.services import (
    PRICE_CONTEXT_MAX_AGE,
    build_destination_context,
    calculate_purchase_equivalent,
)


@pytest.fixture
def japan_context(db):
    japan = Country.objects.create(iso2="JP", iso3="JPN", name="Japan")
    jpy = Currency.objects.create(code="JPY", name="Japanese yen", symbol="¥", minor_units=0)
    profile = CulturalProfile.objects.create(
        country=japan,
        summary="Current sourced payment context.",
        payment_customs="Cards are commonly accepted in many urban businesses.",
        cash_usage="Cash remains useful as a fallback.",
        tipping="Tipping is generally not practiced.",
        source_name="JNTO",
        source_url="https://example.org/payment",
        verified_at=timezone.now(),
        is_published=True,
    )
    price = TypicalPrice.objects.create(
        country=japan,
        city="Tokyo",
        category=TypicalPriceCategory.TRANSIT,
        label="Metro ticket",
        amount_low=Decimal("180"),
        amount_high=Decimal("330"),
        currency=jpy,
        source_name="Tokyo Metro",
        source_url="https://example.org/fare",
        observed_at=timezone.localdate(),
        verified_at=timezone.now(),
        confidence=TypicalPriceConfidence.HIGH,
        is_published=True,
    )
    return japan, jpy, profile, price


def test_purchase_equivalent_keeps_decimal_math_and_range_direction():
    value = calculate_purchase_equivalent(Decimal("17450"), Decimal("100"), Decimal("600"))
    assert value.minimum_count == Decimal("17450") / Decimal("600")
    assert value.maximum_count == Decimal("174.5")
    assert value.status == "range"


def test_purchase_equivalent_reports_below_one_without_division_guessing():
    value = calculate_purchase_equivalent(Decimal("50"), Decimal("100"), Decimal("600"))
    assert value.status == "below_one"


@pytest.mark.django_db
def test_published_profile_requires_https_provenance():
    japan = Country.objects.create(iso2="JP", iso3="JPN", name="Japan")
    profile = CulturalProfile(
        country=japan,
        payment_customs="Cards.",
        source_name="Source",
        source_url="http://example.org",
        verified_at=timezone.now(),
        is_published=True,
    )
    with pytest.raises(ValidationError, match="HTTPS"):
        profile.full_clean()


@pytest.mark.django_db
def test_typical_price_rejects_reversed_range():
    japan = Country.objects.create(iso2="JP", iso3="JPN", name="Japan")
    jpy = Currency.objects.create(code="JPY", name="Japanese yen")
    price = TypicalPrice(
        country=japan,
        category=TypicalPriceCategory.COFFEE,
        label="Coffee",
        amount_low=Decimal("600"),
        amount_high=Decimal("100"),
        currency=jpy,
        source_name="Source",
        source_url="https://example.org",
        observed_at=timezone.localdate(),
    )
    with pytest.raises(ValidationError, match="High price"):
        price.full_clean()


@pytest.mark.django_db
def test_destination_context_preserves_city_scope_and_provenance(japan_context):
    context = build_destination_context(
        country_code="JP",
        converted_amount=Decimal("17450"),
        quote_currency="JPY",
    )
    assert context is not None
    assert context.payment is not None
    assert context.payment.source_name == "JNTO"
    assert len(context.prices) == 1
    assert context.prices[0].scope_label == "Tokyo"
    assert context.prices[0].source_name == "Tokyo Metro"


@pytest.mark.django_db
def test_destination_context_suppresses_old_prices_but_keeps_payment(japan_context):
    _japan, _jpy, _profile, price = japan_context
    price.observed_at = timezone.localdate() - PRICE_CONTEXT_MAX_AGE - timedelta(days=1)
    price.save(update_fields=("observed_at",))
    context = build_destination_context(
        country_code="JP",
        converted_amount=Decimal("1000"),
        quote_currency="JPY",
    )
    assert context is not None
    assert context.payment is not None
    assert context.prices == ()


@pytest.mark.django_db
def test_destination_context_does_not_backdate_current_context(japan_context):
    context = build_destination_context(
        country_code="JP",
        converted_amount=Decimal("1000"),
        quote_currency="JPY",
        as_of=date(2026, 9, 21),
    )
    assert context is not None
    component = build_destination_context_component(context, historical=True)
    assert component["historical_notice"]
    assert "not backdated" in component["historical_notice"]


@pytest.mark.django_db
def test_currency_only_conversion_has_no_destination_context(japan_context):
    assert (
        build_destination_context(
            country_code="",
            converted_amount=Decimal("1000"),
            quote_currency="JPY",
        )
        is None
    )
