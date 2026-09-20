from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass

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
    if not base_url.startswith("https://"):
        raise FxConfigurationError("FRANKFURTER_BASE_URL must use HTTPS.")

    raw_timeout = values.get("FRANKFURTER_TIMEOUT_SECONDS", "3").strip()
    try:
        timeout = float(raw_timeout)
    except ValueError as exc:
        raise FxConfigurationError("FRANKFURTER_TIMEOUT_SECONDS must be numeric.") from exc
    if not 0 < timeout <= 10:
        raise FxConfigurationError("FRANKFURTER_TIMEOUT_SECONDS must be > 0 and <= 10.")

    return FxRuntimeConfig(base_url=base_url, timeout_seconds=timeout)
