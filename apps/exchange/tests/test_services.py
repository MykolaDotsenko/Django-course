from datetime import UTC, datetime
from decimal import Decimal

import pytest

from apps.exchange.domain import FxDomainError
from apps.exchange.services import quote_conversion


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
