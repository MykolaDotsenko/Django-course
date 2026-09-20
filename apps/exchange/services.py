from __future__ import annotations

from datetime import UTC, date, datetime
from decimal import Decimal

from apps.exchange.cache import HistoricalQuoteGateway, LatestQuoteGateway
from apps.exchange.domain import (
    DEFAULT_SOURCE_POLICY,
    ConversionResult,
    FxSourcePolicy,
    HistoricalCurrencyMetadata,
    HistoricalDateError,
    convert_amount,
    normalize_currency_code,
    same_currency_quote,
    validate_historical_currency_metadata,
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


def quote_historical_conversion(
    *,
    amount: Decimal,
    base_currency: str,
    quote_currency: str,
    quote_minor_units: int,
    requested_date: date,
    gateway: HistoricalQuoteGateway,
    base_metadata: HistoricalCurrencyMetadata | None = None,
    quote_metadata: HistoricalCurrencyMetadata | None = None,
    policy: FxSourcePolicy = DEFAULT_SOURCE_POLICY,
    now: datetime | None = None,
) -> ConversionResult:
    current_time = now or datetime.now(UTC)
    if requested_date > current_time.date():
        raise HistoricalDateError("Historical date cannot be in the future.")

    if base_metadata is not None:
        validate_historical_currency_metadata(base_metadata, requested_date)
    if quote_metadata is not None:
        validate_historical_currency_metadata(quote_metadata, requested_date)

    base_code = normalize_currency_code(base_currency)
    quote_code = normalize_currency_code(quote_currency)
    if base_code == quote_code:
        quote = same_currency_quote(
            base_code,
            fetched_at=current_time,
            requested_date=requested_date,
        )
        return ConversionResult(
            input_amount=amount,
            output_amount=convert_amount(amount, quote, minor_units=quote_minor_units),
            quote=quote,
            stale=False,
        )

    quote = gateway.get(base_code, quote_code, requested_date, policy)
    return ConversionResult(
        input_amount=amount,
        output_amount=convert_amount(amount, quote, minor_units=quote_minor_units),
        quote=quote,
        stale=False,
    )
