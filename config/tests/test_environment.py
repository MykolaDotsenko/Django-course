from __future__ import annotations

import pytest

from config.environment import (
    ConfigurationError,
    RuntimeEnvironment,
    load_runtime_config,
)


def test_local_defaults_require_no_committed_secret() -> None:
    config = load_runtime_config({})

    assert config.environment is RuntimeEnvironment.LOCAL
    assert config.debug is True
    assert config.allowed_hosts == ("localhost", "127.0.0.1", "[::1]")
    assert len(config.secret_key) >= 50


def test_test_environment_requires_no_ci_secret() -> None:
    config = load_runtime_config({"APP_ENV": "test"})

    assert config.environment is RuntimeEnvironment.TEST
    assert config.debug is False
    assert "testserver" in config.allowed_hosts
    assert "not-for-production" in config.secret_key


def test_boolean_values_are_parsed_case_insensitively() -> None:
    config = load_runtime_config(
        {
            "APP_ENV": "test",
            "DJANGO_DEBUG": "YeS",
        }
    )

    assert config.debug is True


@pytest.mark.parametrize("value", ["maybe", "2", "enabled"])
def test_invalid_boolean_values_fail_fast(value: str) -> None:
    with pytest.raises(ConfigurationError, match="DJANGO_DEBUG must be a boolean"):
        load_runtime_config(
            {
                "APP_ENV": "test",
                "DJANGO_DEBUG": value,
            }
        )


def test_unknown_environment_fails_fast() -> None:
    with pytest.raises(ConfigurationError, match="APP_ENV must be one of"):
        load_runtime_config({"APP_ENV": "prod"})


@pytest.mark.parametrize("environment", ["preview", "production"])
def test_deployed_environments_require_allowed_hosts(environment: str) -> None:
    with pytest.raises(ConfigurationError, match="DJANGO_ALLOWED_HOSTS is required"):
        load_runtime_config(
            {
                "APP_ENV": environment,
                "DJANGO_SECRET_KEY": "x" * 50,
            }
        )


@pytest.mark.parametrize("environment", ["preview", "production"])
def test_deployed_environments_require_secret(environment: str) -> None:
    with pytest.raises(ConfigurationError, match="DJANGO_SECRET_KEY is required"):
        load_runtime_config(
            {
                "APP_ENV": environment,
                "DJANGO_ALLOWED_HOSTS": "example.com",
            }
        )


@pytest.mark.parametrize("environment", ["preview", "production"])
def test_deployed_environments_reject_short_secret(environment: str) -> None:
    with pytest.raises(ConfigurationError, match="at least 50 characters"):
        load_runtime_config(
            {
                "APP_ENV": environment,
                "DJANGO_SECRET_KEY": "short",
                "DJANGO_ALLOWED_HOSTS": "example.com",
            }
        )


@pytest.mark.parametrize("environment", ["preview", "production"])
def test_deployed_environments_reject_debug(environment: str) -> None:
    with pytest.raises(ConfigurationError, match="DJANGO_DEBUG must be false"):
        load_runtime_config(
            {
                "APP_ENV": environment,
                "DJANGO_DEBUG": "true",
                "DJANGO_SECRET_KEY": "x" * 50,
                "DJANGO_ALLOWED_HOSTS": "example.com",
            }
        )


@pytest.mark.parametrize("environment", ["preview", "production"])
def test_deployed_environments_reject_wildcard_hosts(environment: str) -> None:
    with pytest.raises(ConfigurationError, match="Wildcard"):
        load_runtime_config(
            {
                "APP_ENV": environment,
                "DJANGO_SECRET_KEY": "x" * 50,
                "DJANGO_ALLOWED_HOSTS": "*",
            }
        )


def test_allowed_hosts_reject_urls_and_paths() -> None:
    with pytest.raises(ConfigurationError, match="without schemes or paths"):
        load_runtime_config(
            {
                "APP_ENV": "test",
                "DJANGO_ALLOWED_HOSTS": "https://example.com",
            }
        )


def test_production_accepts_explicit_safe_configuration() -> None:
    config = load_runtime_config(
        {
            "APP_ENV": "production",
            "DJANGO_DEBUG": "false",
            "DJANGO_SECRET_KEY": "s" * 64,
            "DJANGO_ALLOWED_HOSTS": "example.com,www.example.com",
        }
    )

    assert config.environment is RuntimeEnvironment.PRODUCTION
    assert config.debug is False
    assert config.allowed_hosts == ("example.com", "www.example.com")
    assert config.is_production is True
