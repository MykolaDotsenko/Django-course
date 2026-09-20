import pytest

from apps.exchange.config import FxConfigurationError, load_fx_runtime_config


def test_fx_runtime_config_defaults_to_https_v2_endpoint():
    config = load_fx_runtime_config({})
    assert config.base_url == "https://api.frankfurter.dev/v2"
    assert config.timeout_seconds == 3.0


@pytest.mark.parametrize(
    ("values", "message"),
    [
        ({"FRANKFURTER_BASE_URL": "http://example.test/v2"}, "absolute HTTPS"),
        ({"FRANKFURTER_BASE_URL": "https://"}, "absolute HTTPS"),
        (
            {"FRANKFURTER_BASE_URL": "https://user:pass@example.test/v2"},
            "must not contain credentials",
        ),
        (
            {"FRANKFURTER_BASE_URL": "https://example.test/v2?mode=test"},
            "must not contain credentials",
        ),
        ({"FRANKFURTER_TIMEOUT_SECONDS": "slow"}, "must be numeric"),
        ({"FRANKFURTER_TIMEOUT_SECONDS": "30"}, "must be > 0 and <= 10"),
    ],
)
def test_fx_runtime_config_rejects_unsafe_or_invalid_values(values, message):
    with pytest.raises(FxConfigurationError, match=message):
        load_fx_runtime_config(values)
