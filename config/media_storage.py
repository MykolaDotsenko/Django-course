from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from config.environment import ConfigurationError, RuntimeEnvironment

_FILESYSTEM_BACKEND = "django.core.files.storage.FileSystemStorage"
_S3_BACKEND = "storages.backends.s3.S3Storage"
_STATICFILES_BACKEND = "django.contrib.staticfiles.storage.StaticFilesStorage"
_IMMUTABLE_CACHE_CONTROL = "public, max-age=31536000, immutable"


class MediaStorageMode(StrEnum):
    FILESYSTEM = "filesystem"
    S3 = "s3"


@dataclass(frozen=True, slots=True)
class MediaStorageConfig:
    mode: MediaStorageMode
    environment: RuntimeEnvironment
    bucket_name: str = ""
    region_name: str = ""
    endpoint_url: str = ""
    custom_domain: str = ""

    @property
    def is_filesystem(self) -> bool:
        return self.mode is MediaStorageMode.FILESYSTEM

    @property
    def media_url(self) -> str:
        if self.custom_domain:
            return f"https://{self.custom_domain}/media/"
        return "/media/"

    def as_django_storages(self, *, base_dir: Path) -> dict[str, dict[str, Any]]:
        if self.mode is MediaStorageMode.FILESYSTEM:
            default_storage: dict[str, Any] = {
                "BACKEND": _FILESYSTEM_BACKEND,
                "OPTIONS": {
                    "location": base_dir / "media",
                    "base_url": "/media/",
                },
            }
        else:
            options: dict[str, Any] = {
                "bucket_name": self.bucket_name,
                "region_name": self.region_name,
                "location": "media",
                "default_acl": None,
                "querystring_auth": False,
                "file_overwrite": True,
                "object_parameters": {
                    "CacheControl": _IMMUTABLE_CACHE_CONTROL,
                },
                "use_ssl": True,
                "verify": True,
            }
            if self.endpoint_url:
                options["endpoint_url"] = self.endpoint_url
            if self.custom_domain:
                options["custom_domain"] = self.custom_domain
                options["url_protocol"] = "https:"

            default_storage = {
                "BACKEND": _S3_BACKEND,
                "OPTIONS": options,
            }

        return {
            "default": default_storage,
            "staticfiles": {
                "BACKEND": _STATICFILES_BACKEND,
            },
        }


def _optional(environ: Mapping[str, str], name: str) -> str | None:
    value = environ.get(name)
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


def _parse_mode(
    environ: Mapping[str, str],
    environment: RuntimeEnvironment,
) -> MediaStorageMode:
    raw = _optional(environ, "MEDIA_STORAGE_MODE")
    if raw is None:
        if environment in {RuntimeEnvironment.LOCAL, RuntimeEnvironment.TEST}:
            return MediaStorageMode.FILESYSTEM
        raise ConfigurationError(
            "MEDIA_STORAGE_MODE is required for preview and production (filesystem/s3)."
        )

    try:
        mode = MediaStorageMode(raw.lower())
    except ValueError as exc:
        raise ConfigurationError("MEDIA_STORAGE_MODE must be filesystem or s3.") from exc

    if environment is RuntimeEnvironment.PRODUCTION and mode is not MediaStorageMode.S3:
        raise ConfigurationError("Production media storage must use the shared s3 backend.")
    return mode


def _validate_bucket(value: str | None) -> str:
    if not value:
        raise ConfigurationError("MEDIA_S3_BUCKET is required when MEDIA_STORAGE_MODE=s3.")
    if (
        len(value) > 255
        or any(character.isspace() for character in value)
        or "://" in value
        or "/" in value
        or "@" in value
    ):
        raise ConfigurationError("MEDIA_S3_BUCKET must be a plain bucket name.")
    return value


def _validate_region(value: str | None) -> str:
    if not value:
        raise ConfigurationError("MEDIA_S3_REGION is required when MEDIA_STORAGE_MODE=s3.")
    if len(value) > 100 or any(character.isspace() for character in value) or "/" in value:
        raise ConfigurationError("MEDIA_S3_REGION must be a plain region identifier.")
    return value


def _validate_endpoint(
    value: str | None,
    *,
    environment: RuntimeEnvironment,
) -> str:
    if not value:
        return ""

    parsed = urlsplit(value)
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.hostname
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
        or parsed.path not in {"", "/"}
    ):
        raise ConfigurationError(
            "MEDIA_S3_ENDPOINT_URL must be a credential-free HTTP(S) origin without a path."
        )
    if environment in {RuntimeEnvironment.PREVIEW, RuntimeEnvironment.PRODUCTION}:
        if parsed.scheme != "https":
            raise ConfigurationError(
                "MEDIA_S3_ENDPOINT_URL must use HTTPS in preview and production."
            )
    return value.rstrip("/")


def _validate_custom_domain(value: str | None) -> str:
    if not value:
        return ""
    if (
        len(value) > 253
        or "://" in value
        or "/" in value
        or "?" in value
        or "#" in value
        or "@" in value
        or any(character.isspace() for character in value)
    ):
        raise ConfigurationError(
            "MEDIA_CDN_DOMAIN must be a host name without scheme, path or credentials."
        )

    parsed = urlsplit(f"https://{value}")
    if not parsed.hostname or parsed.port is not None:
        raise ConfigurationError("MEDIA_CDN_DOMAIN must be a plain host name.")
    return value.lower()


def load_media_storage_config(
    *,
    environ: Mapping[str, str],
    environment: RuntimeEnvironment,
) -> MediaStorageConfig:
    mode = _parse_mode(environ, environment)
    if mode is MediaStorageMode.FILESYSTEM:
        return MediaStorageConfig(mode=mode, environment=environment)

    return MediaStorageConfig(
        mode=mode,
        environment=environment,
        bucket_name=_validate_bucket(_optional(environ, "MEDIA_S3_BUCKET")),
        region_name=_validate_region(_optional(environ, "MEDIA_S3_REGION")),
        endpoint_url=_validate_endpoint(
            _optional(environ, "MEDIA_S3_ENDPOINT_URL"),
            environment=environment,
        ),
        custom_domain=_validate_custom_domain(_optional(environ, "MEDIA_CDN_DOMAIN")),
    )
