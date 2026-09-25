from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import parse_qsl, urlparse

from config.environment import ConfigurationError, RuntimeEnvironment

_REDIS_BACKEND = "django.core.cache.backends.redis.RedisCache"
_LOCMEM_BACKEND = "django.core.cache.backends.locmem.LocMemCache"
_RESERVED_CACHE_QUERY_OPTIONS = frozenset(
    {
        "socket_timeout",
        "socket_connect_timeout",
        "retry_on_timeout",
        "ssl_cert_reqs",
        "ssl_check_hostname",
    }
)


@dataclass(frozen=True, slots=True)
class CacheConfig:
    """Normalized cache settings independent from Django's global settings."""

    backend: str
    environment: RuntimeEnvironment
    location: str = field(repr=False)
    shared: bool = False

    def as_django_settings(self) -> dict[str, Any]:
        settings: dict[str, Any] = {
            "BACKEND": self.backend,
            "LOCATION": self.location,
            "KEY_PREFIX": f"cultural-currency:{self.environment.value}",
        }

        if self.shared:
            settings["OPTIONS"] = {
                "socket_connect_timeout": 1.0,
                "socket_timeout": 1.0,
            }

        return settings


def _optional(environ: Mapping[str, str], name: str) -> str | None:
    value = environ.get(name)
    if value is None:
        return None

    value = value.strip()
    return value or None


def _validate_redis_url(cache_url: str) -> None:
    parsed = urlparse(cache_url)

    if parsed.scheme not in {"redis", "rediss"}:
        raise ConfigurationError("CACHE_URL must use the redis:// or rediss:// scheme.")

    if parsed.fragment:
        raise ConfigurationError("CACHE_URL must not contain a URL fragment.")

    try:
        hostname = parsed.hostname
        port = parsed.port
    except ValueError as exc:
        raise ConfigurationError("CACHE_URL contains an invalid Redis host or port.") from exc

    if not hostname:
        raise ConfigurationError("CACHE_URL must include a Redis host.")
    if port == 0:
        raise ConfigurationError("CACHE_URL contains an invalid Redis port.")

    if parsed.path not in {"", "/"}:
        if not parsed.path.startswith("/") or "/" in parsed.path[1:]:
            raise ConfigurationError("CACHE_URL may contain at most one Redis database number.")
        database_path = parsed.path[1:]
        if not database_path.isascii() or not database_path.isdecimal():
            raise ConfigurationError("CACHE_URL Redis database must be a non-negative integer.")

    try:
        query_options = parse_qsl(parsed.query, keep_blank_values=False, strict_parsing=True)
    except ValueError as exc:
        raise ConfigurationError("CACHE_URL contains invalid query options.") from exc

    for key, _value in query_options:
        if key in _RESERVED_CACHE_QUERY_OPTIONS:
            raise ConfigurationError(
                "CACHE_URL must not override cache timeout, retry, or TLS verification policy."
            )


def load_cache_config(
    *,
    environ: Mapping[str, str],
    environment: RuntimeEnvironment,
) -> CacheConfig:
    """Load a local cache by default and require a shared cache when deployed."""

    cache_url = _optional(environ, "CACHE_URL")

    if cache_url is not None:
        _validate_redis_url(cache_url)
        return CacheConfig(
            backend=_REDIS_BACKEND,
            environment=environment,
            location=cache_url,
            shared=True,
        )

    if environment in {RuntimeEnvironment.PREVIEW, RuntimeEnvironment.PRODUCTION}:
        raise ConfigurationError("CACHE_URL is required for preview and production.")

    return CacheConfig(
        backend=_LOCMEM_BACKEND,
        environment=environment,
        location=f"cultural-currency-{environment.value}",
    )
