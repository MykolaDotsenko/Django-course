from datetime import UTC, date, datetime
from decimal import Decimal
from urllib.error import HTTPError, URLError
from unittest.mock import patch

import pytest

from apps.exchange.domain import DEFAULT_SOURCE_POLICY, FxSourcePolicy, ProviderPolicyMode
from apps.exchange.providers.frankfurter import (
    FrankfurterProvider,
    FxProviderInvalidPayload,
    FxProviderRateLimited,
    parse_rate_payload,
)


def test_frankfurter_v2_rate_normalizes_decimal_and_attribution():
    result = parse_rate_payload(
        {
            "date": "2026-09-18",
            "base": "EUR",
            "quote": "JPY",
            "rate": Decimal("174.50"),
            "providers": ["ECB", "BOJ"],
        },
        expected_base="EUR",
        expected_quote="JPY",
        requested_date=None,
        policy=DEFAULT_SOURCE_POLICY,
        fetched_at=datetime(2026, 9, 20, tzinfo=UTC),
    )

    assert result.rate == Decimal("174.50")
    assert result.provider_keys == ("boj", "ecb")
    assert result.effective_date == date(2026, 9, 18)


@pytest.mark.parametrize(
    "payload",
    [
        {"date": "2026-09-18", "base": "USD", "quote": "JPY", "rate": Decimal("174.5")},
        {"date": "2026-09-18", "base": "EUR", "quote": "JPY", "rate": Decimal("0")},
        {"date": "not-a-date", "base": "EUR", "quote": "JPY", "rate": Decimal("174.5")},
        {"date": "2026-09-18", "base": "EUR", "quote": "JPY", "rate": True},
    ],
)
def test_malformed_or_wrong_pair_payload_is_rejected(payload):
    with pytest.raises(FxProviderInvalidPayload):
        parse_rate_payload(
            payload,
            expected_base="EUR",
            expected_quote="JPY",
            requested_date=None,
            policy=DEFAULT_SOURCE_POLICY,
            fetched_at=datetime(2026, 9, 20, tzinfo=UTC),
        )


def test_pinned_quote_retains_pinned_provider_identity_without_expand_field():
    policy = FxSourcePolicy(mode=ProviderPolicyMode.PINNED, provider_key="ecb")
    result = parse_rate_payload(
        {"date": "2026-09-18", "base": "EUR", "quote": "JPY", "rate": Decimal("174.5")},
        expected_base="EUR",
        expected_quote="JPY",
        requested_date=None,
        policy=policy,
        fetched_at=datetime(2026, 9, 20, tzinfo=UTC),
    )
    assert result.provider_keys == ("ecb",)


class FakeResponse:
    def __init__(self, payload: bytes):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return self.payload


def test_transient_network_failure_retries_at_most_once():
    payload = (
        b'{"date":"2026-09-18","base":"EUR","quote":"JPY","rate":174.5,'
        b'"providers":["ECB"]}'
    )
    attempts = [URLError("temporary"), FakeResponse(payload)]

    def fake_urlopen(*args, **kwargs):
        return attempts.pop(0)

    provider = FrankfurterProvider(max_attempts=2)
    with patch("apps.exchange.providers.frankfurter.urlopen", side_effect=fake_urlopen) as mocked:
        result = provider.latest_quote("EUR", "JPY", DEFAULT_SOURCE_POLICY)

    assert mocked.call_count == 2
    assert result.rate == Decimal("174.5")


def test_rate_limit_is_not_retried():
    error = HTTPError(
        url="https://api.frankfurter.dev/v2/rate/EUR/JPY",
        code=429,
        msg="Too Many Requests",
        hdrs=None,
        fp=None,
    )
    provider = FrankfurterProvider(max_attempts=2)

    with patch("apps.exchange.providers.frankfurter.urlopen", side_effect=error) as mocked:
        with pytest.raises(FxProviderRateLimited):
            provider.latest_quote("EUR", "JPY", DEFAULT_SOURCE_POLICY)

    assert mocked.call_count == 1
