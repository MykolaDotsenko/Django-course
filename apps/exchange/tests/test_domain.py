from datetime import UTC, date, datetime
from decimal import Decimal

import pytest

from apps.exchange.domain import (
    DEFAULT_SOURCE_POLICY,
    FxDomainError,
    FxSourcePolicy,
    ProviderPolicyMode,
    RateQuote,
    convert_amount,
)


def quote(rate="174.505"):
    return RateQuote(
        base_currency="EUR",
        quote_currency="JPY",
        rate=Decimal(rate),
        requested_date=None,
        effective_date=date(2026, 9, 18),
        fetched_at=datetime(2026, 9, 20, 8, tzinfo=UTC),
        provider_policy=DEFAULT_SOURCE_POLICY,
        provider_keys=("ecb",),
        historical=False,
    )


def test_decimal_conversion_rounds_once_at_display_boundary():
    assert convert_amount(Decimal("100.125"), quote(), minor_units=0) == Decimal("17472")


def test_invalid_rate_cannot_enter_domain():
    with pytest.raises(FxDomainError):
        quote("0")


def test_pinned_policy_requires_provider():
    with pytest.raises(FxDomainError):
        FxSourcePolicy(mode=ProviderPolicyMode.PINNED)


def test_historical_quote_cannot_claim_future_effective_observation():
    with pytest.raises(FxDomainError):
        RateQuote(
            base_currency="EUR",
            quote_currency="JPY",
            rate=Decimal("174.5"),
            requested_date=date(2026, 9, 18),
            effective_date=date(2026, 9, 19),
            fetched_at=datetime(2026, 9, 20, tzinfo=UTC),
            provider_policy=DEFAULT_SOURCE_POLICY,
            provider_keys=("ecb",),
            historical=True,
        )
