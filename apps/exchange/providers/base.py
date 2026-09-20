from __future__ import annotations

from datetime import date
from typing import Protocol

from apps.exchange.domain import FxSourcePolicy, RateQuote


class FxProvider(Protocol):
    def latest_quote(self, base: str, quote: str, policy: FxSourcePolicy) -> RateQuote: ...

    def historical_quote(
        self,
        base: str,
        quote: str,
        requested_date: date,
        policy: FxSourcePolicy,
    ) -> RateQuote: ...
