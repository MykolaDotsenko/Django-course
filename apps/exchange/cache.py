from __future__ import annotations

import logging
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from enum import StrEnum
from typing import Any

from django.core.cache import cache

from apps.exchange.domain import (
    FxSourcePolicy,
    ObservationGranularity,
    ProviderPolicyMode,
    RateQuote,
)
from apps.exchange.providers.base import FxProvider
from apps.exchange.providers.frankfurter import FxProviderInvalidPayload, FxProviderUnavailable

logger = logging.getLogger(__name__)
CACHE_VERSION = "v1"


class QuoteFreshness(StrEnum):
    FRESH = "fresh"
    STALE = "stale"
    TOO_OLD = "too_old"


def latest_cache_key(base: str, quote: str, policy: FxSourcePolicy) -> str:
    return (
        f"fx:{CACHE_VERSION}:latest:{policy.mode.value}:{policy.cache_identity}:"
        f"{base.upper()}:{quote.upper()}"
    )


def historical_cache_key(
    base: str,
    quote: str,
    effective_date: date,
    policy: FxSourcePolicy,
) -> str:
    return (
        f"fx:{CACHE_VERSION}:historical:{policy.mode.value}:{policy.cache_identity}:"
        f"{base.upper()}:{quote.upper()}:{effective_date.isoformat()}"
    )


def serialize_quote(quote: RateQuote) -> dict[str, Any]:
    return {
        "base_currency": quote.base_currency,
        "quote_currency": quote.quote_currency,
        "rate": str(quote.rate),
        "requested_date": quote.requested_date.isoformat() if quote.requested_date else None,
        "effective_date": quote.effective_date.isoformat(),
        "fetched_at": quote.fetched_at.isoformat(),
        "provider_policy": {
            "mode": quote.provider_policy.mode.value,
            "provider_key": quote.provider_policy.provider_key,
            "include_attribution": quote.provider_policy.include_attribution,
        },
        "provider_keys": list(quote.provider_keys),
        "historical": quote.historical,
        "observation_granularity": quote.observation_granularity.value,
    }


def deserialize_quote(value: Any) -> RateQuote | None:
    if not isinstance(value, dict):
        return None
    try:
        raw_policy = value["provider_policy"]
        raw_provider_keys = value["provider_keys"]
        raw_historical = value["historical"]
        if not isinstance(raw_policy, dict):
            return None
        if not isinstance(raw_provider_keys, (list, tuple)) or not all(
            isinstance(key, str) for key in raw_provider_keys
        ):
            return None
        if not isinstance(raw_historical, bool):
            return None
        policy = FxSourcePolicy(
            mode=ProviderPolicyMode(raw_policy["mode"]),
            provider_key=raw_policy.get("provider_key"),
            include_attribution=bool(raw_policy.get("include_attribution", True)),
        )
        return RateQuote(
            base_currency=value["base_currency"],
            quote_currency=value["quote_currency"],
            rate=Decimal(value["rate"]),
            requested_date=(
                date.fromisoformat(value["requested_date"]) if value.get("requested_date") else None
            ),
            effective_date=date.fromisoformat(value["effective_date"]),
            fetched_at=datetime.fromisoformat(value["fetched_at"]),
            provider_policy=policy,
            provider_keys=tuple(raw_provider_keys),
            historical=raw_historical,
            observation_granularity=ObservationGranularity(value["observation_granularity"]),
        )
    except (KeyError, TypeError, ValueError, ArithmeticError):
        return None


def classify_quote_freshness(
    quote: RateQuote,
    *,
    now: datetime,
    fresh_for: timedelta,
    stale_for: timedelta,
) -> QuoteFreshness:
    age = now.astimezone(UTC) - quote.fetched_at.astimezone(UTC)
    if age <= fresh_for:
        return QuoteFreshness.FRESH
    if age <= stale_for:
        return QuoteFreshness.STALE
    return QuoteFreshness.TOO_OLD


class LatestQuoteGateway:
    def __init__(
        self,
        provider: FxProvider,
        *,
        fresh_for: timedelta = timedelta(hours=6),
        stale_for: timedelta = timedelta(days=7),
        physical_ttl_seconds: int = 8 * 24 * 60 * 60,
    ):
        if fresh_for <= timedelta(0) or stale_for <= fresh_for:
            raise ValueError("FX freshness windows must be positive and ordered.")
        self.provider = provider
        self.fresh_for = fresh_for
        self.stale_for = stale_for
        self.physical_ttl_seconds = physical_ttl_seconds

    def get(
        self, base: str, quote: str, policy: FxSourcePolicy, *, now: datetime
    ) -> tuple[RateQuote, bool]:
        key = latest_cache_key(base, quote, policy)
        cached = self._cache_get(key)
        if (
            cached
            and classify_quote_freshness(
                cached, now=now, fresh_for=self.fresh_for, stale_for=self.stale_for
            )
            is QuoteFreshness.FRESH
        ):
            return cached, False

        try:
            fresh = self.provider.latest_quote(base, quote, policy)
        except (FxProviderUnavailable, FxProviderInvalidPayload):
            if (
                cached
                and classify_quote_freshness(
                    cached, now=now, fresh_for=self.fresh_for, stale_for=self.stale_for
                )
                is QuoteFreshness.STALE
            ):
                return cached, True
            raise

        self._assert_quote_identity(fresh, base=base, quote=quote, policy=policy)
        self._cache_set(key, fresh)
        return fresh, False

    @staticmethod
    def _assert_quote_identity(
        quote_value: RateQuote,
        *,
        base: str,
        quote: str,
        policy: FxSourcePolicy,
    ) -> None:
        if quote_value.base_currency != base.upper() or quote_value.quote_currency != quote.upper():
            raise FxProviderInvalidPayload("Provider returned a quote for a different pair.")
        if quote_value.provider_policy != policy:
            raise FxProviderInvalidPayload(
                "Provider returned a quote under a different source policy."
            )
        if quote_value.historical or quote_value.requested_date is not None:
            raise FxProviderInvalidPayload("Latest quote gateway received historical semantics.")

    def _cache_get(self, key: str) -> RateQuote | None:
        try:
            return deserialize_quote(cache.get(key))
        except Exception:
            logger.warning("FX cache read failed", extra={"cache_key": key}, exc_info=True)
            return None

    def _cache_set(self, key: str, quote: RateQuote) -> None:
        try:
            cache.set(key, serialize_quote(quote), timeout=self.physical_ttl_seconds)
        except Exception:
            logger.warning("FX cache write failed", extra={"cache_key": key}, exc_info=True)
