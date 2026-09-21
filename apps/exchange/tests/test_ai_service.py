from __future__ import annotations

from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from django.core.cache import cache
from django.db import transaction
from django.test import override_settings

from apps.exchange.ai.contracts import ProviderExplanation
from apps.exchange.ai.service import (
    AITransactionPolicyError,
    RuntimeExplanationService,
    build_runtime_explanation_service,
)
from apps.exchange.ai.tokens import TrustedConversionSnapshot
from apps.exchange.domain import ObservationGranularity
from apps.exchange.models import RuntimeExplanationCache
from integrations.gemini.errors import AIProviderUnavailable
from integrations.gemini.models import ProviderUsage


@pytest.fixture(autouse=True)
def clear_ai_cache():
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def snapshot():
    return TrustedConversionSnapshot(
        input_amount=Decimal("100.00"),
        output_amount=Decimal("17450"),
        base_currency="EUR",
        quote_currency="JPY",
        rate=Decimal("174.50"),
        requested_date=None,
        effective_date=date(2026, 9, 18),
        historical=False,
        observation_granularity=ObservationGranularity.DAILY,
        provider_keys=("ecb",),
        stale=False,
    )


def _payload():
    return {
        "headline": "Reference conversion explained",
        "bullets": [
            {
                "text": "100 EUR is approximately 17450 JPY.",
                "supporting_fact_ids": ["conversion"],
            },
            {
                "text": "The displayed rate is 1 EUR = 174.5 JPY and attribution includes ECB.",
                "supporting_fact_ids": ["rate", "provider"],
            },
            {
                "text": "The effective observation date is 2026-09-18.",
                "supporting_fact_ids": ["effective_date"],
            },
        ],
        "caveat": (
            "Reference exchange rates are informational; payment providers may use different "
            "rates or add fees."
        ),
    }


class FakeDrafter:
    def __init__(self, *, payload=None, error=None):
        self.payload = payload or _payload()
        self.error = error
        self.calls = 0

    def draft(self, packet):
        self.calls += 1
        if self.error is not None:
            raise self.error
        return ProviderExplanation(
            payload=self.payload,
            provider_model="gemini-3.1-flash-lite-2026-05",
            response_id="response-1",
            usage=ProviderUsage(input_tokens=120, output_tokens=60, total_tokens=180),
        )


@pytest.mark.django_db(transaction=True)
def test_live_explanation_is_validated_persisted_and_reused(snapshot):
    drafter = FakeDrafter()
    service = RuntimeExplanationService(
        enabled=True,
        model="gemini-3.1-flash-lite",
        drafter=drafter,
    )

    first = service.explain(snapshot)
    second = service.explain(snapshot)

    assert first.result.generated is True
    assert first.cache_status == "live"
    assert second.cache_status == "persistent_hit"
    assert drafter.calls == 1

    stored = RuntimeExplanationCache.objects.get()
    assert stored.provider == "google"
    assert stored.model == "gemini-3.1-flash-lite"
    assert stored.provider_model_version == "gemini-3.1-flash-lite-2026-05"
    assert stored.input_tokens == 120
    assert stored.output_tokens == 60
    assert stored.total_tokens == 180
    assert stored.provider_response_id == "response-1"


@pytest.mark.django_db(transaction=True)
def test_provider_failure_returns_deterministic_fallback_and_sets_cooldown(snapshot):
    drafter = FakeDrafter(error=AIProviderUnavailable("down"))
    service = RuntimeExplanationService(
        enabled=True,
        model="gemini-3.1-flash-lite",
        drafter=drafter,
    )

    first = service.explain(snapshot)
    second = service.explain(snapshot)

    assert first.result.generated is False
    assert first.cache_status == "deterministic_fallback"
    assert "temporarily unavailable" in first.result.fallback_reason
    assert second.result.generated is False
    assert "cooling down" in second.result.fallback_reason
    assert drafter.calls == 1
    assert RuntimeExplanationCache.objects.count() == 0


@pytest.mark.django_db(transaction=True)
def test_schema_valid_but_semantically_invalid_output_falls_back(snapshot):
    payload = _payload()
    payload["bullets"][0]["supporting_fact_ids"] = ["invented_fact"]
    drafter = FakeDrafter(payload=payload)
    service = RuntimeExplanationService(
        enabled=True,
        model="gemini-3.1-flash-lite",
        drafter=drafter,
    )

    delivery = service.explain(snapshot)

    assert delivery.result.generated is False
    assert RuntimeExplanationCache.objects.count() == 0


@pytest.mark.django_db
def test_disabled_service_never_calls_provider(snapshot):
    drafter = FakeDrafter()
    service = RuntimeExplanationService(
        enabled=False,
        model="gemini-3.1-flash-lite",
        drafter=drafter,
    )

    delivery = service.explain(snapshot)

    assert delivery.result.generated is False
    assert "disabled" in delivery.result.fallback_reason
    assert drafter.calls == 0


@pytest.mark.django_db(transaction=True)
def test_corrupt_persistent_cache_is_deleted_before_live_generation(snapshot):
    drafter = FakeDrafter()
    service = RuntimeExplanationService(
        enabled=True,
        model="gemini-3.1-flash-lite",
        drafter=drafter,
    )
    service.explain(snapshot)
    stored = RuntimeExplanationCache.objects.get()
    stored.result = {
        "headline": "Bad",
        "bullets": [
            {
                "text": "100 USD is better.",
                "supporting_fact_ids": ["conversion"],
            }
        ],
        "caveat": "Bad cache.",
    }
    stored.save(update_fields=("result",))

    replacement = FakeDrafter()
    second_service = RuntimeExplanationService(
        enabled=True,
        model="gemini-3.1-flash-lite",
        drafter=replacement,
    )
    delivery = second_service.explain(snapshot)

    assert delivery.cache_status == "live"
    assert replacement.calls == 1
    assert RuntimeExplanationCache.objects.count() == 1


@pytest.mark.django_db
def test_inflight_duplicate_uses_fallback_instead_of_second_provider_call(snapshot, monkeypatch):
    drafter = FakeDrafter()
    service = RuntimeExplanationService(
        enabled=True,
        model="gemini-3.1-flash-lite",
        drafter=drafter,
    )
    monkeypatch.setattr(cache, "add", lambda *args, **kwargs: False)

    delivery = service.explain(snapshot)

    assert delivery.result.generated is False
    assert "already being generated" in delivery.result.fallback_reason
    assert drafter.calls == 0


@pytest.mark.django_db(transaction=True)
def test_live_ai_call_is_rejected_inside_database_transaction(snapshot):
    drafter = FakeDrafter()
    service = RuntimeExplanationService(
        enabled=True,
        model="gemini-3.1-flash-lite",
        drafter=drafter,
    )

    with pytest.raises(AITransactionPolicyError), transaction.atomic():
        service.explain(snapshot)

    assert drafter.calls == 0


def test_service_factory_does_not_construct_provider_when_feature_disabled():
    with (
        override_settings(AI_RUNTIME_EXPLANATION_ENABLED=False),
        patch("apps.exchange.ai.service.GeminiStructuredClient") as client_factory,
    ):
        service = build_runtime_explanation_service()

    assert service.enabled is False
    client_factory.assert_not_called()


def test_service_factory_builds_configured_capability_when_enabled():
    fake_client = SimpleNamespace()
    with (
        override_settings(
            AI_RUNTIME_EXPLANATION_ENABLED=True,
            AI_TEXT_MODEL="gemini-3.1-flash-lite",
            GEMINI_API_KEY="server-secret",
            AI_TIMEOUT_SECONDS=4,
            AI_MAX_ATTEMPTS=2,
        ),
        patch(
            "apps.exchange.ai.service.GeminiStructuredClient",
            return_value=fake_client,
        ) as client_factory,
    ):
        service = build_runtime_explanation_service()

    assert service.enabled is True
    client_factory.assert_called_once_with(
        api_key="server-secret",
        timeout_seconds=4,
        max_attempts=2,
    )
