from datetime import UTC, date, datetime
from decimal import Decimal

import pytest

from apps.exchange.domain import DEFAULT_SOURCE_POLICY, FxSourcePolicy, ProviderPolicyMode
from apps.exchange.providers.frankfurter import FxProviderInvalidPayload, parse_rate_payload


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
