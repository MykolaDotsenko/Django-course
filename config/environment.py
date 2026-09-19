from __future__ import annotations

import os
import secrets
from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum


class ConfigurationError(RuntimeError):
    """Raised when runtime configuration is missing or unsafe."""


class RuntimeEnvironment(StrEnum):
    LOCAL = "local"
    TEST = "test"
    PREVIEW = "preview"
    PRODUCTION = "production"


@dataclass(frozen=True, slots=True)
class RuntimeConfig:
    environment: RuntimeEnvironment
    secret_key: str
    debug: bool
    allowed_hosts: tuple[str, ...]

    @property
    def is_production(self) -> bool:
        return self.environment is RuntimeEnvironment.PRODUCTION


_TRUE_VALUES = frozenset({"1", "true", "yes", "on"})
_FALSE_VALUES = frozenset({"0", "false", "no", "off"})

_LOCAL_HOSTS = ("localhost", "127.0.0.1", "[::1]")
_TEST_HOSTS = ("testserver", "localhost", "127.0.0.1")
_TEST_SECRET_KEY = "test-only-secret-key-not-for-production-use-0123456789abcdef"


def _optional(environ: Mapping[str, str], name: str) -> str | None:
    value = environ.get(name)
    if value is None:
        return None

    value = value.strip()
    return value or None


def _parse_environment(environ: Mapping[str, str]) -> RuntimeEnvironment:
    raw = _optional(environ, "APP_ENV") or RuntimeEnvironment.LOCAL.value

    try:
        return RuntimeEnvironment(raw.lower())
    except ValueError as exc:
        allowed = ", ".join(environment.value for environment in RuntimeEnvironment)
        raise ConfigurationError(f"APP_ENV must be one of: {allowed}.") from exc


def _parse_bool(
    environ: Mapping[str, str],
    name: str,
    *,
    default: bool,
) -> bool:
    raw = _optional(environ, name)
    if raw is None:
        return default

    normalized = raw.lower()
    if normalized in _TRUE_VALUES:
        return True
    if normalized in _FALSE_VALUES:
        return False

    raise ConfigurationError(
        f"{name} must be a boolean value (true/false, yes/no, on/off, 1/0)."
    )


def _parse_allowed_hosts(
    environ: Mapping[str, str],
    environment: RuntimeEnvironment,
) -> tuple[str, ...]:
    raw = _optional(environ, "DJANGO_ALLOWED_HOSTS")

    if raw is None:
        if environment is RuntimeEnvironment.LOCAL:
            return _LOCAL_HOSTS
        if environment is RuntimeEnvironment.TEST:
            return _TEST_HOSTS
        raise ConfigurationError(
            "DJANGO_ALLOWED_HOSTS is required for preview and production."
        )

    hosts = tuple(host.strip() for host in raw.split(",") if host.strip())
    if not hosts:
        raise ConfigurationError("DJANGO_ALLOWED_HOSTS must contain at least one host.")

    for host in hosts:
        if "://" in host or "/" in host:
            raise ConfigurationError(
                "DJANGO_ALLOWED_HOSTS entries must be host names without schemes or paths."
            )

    if environment in {
        RuntimeEnvironment.PREVIEW,
        RuntimeEnvironment.PRODUCTION,
    } and "*" in hosts:
        raise ConfigurationError(
            "Wildcard DJANGO_ALLOWED_HOSTS is not allowed in preview or production."
        )

    return hosts


def _load_secret_key(
    environ: Mapping[str, str],
    environment: RuntimeEnvironment,
) -> str:
    configured = _optional(environ, "DJANGO_SECRET_KEY")
    if configured is not None:
        if environment in {
            RuntimeEnvironment.PREVIEW,
            RuntimeEnvironment.PRODUCTION,
        } and len(configured) < 50:
            raise ConfigurationError(
                "DJANGO_SECRET_KEY must be at least 50 characters in preview or production."
            )
        return configured

    if environment is RuntimeEnvironment.TEST:
        return _TEST_SECRET_KEY

    if environment is RuntimeEnvironment.LOCAL:
        # Local development requires no committed secret. Set DJANGO_SECRET_KEY
        # explicitly when stable sessions across process restarts are useful.
        return secrets.token_urlsafe(48)

    raise ConfigurationError(
        "DJANGO_SECRET_KEY is required for preview and production."
    )


def load_runtime_config(
    environ: Mapping[str, str] | None = None,
) -> RuntimeConfig:
    """Load and validate security-sensitive Django runtime configuration."""

    values = os.environ if environ is None else environ
    environment = _parse_environment(values)
    debug = _parse_bool(
        values,
        "DJANGO_DEBUG",
        default=environment is RuntimeEnvironment.LOCAL,
    )

    if environment in {
        RuntimeEnvironment.PREVIEW,
        RuntimeEnvironment.PRODUCTION,
    } and debug:
        raise ConfigurationError(
            "DJANGO_DEBUG must be false in preview and production."
        )

    return RuntimeConfig(
        environment=environment,
        secret_key=_load_secret_key(values, environment),
        debug=debug,
        allowed_hosts=_parse_allowed_hosts(values, environment),
    )
