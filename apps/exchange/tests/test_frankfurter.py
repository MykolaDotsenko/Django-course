from datetime import UTC, date, datetime
from decimal import Decimal
from unittest.mock import patch
from urllib.error import HTTPError, URLError

import pytest

from apps.exchange.domain import (
    DEFAULT_SOURCE_POLICY,
    FxSourcePolicy,
    ObservationGranularity,
    ProviderPolicyMode,
    RateSeriesGrouping,
)
from apps.exchange.providers.base import (
    FxProviderAuthenticationError,
    FxProviderInvalidPayload,
    FxProviderRateLimited,
    FxProviderTimeout,
    FxProviderUnavailable,
    FxProviderUnsupportedPair,
)
from apps.exchange.providers.frankfurter import (
    MAX_RESPONSE_BYTES,
    MAX_SERIES_RESPONSE_BYTES,
    FrankfurterProvider,
    parse_rate_payload,
    parse_series_payload,
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
    assert result.observation_granularity is ObservationGranularity.DAILY


@pytest.mark.parametrize(
    "payload",
    [
        {"date": "2026-09-18", "base": "USD", "quote": "JPY", "rate": Decimal("174.5")},
        {"date": "2026-09-18", "base": "EUR", "quote": "JPY", "rate": Decimal("0")},
        {"date": "2026-09-18", "base": "EUR", "quote": "JPY", "rate": Decimal("NaN")},
        {"date": "2026-09-18", "base": "EUR", "quote": "JPY", "rate": Decimal("Infinity")},
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


def test_pinned_quote_retains_identity_when_attribution_expansion_is_disabled():
    policy = FxSourcePolicy(
        mode=ProviderPolicyMode.PINNED,
        provider_key="ecb",
        include_attribution=False,
    )
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

    def read(self, size=-1):
        return self.payload if size < 0 else self.payload[:size]


def test_transient_network_failure_retries_at_most_once():
    payload = b'{"date":"2026-09-18","base":"EUR","quote":"JPY","rate":174.5,"providers":["ECB"]}'
    attempts = [URLError("temporary"), FakeResponse(payload)]

    def fake_urlopen(*args, **kwargs):
        result = attempts.pop(0)
        if isinstance(result, Exception):
            raise result
        return result

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


def test_invalid_currency_code_is_rejected_before_network_call():
    provider = FrankfurterProvider()

    with patch("apps.exchange.providers.frankfurter.urlopen") as mocked:
        with pytest.raises(FxProviderUnsupportedPair):
            provider.latest_quote("EUR/USD", "JPY", DEFAULT_SOURCE_POLICY)

    mocked.assert_not_called()


def test_blended_pegged_rate_may_omit_provider_attribution():
    result = parse_rate_payload(
        {"date": "2026-09-18", "base": "USD", "quote": "HKD", "rate": Decimal("7.8")},
        expected_base="USD",
        expected_quote="HKD",
        requested_date=None,
        policy=DEFAULT_SOURCE_POLICY,
        fetched_at=datetime(2026, 9, 20, tzinfo=UTC),
    )

    assert result.provider_keys == ()


def test_pinned_quote_missing_requested_attribution_is_rejected():
    policy = FxSourcePolicy(mode=ProviderPolicyMode.PINNED, provider_key="ecb")
    with pytest.raises(FxProviderInvalidPayload, match="pinned-provider"):
        parse_rate_payload(
            {"date": "2026-09-18", "base": "EUR", "quote": "JPY", "rate": Decimal("174.5")},
            expected_base="EUR",
            expected_quote="JPY",
            requested_date=None,
            policy=policy,
            fetched_at=datetime(2026, 9, 20, tzinfo=UTC),
        )


@pytest.mark.parametrize(
    ("status", "error_type"),
    [(401, FxProviderAuthenticationError), (403, FxProviderAuthenticationError)],
)
def test_authentication_failures_are_not_retried(status, error_type):
    error = HTTPError(
        url="https://api.frankfurter.dev/v2/rate/EUR/JPY",
        code=status,
        msg="auth failure",
        hdrs=None,
        fp=None,
    )
    provider = FrankfurterProvider(max_attempts=2)

    with patch("apps.exchange.providers.frankfurter.urlopen", side_effect=error) as mocked:
        with pytest.raises(error_type):
            provider.latest_quote("EUR", "JPY", DEFAULT_SOURCE_POLICY)

    assert mocked.call_count == 1


def test_non_retryable_unexpected_4xx_is_not_retried():
    error = HTTPError(
        url="https://api.frankfurter.dev/v2/rate/EUR/JPY",
        code=418,
        msg="client error",
        hdrs=None,
        fp=None,
    )
    provider = FrankfurterProvider(max_attempts=2)

    with patch("apps.exchange.providers.frankfurter.urlopen", side_effect=error) as mocked:
        with pytest.raises(FxProviderUnavailable):
            provider.latest_quote("EUR", "JPY", DEFAULT_SOURCE_POLICY)

    assert mocked.call_count == 1


def test_timeout_is_normalized_after_bounded_retry():
    provider = FrankfurterProvider(max_attempts=2)

    with patch(
        "apps.exchange.providers.frankfurter.urlopen",
        side_effect=TimeoutError("slow"),
    ) as mocked:
        with pytest.raises(FxProviderTimeout):
            provider.latest_quote("EUR", "JPY", DEFAULT_SOURCE_POLICY)

    assert mocked.call_count == 2


def test_oversized_single_rate_response_is_rejected_before_json_parsing():
    provider = FrankfurterProvider(max_attempts=1)
    response = FakeResponse(b"x" * (MAX_RESPONSE_BYTES + 1))

    with patch("apps.exchange.providers.frankfurter.urlopen", return_value=response):
        with pytest.raises(FxProviderInvalidPayload, match="size limit"):
            provider.latest_quote("EUR", "JPY", DEFAULT_SOURCE_POLICY)


@pytest.mark.parametrize(
    ("provider_key", "expected"),
    [
        ("hmrc", ObservationGranularity.MONTHLY),
        ("ust", ObservationGranularity.QUARTERLY),
        ("ecb", ObservationGranularity.DAILY),
    ],
)
def test_pinned_provider_frequency_is_normalized(provider_key, expected):
    policy = FxSourcePolicy(
        mode=ProviderPolicyMode.PINNED,
        provider_key=provider_key,
        include_attribution=False,
    )
    result = parse_rate_payload(
        {"date": "2026-09-18", "base": "EUR", "quote": "JPY", "rate": Decimal("174.5")},
        expected_base="EUR",
        expected_quote="JPY",
        requested_date=date(2026, 9, 20),
        policy=policy,
        fetched_at=datetime(2026, 9, 20, tzinfo=UTC),
    )

    assert result.observation_granularity is expected



def test_series_payload_sorts_observations_and_preserves_missing_dates():
    result = parse_series_payload(
        [
            {
                "date": "2026-01-05",
                "base": "EUR",
                "quote": "JPY",
                "rate": Decimal("181.2"),
                "providers": ["ECB"],
            },
            {
                "date": "2026-01-02",
                "base": "EUR",
                "quote": "JPY",
                "rate": Decimal("179.8"),
                "providers": ["ECB"],
            },
        ],
        expected_base="EUR",
        expected_quote="JPY",
        start_date=date(2026, 1, 1),
        end_date=date(2026, 1, 7),
        grouping=RateSeriesGrouping.DAILY,
        policy=DEFAULT_SOURCE_POLICY,
        fetched_at=datetime(2026, 1, 8, tzinfo=UTC),
    )

    assert [point.observation_date for point in result.points] == [
        date(2026, 1, 2),
        date(2026, 1, 5),
    ]
    assert [point.rate for point in result.points] == [
        Decimal("179.8"),
        Decimal("181.2"),
    ]


def test_series_payload_rejects_duplicate_observation_date():
    payload = [
        {
            "date": "2026-01-02",
            "base": "EUR",
            "quote": "JPY",
            "rate": Decimal("179.8"),
            "providers": ["ECB"],
        },
        {
            "date": "2026-01-02",
            "base": "EUR",
            "quote": "JPY",
            "rate": Decimal("180.0"),
            "providers": ["ECB"],
        },
    ]

    with pytest.raises(FxProviderInvalidPayload, match="duplicate"):
        parse_series_payload(
            payload,
            expected_base="EUR",
            expected_quote="JPY",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 7),
            grouping=RateSeriesGrouping.DAILY,
            policy=DEFAULT_SOURCE_POLICY,
            fetched_at=datetime(2026, 1, 8, tzinfo=UTC),
        )


@pytest.mark.parametrize(
    "payload",
    [
        [{"date": "2026-01-02", "base": "USD", "quote": "JPY", "rate": 180}],
        [{"date": "2025-12-31", "base": "EUR", "quote": "JPY", "rate": 180}],
        [{"date": "2026-01-02", "base": "EUR", "quote": "JPY", "rate": 0}],
        [{"date": "bad-date", "base": "EUR", "quote": "JPY", "rate": 180}],
    ],
)
def test_series_payload_rejects_wrong_identity_range_or_value(payload):
    with pytest.raises(FxProviderInvalidPayload):
        parse_series_payload(
            payload,
            expected_base="EUR",
            expected_quote="JPY",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 1, 7),
            grouping=RateSeriesGrouping.DAILY,
            policy=FxSourcePolicy(include_attribution=False),
            fetched_at=datetime(2026, 1, 8, tzinfo=UTC),
        )


def test_rate_series_builds_bounded_monthly_query():
    payload = (
        b'[{"date":"2025-01-31","base":"EUR","quote":"JPY",'
        b'"rate":161.2,"providers":["ECB"]}]'
    )
    provider = FrankfurterProvider(base_url="https://example.test/v2", max_attempts=1)

    with patch("apps.exchange.providers.frankfurter.urlopen", return_value=FakeResponse(payload)) as mocked:
        result = provider.rate_series(
            "EUR",
            "JPY",
            date(2025, 1, 1),
            date(2025, 12, 31),
            RateSeriesGrouping.MONTH,
            DEFAULT_SOURCE_POLICY,
        )

    request = mocked.call_args.args[0]
    assert request.full_url.startswith("https://example.test/v2/rates?")
    assert "from=2025-01-01" in request.full_url
    assert "to=2025-12-31" in request.full_url
    assert "base=EUR" in request.full_url
    assert "quotes=JPY" in request.full_url
    assert "group=month" in request.full_url
    assert "expand=providers" in request.full_url
    assert result.grouping is RateSeriesGrouping.MONTH


def test_daily_rate_series_omits_group_query_parameter():
    payload = (
        b'[{"date":"2026-01-02","base":"EUR","quote":"JPY",'
        b'"rate":179.8,"providers":["ECB"]}]'
    )
    provider = FrankfurterProvider(base_url="https://example.test/v2", max_attempts=1)

    with patch("apps.exchange.providers.frankfurter.urlopen", return_value=FakeResponse(payload)) as mocked:
        provider.rate_series(
            "EUR",
            "JPY",
            date(2026, 1, 1),
            date(2026, 1, 7),
            RateSeriesGrouping.DAILY,
            DEFAULT_SOURCE_POLICY,
        )

    request = mocked.call_args.args[0]
    assert "group=" not in request.full_url


def test_oversized_series_response_is_rejected_before_json_parsing():
    provider = FrankfurterProvider(max_attempts=1)
    response = FakeResponse(b"x" * (MAX_SERIES_RESPONSE_BYTES + 1))

    with patch("apps.exchange.providers.frankfurter.urlopen", return_value=response):
        with pytest.raises(FxProviderInvalidPayload, match="size limit"):
            provider.rate_series(
                "EUR",
                "JPY",
                date(2026, 1, 1),
                date(2026, 1, 7),
                RateSeriesGrouping.DAILY,
                DEFAULT_SOURCE_POLICY,
            )
