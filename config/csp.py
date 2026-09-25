from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum

from config.environment import ConfigurationError, RuntimeEnvironment


class CspMode(StrEnum):
    DISABLED = "disabled"
    REPORT_ONLY = "report-only"
    ENFORCE = "enforce"


@dataclass(frozen=True, slots=True)
class CspConfig:
    mode: CspMode

    @property
    def enabled(self) -> bool:
        return self.mode is not CspMode.DISABLED

    @property
    def header_name(self) -> str | None:
        if self.mode is CspMode.ENFORCE:
            return "Content-Security-Policy"
        if self.mode is CspMode.REPORT_ONLY:
            return "Content-Security-Policy-Report-Only"
        return None


def _optional(environ: Mapping[str, str], name: str) -> str | None:
    value = environ.get(name)
    if value is None:
        return None

    normalized = value.strip()
    return normalized or None


def load_csp_config(
    *,
    environ: Mapping[str, str],
    environment: RuntimeEnvironment,
) -> CspConfig:
    """Load the CSP rollout mode with explicit deployed-environment intent."""

    raw = _optional(environ, "DJANGO_CSP_MODE")
    if raw is None:
        if environment is RuntimeEnvironment.LOCAL:
            return CspConfig(CspMode.DISABLED)
        if environment is RuntimeEnvironment.TEST:
            return CspConfig(CspMode.ENFORCE)
        raise ConfigurationError(
            "DJANGO_CSP_MODE is required for preview and production "
            "(report-only/enforce)."
        )

    try:
        mode = CspMode(raw.lower())
    except ValueError as exc:
        raise ConfigurationError(
            "DJANGO_CSP_MODE must be disabled, report-only or enforce."
        ) from exc

    if (
        environment in {RuntimeEnvironment.PREVIEW, RuntimeEnvironment.PRODUCTION}
        and mode is CspMode.DISABLED
    ):
        raise ConfigurationError(
            "DJANGO_CSP_MODE cannot be disabled in preview or production."
        )

    return CspConfig(mode)
