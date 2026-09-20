from __future__ import annotations

from datetime import date
from typing import Protocol

from apps.exchange.domain import FxSourcePolicy, RateQuote, RateSeries, RateSeriesGrouping


class FxProviderError(RuntimeError):
    pass


class FxProviderUnavailable(FxProviderError):
    pass


class FxProviderRateLimited(FxProviderUnavailable):
    pass


class FxProviderAuthenticationError(FxProviderUnavailable):
    pass


class FxProviderTimeout(FxProviderUnavailable):
    pass


class FxProviderUnsupportedPair(FxProviderError):
    pass


class FxProviderInvalidPayload(FxProviderError):
    pass


class FxProvider(Protocol):
    def latest_quote(self, base: str, quote: str, policy: FxSourcePolicy) -> RateQuote: ...

    def historical_quote(
        self,
        base: str,
        quote: str,
        requested_date: date,
        policy: FxSourcePolicy,
    ) -> RateQuote: ...

    def rate_series(
        self,
        base: str,
        quote: str,
        start_date: date,
        end_date: date,
        grouping: RateSeriesGrouping,
        policy: FxSourcePolicy,
    ) -> RateSeries: ...
