from datetime import UTC, date, datetime
from decimal import Decimal

from apps.exchange.domain import (
    DEFAULT_SOURCE_POLICY,
    RateSeries,
    RateSeriesGrouping,
    RateSeriesPoint,
    RateSeriesResult,
)
from apps.exchange.series_presentation import build_rate_series_component


def build_rate_series_preview_context() -> dict[str, object]:
    series = RateSeries(
        base_currency="EUR",
        quote_currency="JPY",
        start_date=date(2025, 9, 18),
        end_date=date(2026, 9, 18),
        grouping=RateSeriesGrouping.DAILY,
        points=(
            RateSeriesPoint(date(2025, 9, 18), Decimal("171.2"), ("ecb",)),
            RateSeriesPoint(date(2025, 12, 18), Decimal("175.8"), ("ecb",)),
            RateSeriesPoint(date(2026, 3, 18), Decimal("178.4"), ("ecb",)),
            RateSeriesPoint(date(2026, 6, 18), Decimal("176.1"), ("ecb",)),
            RateSeriesPoint(date(2026, 9, 18), Decimal("174.5"), ("ecb",)),
        ),
        fetched_at=datetime(2026, 9, 20, 12, tzinfo=UTC),
        provider_policy=DEFAULT_SOURCE_POLICY,
    )
    return {
        "series_component": build_rate_series_component(
            RateSeriesResult(series=series, stale=False),
            selected_date=date(2026, 9, 18),
            requested_date=date(2026, 9, 20),
            period="1y",
        ),
        "series_error": None,
    }
