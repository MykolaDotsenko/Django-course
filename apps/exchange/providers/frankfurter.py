from __future__ import annotations

import json
import socket
from datetime import UTC, date, datetime
from decimal import Decimal
from http.client import HTTPException
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from apps.exchange.domain import (
    FxDomainError,
    FxSourcePolicy,
    ObservationGranularity,
    ProviderPolicyMode,
    RateQuote,
    normalize_currency_code,
)
from apps.exchange.providers.base import (
    FxProviderAuthenticationError,
    FxProviderInvalidPayload,
    FxProviderRateLimited,
    FxProviderTimeout,
    FxProviderUnavailable,
    FxProviderUnsupportedPair,
)

DEFAULT_BASE_URL = "https://api.frankfurter.dev/v2"
MAX_RESPONSE_BYTES = 64 * 1024
RETRYABLE_HTTP_STATUSES = frozenset({408, 500, 502, 503, 504})


def _currency_code(value: Any) -> str:
    code = str(value or "").upper().strip()
    if len(code) != 3 or not code.isalpha():
        raise FxProviderInvalidPayload("Frankfurter returned an invalid currency code.")
    return code


def parse_rate_payload(
    payload: Any,
    *,
    expected_base: str,
    expected_quote: str,
    requested_date: date | None,
    policy: FxSourcePolicy,
    fetched_at: datetime,
) -> RateQuote:
    if not isinstance(payload, dict):
        raise FxProviderInvalidPayload("Frankfurter rate response must be an object.")

    base = _currency_code(payload.get("base"))
    quote = _currency_code(payload.get("quote"))
    if base != expected_base.upper() or quote != expected_quote.upper():
        raise FxProviderInvalidPayload("Frankfurter returned a different currency pair.")

    raw_rate = payload.get("rate")
    if isinstance(raw_rate, bool):
        raise FxProviderInvalidPayload("Frankfurter returned an invalid rate.")
    try:
        rate = raw_rate if isinstance(raw_rate, Decimal) else Decimal(str(raw_rate))
    except (ArithmeticError, ValueError) as exc:
        raise FxProviderInvalidPayload("Frankfurter returned a non-decimal rate.") from exc

    try:
        effective_date = date.fromisoformat(str(payload.get("date")))
    except ValueError as exc:
        raise FxProviderInvalidPayload("Frankfurter returned an invalid observation date.") from exc

    raw_providers = payload.get("providers")
    if raw_providers is None:
        raw_providers = []
        if policy.mode is ProviderPolicyMode.PINNED and policy.include_attribution:
            raise FxProviderInvalidPayload(
                "Frankfurter omitted attribution for a pinned-provider quote."
            )
    if not isinstance(raw_providers, list):
        raise FxProviderInvalidPayload("Frankfurter provider attribution must be an array.")
    provider_keys = tuple(str(key).lower().strip() for key in raw_providers if str(key).strip())
    if policy.mode is ProviderPolicyMode.PINNED and not provider_keys:
        provider_keys = (policy.provider_key or "",)

    try:
        return RateQuote(
            base_currency=base,
            quote_currency=quote,
            rate=rate,
            requested_date=requested_date,
            effective_date=effective_date,
            fetched_at=fetched_at,
            provider_policy=policy,
            provider_keys=provider_keys,
            historical=requested_date is not None,
            observation_granularity=ObservationGranularity.UNKNOWN,
        )
    except FxDomainError as exc:
        raise FxProviderInvalidPayload(str(exc)) from exc


class FrankfurterProvider:
    def __init__(
        self,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout_seconds: float = 3.0,
        max_attempts: int = 2,
    ):
        if timeout_seconds <= 0:
            raise ValueError("Frankfurter timeout must be positive.")
        if max_attempts not in {1, 2}:
            raise ValueError("Frankfurter max_attempts must be 1 or 2.")
        self.base_url = base_url.rstrip("/")
        self.timeout_seconds = timeout_seconds
        self.max_attempts = max_attempts

    def latest_quote(self, base: str, quote: str, policy: FxSourcePolicy) -> RateQuote:
        return self._fetch_quote(base, quote, requested_date=None, policy=policy)

    def historical_quote(
        self,
        base: str,
        quote: str,
        requested_date: date,
        policy: FxSourcePolicy,
    ) -> RateQuote:
        return self._fetch_quote(base, quote, requested_date=requested_date, policy=policy)

    def _fetch_quote(
        self,
        base: str,
        quote: str,
        *,
        requested_date: date | None,
        policy: FxSourcePolicy,
    ) -> RateQuote:
        try:
            base_code = normalize_currency_code(base)
            quote_code = normalize_currency_code(quote)
        except FxDomainError as exc:
            raise FxProviderUnsupportedPair("Invalid currency code for Frankfurter query.") from exc
        params: dict[str, str] = {}
        if requested_date is not None:
            params["date"] = requested_date.isoformat()
        if policy.mode is ProviderPolicyMode.PINNED:
            params["providers"] = policy.provider_key or ""
        if policy.include_attribution:
            params["expand"] = "providers"

        query = f"?{urlencode(params)}" if params else ""
        request = Request(
            f"{self.base_url}/rate/{base_code}/{quote_code}{query}",
            headers={"Accept": "application/json", "User-Agent": "cultural-currency-converter/0.1"},
        )
        raw: bytes | None = None
        last_transient_error: Exception | None = None
        for attempt in range(self.max_attempts):
            try:
                with urlopen(request, timeout=self.timeout_seconds) as response:
                    raw = response.read(MAX_RESPONSE_BYTES + 1)
                if len(raw) > MAX_RESPONSE_BYTES:
                    raise FxProviderInvalidPayload("Frankfurter response exceeded the size limit.")
                break
            except HTTPError as exc:
                if exc.code == 429:
                    raise FxProviderRateLimited("Frankfurter rate limit reached.") from exc
                if exc.code in {401, 403}:
                    raise FxProviderAuthenticationError(
                        "Frankfurter authentication or authorization failed."
                    ) from exc
                if exc.code in {400, 404, 422}:
                    raise FxProviderUnsupportedPair(
                        "Frankfurter does not support this rate query."
                    ) from exc
                if exc.code not in RETRYABLE_HTTP_STATUSES:
                    raise FxProviderUnavailable(f"Frankfurter returned HTTP {exc.code}.") from exc
                last_transient_error = exc
                if attempt + 1 == self.max_attempts:
                    raise FxProviderUnavailable(f"Frankfurter returned HTTP {exc.code}.") from exc
            except (TimeoutError, socket.timeout) as exc:
                last_transient_error = exc
                if attempt + 1 == self.max_attempts:
                    raise FxProviderTimeout("Frankfurter request timed out.") from exc
            except URLError as exc:
                if isinstance(exc.reason, (TimeoutError, socket.timeout)):
                    last_transient_error = exc
                    if attempt + 1 == self.max_attempts:
                        raise FxProviderTimeout("Frankfurter request timed out.") from exc
                    continue
                last_transient_error = exc
                if attempt + 1 == self.max_attempts:
                    raise FxProviderUnavailable("Frankfurter request failed.") from exc
            except HTTPException as exc:
                last_transient_error = exc
                if attempt + 1 == self.max_attempts:
                    raise FxProviderUnavailable("Frankfurter request failed.") from exc

        if raw is None:
            raise FxProviderUnavailable("Frankfurter request failed.") from last_transient_error

        fetched_at = datetime.now(UTC)
        try:
            payload = json.loads(raw, parse_float=Decimal, parse_int=Decimal)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise FxProviderInvalidPayload("Frankfurter returned malformed JSON.") from exc

        return parse_rate_payload(
            payload,
            expected_base=base_code,
            expected_quote=quote_code,
            requested_date=requested_date,
            policy=policy,
            fetched_at=fetched_at,
        )
