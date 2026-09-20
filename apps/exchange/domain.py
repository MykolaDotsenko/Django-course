from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_EVEN
from enum import StrEnum


class FxDomainError(ValueError):
    pass


class ProviderPolicyMode(StrEnum):
    BLEND = "blend"
    PINNED = "pinned"


class ObservationGranularity(StrEnum):
    DAILY = "daily"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class FxSourcePolicy:
    mode: ProviderPolicyMode = ProviderPolicyMode.BLEND
    provider_key: str | None = None
    include_attribution: bool = True

    def __post_init__(self) -> None:
        provider = self.provider_key.lower().strip() if self.provider_key else None
        if self.mode is ProviderPolicyMode.PINNED and not provider:
            raise FxDomainError("Pinned FX policy requires a provider key.")
        if self.mode is ProviderPolicyMode.BLEND and provider:
            raise FxDomainError("Blend FX policy cannot carry a pinned provider key.")
        object.__setattr__(self, "provider_key", provider)

    @property
    def cache_identity(self) -> str:
        provider = self.provider_key or "all"
        attribution = "attr" if self.include_attribution else "noattr"
        return f"{provider}:{attribution}"


DEFAULT_SOURCE_POLICY = FxSourcePolicy()


@dataclass(frozen=True)
class RateQuote:
    base_currency: str
    quote_currency: str
    rate: Decimal
    requested_date: date | None
    effective_date: date
    fetched_at: datetime
    provider_policy: FxSourcePolicy
    provider_keys: tuple[str, ...]
    historical: bool
    observation_granularity: ObservationGranularity = ObservationGranularity.DAILY

    def __post_init__(self) -> None:
        base = self.base_currency.upper().strip()
        quote = self.quote_currency.upper().strip()
        if len(base) != 3 or len(quote) != 3 or not base.isalpha() or not quote.isalpha():
            raise FxDomainError("FX quotes require three-letter alphabetic currency codes.")
        if not isinstance(self.rate, Decimal):
            raise FxDomainError("FX rate must be a Decimal.")
        if self.rate <= 0 or not self.rate.is_finite():
            raise FxDomainError("FX rate must be a finite positive Decimal.")
        if self.fetched_at.tzinfo is None:
            raise FxDomainError("FX fetched_at must be timezone-aware.")
        providers = tuple(
            sorted({key.lower().strip() for key in self.provider_keys if key.strip()})
        )
        if self.provider_policy.mode is ProviderPolicyMode.PINNED:
            if self.provider_policy.provider_key not in providers:
                raise FxDomainError("Pinned FX quote must attribute the pinned provider.")
        if self.requested_date and self.effective_date > self.requested_date:
            raise FxDomainError("Historical effective date cannot be after the requested date.")
        if self.historical != (self.requested_date is not None):
            raise FxDomainError("Historical flag must match requested-date semantics.")
        object.__setattr__(self, "base_currency", base)
        object.__setattr__(self, "quote_currency", quote)
        object.__setattr__(self, "provider_keys", providers)


@dataclass(frozen=True)
class ConversionResult:
    input_amount: Decimal
    output_amount: Decimal
    quote: RateQuote
    stale: bool


def convert_amount(amount: Decimal, quote: RateQuote, *, minor_units: int) -> Decimal:
    if not isinstance(amount, Decimal):
        raise FxDomainError("Amount must be a Decimal.")
    if not amount.is_finite():
        raise FxDomainError("Amount must be a finite Decimal.")
    if isinstance(minor_units, bool) or not isinstance(minor_units, int):
        raise FxDomainError("Minor units must be an integer.")
    if not 0 <= minor_units <= 6:
        raise FxDomainError("Minor units must be between 0 and 6.")
    quantum = Decimal(1).scaleb(-minor_units)
    try:
        return (amount * quote.rate).quantize(quantum, rounding=ROUND_HALF_EVEN)
    except InvalidOperation as exc:
        raise FxDomainError("Conversion cannot be represented at the requested precision.") from exc


def same_currency_quote(currency: str, *, fetched_at: datetime) -> RateQuote:
    code = currency.upper().strip()
    return RateQuote(
        base_currency=code,
        quote_currency=code,
        rate=Decimal("1"),
        requested_date=None,
        effective_date=fetched_at.date(),
        fetched_at=fetched_at,
        provider_policy=DEFAULT_SOURCE_POLICY,
        provider_keys=(),
        historical=False,
    )
