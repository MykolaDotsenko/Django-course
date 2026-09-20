from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from apps.exchange.cache import LatestQuoteGateway
from apps.exchange.domain import (
    DEFAULT_SOURCE_POLICY,
    ConversionResult,
    FxSourcePolicy,
    convert_amount,
    normalize_currency_code,
    same_currency_quote,
)


def quote_conversion(
    *,
    amount: Decimal,
    base_currency: str,
    quote_currency: str,
    quote_minor_units: int,
    gateway: LatestQuoteGateway,
    policy: FxSourcePolicy = DEFAULT_SOURCE_POLICY,
    now: datetime | None = None,
) -> ConversionResult:
    current_time = now or datetime.now(UTC)
    base_code = normalize_currency_code(base_currency)
    quote_code = normalize_currency_code(quote_currency)
    if base_code == quote_code:
        quote = same_currency_quote(base_code, fetched_at=current_time)
        return ConversionResult(
            input_amount=amount,
            output_amount=convert_amount(amount, quote, minor_units=quote_minor_units),
            quote=quote,
            stale=False,
        )

    quote, stale = gateway.get(base_code, quote_code, policy, now=current_time)
    return ConversionResult(
        input_amount=amount,
        output_amount=convert_amount(amount, quote, minor_units=quote_minor_units),
        quote=quote,
        stale=stale,
    )
