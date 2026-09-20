from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from urllib.parse import urlsplit

from apps.exchange.providers.frankfurter import DEFAULT_BASE_URL, FrankfurterProvider


class FxConfigurationError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class FxRuntimeConfig:
    base_url: str
    timeout_seconds: float

    def build_provider(self) -> FrankfurterProvider:
        return FrankfurterProvider(
            base_url=self.base_url,
            timeout_seconds=self.timeout_seconds,
        )


def load_fx_runtime_config(environ: Mapping[str, str] | None = None) -> FxRuntimeConfig:
    values = os.environ if environ is None else environ
    base_url = values.get("FRANKFURTER_BASE_URL", DEFAULT_BASE_URL).strip().rstrip("/")
    parsed = urlsplit(base_url)
    if parsed.scheme != "https" or not parsed.hostname:
        raise FxConfigurationError("FRANKFURTER_BASE_URL must be an absolute HTTPS URL.")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise FxConfigurationError(
            "FRANKFURTER_BASE_URL must not contain credentials, query parameters, or fragments."
        )

    raw_timeout = values.get("FRANKFURTER_TIMEOUT_SECONDS", "3").strip()
    try:
        timeout = float(raw_timeout)
    except ValueError as exc:
        raise FxConfigurationError("FRANKFURTER_TIMEOUT_SECONDS must be numeric.") from exc
    if not 0 < timeout <= 10:
        raise FxConfigurationError("FRANKFURTER_TIMEOUT_SECONDS must be > 0 and <= 10.")

    return FxRuntimeConfig(base_url=base_url, timeout_seconds=timeout)
