from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

import pytest
from django.core.cache import cache

from apps.exchange.cache import LatestQuoteGateway, latest_cache_key, serialize_quote
from apps.exchange.domain import (
    DEFAULT_SOURCE_POLICY,
    FxSourcePolicy,
    ProviderPolicyMode,
    RateQuote,
)
from apps.exchange.providers.frankfurter import FxProviderInvalidPayload, FxProviderUnavailable


NOW = datetime(2026, 9, 20, 12, tzinfo=UTC)


def make_quote(*, fetched_at=NOW, policy=DEFAULT_SOURCE_POLICY):
    return RateQuote(
        base_currency="EUR",
        quote_currency="JPY",
        rate=Decimal("174.5"),
        requested_date=None,
        effective_date=date(2026, 9, 18),
        fetched_at=fetched_at,
        provider_policy=policy,
        provider_keys=((policy.provider_key,) if policy.provider_key else ("ecb",)),
        historical=False,
    )


class FakeProvider:
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error
        self.calls = 0

    def latest_quote(self, base, quote, policy):
        self.calls += 1
        if self.error:
            raise self.error
        return self.result


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()
    yield
    cache.clear()


def test_fresh_cache_hit_skips_provider():
    cached = make_quote(fetched_at=NOW - timedelta(hours=1))
    cache.set(latest_cache_key("EUR", "JPY", DEFAULT_SOURCE_POLICY), serialize_quote(cached), 100)
    provider = FakeProvider(error=AssertionError("provider must not be called"))

    result, stale = LatestQuoteGateway(provider).get("EUR", "JPY", DEFAULT_SOURCE_POLICY, now=NOW)

    assert result == cached
    assert stale is False
    assert provider.calls == 0


def test_provider_failure_uses_only_bounded_semantically_matching_stale_quote():
    cached = make_quote(fetched_at=NOW - timedelta(days=2))
    cache.set(latest_cache_key("EUR", "JPY", DEFAULT_SOURCE_POLICY), serialize_quote(cached), 100)
    provider = FakeProvider(error=FxProviderUnavailable("down"))

    result, stale = LatestQuoteGateway(provider).get("EUR", "JPY", DEFAULT_SOURCE_POLICY, now=NOW)

    assert result == cached
    assert stale is True


def test_too_old_stale_quote_is_rejected():
    cached = make_quote(fetched_at=NOW - timedelta(days=8))
    cache.set(latest_cache_key("EUR", "JPY", DEFAULT_SOURCE_POLICY), serialize_quote(cached), 100)
    gateway = LatestQuoteGateway(FakeProvider(error=FxProviderUnavailable("down")))

    with pytest.raises(FxProviderUnavailable):
        gateway.get("EUR", "JPY", DEFAULT_SOURCE_POLICY, now=NOW)


def test_provider_policy_changes_cache_identity():
    pinned = FxSourcePolicy(mode=ProviderPolicyMode.PINNED, provider_key="ecb")
    assert latest_cache_key("EUR", "JPY", DEFAULT_SOURCE_POLICY) != latest_cache_key(
        "EUR", "JPY", pinned
    )


def test_malformed_provider_response_can_fall_back_to_matching_stale_quote():
    cached = make_quote(fetched_at=NOW - timedelta(days=2))
    cache.set(latest_cache_key("EUR", "JPY", DEFAULT_SOURCE_POLICY), serialize_quote(cached), 100)
    gateway = LatestQuoteGateway(FakeProvider(error=FxProviderInvalidPayload("bad payload")))

    result, stale = gateway.get("EUR", "JPY", DEFAULT_SOURCE_POLICY, now=NOW)

    assert result == cached
    assert stale is True


def test_wrong_pair_cache_key_is_never_reused_on_failure():
    cached = make_quote(fetched_at=NOW - timedelta(days=2))
    cache.set(latest_cache_key("EUR", "USD", DEFAULT_SOURCE_POLICY), serialize_quote(cached), 100)
    gateway = LatestQuoteGateway(FakeProvider(error=FxProviderUnavailable("down")))

    with pytest.raises(FxProviderUnavailable):
        gateway.get("EUR", "JPY", DEFAULT_SOURCE_POLICY, now=NOW)


def test_attribution_mode_changes_cache_identity():
    without_attribution = FxSourcePolicy(include_attribution=False)
    assert latest_cache_key("EUR", "JPY", DEFAULT_SOURCE_POLICY) != latest_cache_key(
        "EUR", "JPY", without_attribution
    )


def test_corrupted_cached_provider_keys_are_ignored():
    key = latest_cache_key("EUR", "JPY", DEFAULT_SOURCE_POLICY)
    payload = serialize_quote(make_quote())
    payload["provider_keys"] = "ecb"
    cache.set(key, payload, 100)
    provider_quote = make_quote(fetched_at=NOW)
    provider = FakeProvider(result=provider_quote)

    result, stale = LatestQuoteGateway(provider).get("EUR", "JPY", DEFAULT_SOURCE_POLICY, now=NOW)

    assert result == provider_quote
    assert stale is False
    assert provider.calls == 1


def test_provider_quote_identity_is_rechecked_before_caching():
    wrong_pair = RateQuote(
        base_currency="EUR",
        quote_currency="USD",
        rate=Decimal("1.1"),
        requested_date=None,
        effective_date=date(2026, 9, 18),
        fetched_at=NOW,
        provider_policy=DEFAULT_SOURCE_POLICY,
        provider_keys=("ecb",),
        historical=False,
    )
    gateway = LatestQuoteGateway(FakeProvider(result=wrong_pair))

    with pytest.raises(FxProviderInvalidPayload, match="different pair"):
        gateway.get("EUR", "JPY", DEFAULT_SOURCE_POLICY, now=NOW)

    assert cache.get(latest_cache_key("EUR", "JPY", DEFAULT_SOURCE_POLICY)) is None


def test_cache_read_failure_falls_through_to_provider(monkeypatch):
    provider_quote = make_quote()
    provider = FakeProvider(result=provider_quote)

    def fail_get(*args, **kwargs):
        raise RuntimeError("cache unavailable")

    monkeypatch.setattr(cache, "get", fail_get)

    result, stale = LatestQuoteGateway(provider).get("EUR", "JPY", DEFAULT_SOURCE_POLICY, now=NOW)

    assert result == provider_quote
    assert stale is False
    assert provider.calls == 1


def test_cache_write_failure_does_not_invalidate_provider_result(monkeypatch):
    provider_quote = make_quote()
    provider = FakeProvider(result=provider_quote)

    def fail_set(*args, **kwargs):
        raise RuntimeError("cache unavailable")

    monkeypatch.setattr(cache, "set", fail_set)

    result, stale = LatestQuoteGateway(provider).get(
        "EUR", "JPY", DEFAULT_SOURCE_POLICY, now=NOW
    )

    assert result == provider_quote
    assert stale is False


def test_invalid_provider_quote_identity_can_use_matching_stale_cache():
    cached = make_quote(fetched_at=NOW - timedelta(days=2))
    cache.set(latest_cache_key("EUR", "JPY", DEFAULT_SOURCE_POLICY), serialize_quote(cached), 100)
    wrong_pair = RateQuote(
        base_currency="EUR",
        quote_currency="USD",
        rate=Decimal("1.1"),
        requested_date=None,
        effective_date=date(2026, 9, 18),
        fetched_at=NOW,
        provider_policy=DEFAULT_SOURCE_POLICY,
        provider_keys=("ecb",),
        historical=False,
    )

    result, stale = LatestQuoteGateway(FakeProvider(result=wrong_pair)).get(
        "EUR", "JPY", DEFAULT_SOURCE_POLICY, now=NOW
    )

    assert result == cached
    assert stale is True
