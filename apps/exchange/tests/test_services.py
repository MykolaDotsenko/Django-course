from datetime import UTC, date, datetime
from decimal import Decimal

import pytest

from apps.exchange.domain import DEFAULT_SOURCE_POLICY, FxDomainError, HistoricalDateError, RateQuote
from apps.exchange.services import quote_conversion, quote_historical_conversion


class ExplodingGateway:
    def get(self, *args, **kwargs):
        raise AssertionError("same-currency conversion must not call the provider gateway")


def test_same_currency_fast_path_uses_exact_one_without_provider():
    result = quote_conversion(
        amount=Decimal("12.345"),
        base_currency="EUR",
        quote_currency="EUR",
        quote_minor_units=2,
        gateway=ExplodingGateway(),
        now=datetime(2026, 9, 20, tzinfo=UTC),
    )

    assert result.quote.rate == Decimal("1")
    assert result.output_amount == Decimal("12.34")
    assert result.stale is False


@pytest.mark.parametrize("base_currency", ["EU", "EUR/USD", "€UR", "ΕUR"])
def test_invalid_currency_syntax_is_rejected_before_gateway(base_currency):
    with pytest.raises(FxDomainError):
        quote_conversion(
            amount=Decimal("10"),
            base_currency=base_currency,
            quote_currency="JPY",
            quote_minor_units=0,
            gateway=ExplodingGateway(),
            now=datetime(2026, 9, 20, tzinfo=UTC),
        )


class HistoricalExplodingGateway:
    def get(self, *args, **kwargs):
        raise AssertionError("historical same-currency conversion must not call the provider gateway")


class HistoricalGateway:
    def __init__(self, quote):
        self.quote = quote
        self.calls = []

    def get(self, base, quote, requested_date, policy):
        self.calls.append((base, quote, requested_date, policy))
        return self.quote


def test_historical_same_currency_preserves_requested_and_effective_date_without_provider():
    requested = date(1998, 6, 15)
    result = quote_historical_conversion(
        amount=Decimal("12.345"),
        base_currency="FIM",
        quote_currency="FIM",
        quote_minor_units=2,
        requested_date=requested,
        gateway=HistoricalExplodingGateway(),
        now=datetime(2026, 9, 20, tzinfo=UTC),
    )

    assert result.quote.rate == Decimal("1")
    assert result.quote.historical is True
    assert result.quote.requested_date == requested
    assert result.quote.effective_date == requested
    assert result.output_amount == Decimal("12.34")


def test_historical_future_date_is_rejected_before_gateway():
    with pytest.raises(HistoricalDateError):
        quote_historical_conversion(
            amount=Decimal("10"),
            base_currency="EUR",
            quote_currency="JPY",
            quote_minor_units=0,
            requested_date=date(2026, 9, 21),
            gateway=HistoricalExplodingGateway(),
            now=datetime(2026, 9, 20, tzinfo=UTC),
        )


def test_historical_conversion_uses_gateway_quote():
    requested = date(2026, 9, 18)
    quote = RateQuote(
        base_currency="EUR",
        quote_currency="JPY",
        rate=Decimal("174.5"),
        requested_date=requested,
        effective_date=requested,
        fetched_at=datetime(2026, 9, 20, tzinfo=UTC),
        provider_policy=DEFAULT_SOURCE_POLICY,
        provider_keys=("ecb",),
        historical=True,
    )
    gateway = HistoricalGateway(quote)

    result = quote_historical_conversion(
        amount=Decimal("10"),
        base_currency="EUR",
        quote_currency="JPY",
        quote_minor_units=0,
        requested_date=requested,
        gateway=gateway,
        now=datetime(2026, 9, 20, tzinfo=UTC),
    )

    assert result.output_amount == Decimal("1745")
    assert gateway.calls == [("EUR", "JPY", requested, DEFAULT_SOURCE_POLICY)]
