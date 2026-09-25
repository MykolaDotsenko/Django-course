from __future__ import annotations

import pytest
from storages.backends.s3 import S3Storage

from config.environment import ConfigurationError, RuntimeEnvironment
from config.media_storage import MediaStorageMode, load_media_storage_config


def test_local_defaults_to_filesystem_media_storage() -> None:
    config = load_media_storage_config(
        environ={},
        environment=RuntimeEnvironment.LOCAL,
    )

    assert config.mode is MediaStorageMode.FILESYSTEM
    assert config.is_filesystem is True
    assert config.media_url == "/media/"
    assert config.as_django_storages() == {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }


@pytest.mark.parametrize("environment", [RuntimeEnvironment.PREVIEW, RuntimeEnvironment.PRODUCTION])
def test_deployed_environments_require_explicit_media_storage_mode(
    environment: RuntimeEnvironment,
) -> None:
    with pytest.raises(ConfigurationError, match="MEDIA_STORAGE_MODE is required"):
        load_media_storage_config(environ={}, environment=environment)


def test_production_rejects_process_local_filesystem_media() -> None:
    with pytest.raises(ConfigurationError, match="must use the shared s3 backend"):
        load_media_storage_config(
            environ={"MEDIA_STORAGE_MODE": "filesystem"},
            environment=RuntimeEnvironment.PRODUCTION,
        )


def test_preview_can_explicitly_use_filesystem_for_ephemeral_validation() -> None:
    config = load_media_storage_config(
        environ={"MEDIA_STORAGE_MODE": "filesystem"},
        environment=RuntimeEnvironment.PREVIEW,
    )

    assert config.mode is MediaStorageMode.FILESYSTEM


def test_s3_backend_uses_public_immutable_content_delivery() -> None:
    config = load_media_storage_config(
        environ={
            "MEDIA_STORAGE_MODE": "s3",
            "MEDIA_S3_BUCKET": "cultural-currency-media",
            "MEDIA_S3_REGION": "eu-north-1",
            "MEDIA_CDN_DOMAIN": "media.example.test",
        },
        environment=RuntimeEnvironment.PRODUCTION,
    )

    storage = config.as_django_storages()["default"]
    assert storage["BACKEND"] == "storages.backends.s3.S3Storage"
    assert storage["OPTIONS"] == {
        "bucket_name": "cultural-currency-media",
        "region_name": "eu-north-1",
        "location": "media",
        "default_acl": None,
        "querystring_auth": False,
        "file_overwrite": True,
        "object_parameters": {
            "CacheControl": "public, max-age=31536000, immutable",
        },
        "use_ssl": True,
        "verify": True,
        "custom_domain": "media.example.test",
        "url_protocol": "https:",
    }
    assert config.media_url == "https://media.example.test/media/"


def test_s3_backend_generates_stable_unsigned_cdn_url_without_network() -> None:
    storage = S3Storage(
        access_key="test-access-key",
        secret_key="test-secret-key",
        bucket_name="media-bucket",
        region_name="eu-north-1",
        location="media",
        custom_domain="media.example.test",
        querystring_auth=False,
        object_parameters={
            "CacheControl": "public, max-age=31536000, immutable",
        },
    )

    url = storage.url("sourced/ab/abcdef.webp")

    assert url == "https://media.example.test/media/sourced/ab/abcdef.webp"
    assert "?" not in url
    assert storage.get_object_parameters("sourced/ab/abcdef.webp") == {
        "CacheControl": "public, max-age=31536000, immutable",
    }


def test_s3_compatible_endpoint_is_supported_without_credential_config() -> None:
    config = load_media_storage_config(
        environ={
            "MEDIA_STORAGE_MODE": "s3",
            "MEDIA_S3_BUCKET": "media",
            "MEDIA_S3_REGION": "auto",
            "MEDIA_S3_ENDPOINT_URL": "https://account.r2.cloudflarestorage.com",
        },
        environment=RuntimeEnvironment.PRODUCTION,
    )

    options = config.as_django_storages()["default"]["OPTIONS"]
    assert options["endpoint_url"] == "https://account.r2.cloudflarestorage.com"
    assert "access_key" not in options
    assert "secret_key" not in options


@pytest.mark.parametrize(
    ("environment", "endpoint", "message"),
    [
        (
            RuntimeEnvironment.PRODUCTION,
            "http://minio.example.test",
            "must use HTTPS",
        ),
        (
            RuntimeEnvironment.PREVIEW,
            "https://user:secret@example.test",
            "credential-free HTTP",
        ),
        (
            RuntimeEnvironment.TEST,
            "https://example.test/path",
            "without a path",
        ),
        (
            RuntimeEnvironment.TEST,
            "https://example.test?token=secret",
            "without a path",
        ),
    ],
)
def test_invalid_s3_endpoint_fails_fast(
    environment: RuntimeEnvironment,
    endpoint: str,
    message: str,
) -> None:
    with pytest.raises(ConfigurationError, match=message):
        load_media_storage_config(
            environ={
                "MEDIA_STORAGE_MODE": "s3",
                "MEDIA_S3_BUCKET": "media",
                "MEDIA_S3_REGION": "auto",
                "MEDIA_S3_ENDPOINT_URL": endpoint,
            },
            environment=environment,
        )


@pytest.mark.parametrize(
    ("name", "value", "message"),
    [
        ("MEDIA_S3_BUCKET", "https://bucket.example", "plain bucket name"),
        ("MEDIA_S3_BUCKET", "bucket/name", "plain bucket name"),
        ("MEDIA_S3_REGION", "eu north 1", "plain region identifier"),
        ("MEDIA_CDN_DOMAIN", "https://media.example.test", "host name"),
        ("MEDIA_CDN_DOMAIN", "user@media.example.test", "host name"),
        ("MEDIA_CDN_DOMAIN", "media.example.test/path", "host name"),
    ],
)
def test_invalid_s3_identifiers_fail_fast(name: str, value: str, message: str) -> None:
    environ = {
        "MEDIA_STORAGE_MODE": "s3",
        "MEDIA_S3_BUCKET": "media-bucket",
        "MEDIA_S3_REGION": "eu-north-1",
        name: value,
    }

    with pytest.raises(ConfigurationError, match=message):
        load_media_storage_config(
            environ=environ,
            environment=RuntimeEnvironment.PRODUCTION,
        )


def test_storage_config_repr_contains_no_credentials() -> None:
    config = load_media_storage_config(
        environ={
            "MEDIA_STORAGE_MODE": "s3",
            "MEDIA_S3_BUCKET": "media",
            "MEDIA_S3_REGION": "eu-north-1",
        },
        environment=RuntimeEnvironment.PRODUCTION,
    )

    assert "access_key" not in repr(config)
    assert "secret" not in repr(config)
