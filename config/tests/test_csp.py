from __future__ import annotations

import pytest

from config.csp import CspConfig, CspMode, load_csp_config
from config.environment import ConfigurationError, RuntimeEnvironment


def test_local_defaults_to_disabled_csp_for_vite_development() -> None:
    config = load_csp_config(environ={}, environment=RuntimeEnvironment.LOCAL)

    assert config == CspConfig(CspMode.DISABLED)
    assert config.enabled is False
    assert config.header_name is None


def test_test_environment_enforces_csp_by_default() -> None:
    config = load_csp_config(environ={}, environment=RuntimeEnvironment.TEST)

    assert config.mode is CspMode.ENFORCE
    assert config.enabled is True
    assert config.header_name == "Content-Security-Policy"


@pytest.mark.parametrize("environment", [RuntimeEnvironment.PREVIEW, RuntimeEnvironment.PRODUCTION])
def test_deployed_environments_require_explicit_csp_mode(
    environment: RuntimeEnvironment,
) -> None:
    with pytest.raises(ConfigurationError, match="DJANGO_CSP_MODE is required"):
        load_csp_config(environ={}, environment=environment)


@pytest.mark.parametrize("environment", [RuntimeEnvironment.PREVIEW, RuntimeEnvironment.PRODUCTION])
def test_deployed_environments_reject_disabled_csp(environment: RuntimeEnvironment) -> None:
    with pytest.raises(ConfigurationError, match="cannot be disabled"):
        load_csp_config(
            environ={"DJANGO_CSP_MODE": "disabled"},
            environment=environment,
        )


@pytest.mark.parametrize(
    ("value", "expected_mode", "expected_header"),
    [
        ("REPORT-ONLY", CspMode.REPORT_ONLY, "Content-Security-Policy-Report-Only"),
        ("enforce", CspMode.ENFORCE, "Content-Security-Policy"),
    ],
)
def test_deployed_csp_modes_are_parsed_case_insensitively(
    value: str,
    expected_mode: CspMode,
    expected_header: str,
) -> None:
    config = load_csp_config(
        environ={"DJANGO_CSP_MODE": value},
        environment=RuntimeEnvironment.PRODUCTION,
    )

    assert config.mode is expected_mode
    assert config.header_name == expected_header


def test_unknown_csp_mode_fails_fast() -> None:
    with pytest.raises(ConfigurationError, match="must be disabled, report-only or enforce"):
        load_csp_config(
            environ={"DJANGO_CSP_MODE": "strict"},
            environment=RuntimeEnvironment.TEST,
        )
