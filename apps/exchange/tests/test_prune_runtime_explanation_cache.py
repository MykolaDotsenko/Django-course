from __future__ import annotations

from datetime import UTC, datetime, timedelta
from io import StringIO
from unittest.mock import patch

import pytest
from django.core.management import CommandError, call_command

from apps.exchange.models import RuntimeExplanationCache

NOW = datetime(2026, 9, 25, 12, 0, tzinfo=UTC)


def _create_cache_row(*, sequence: int, created_at: datetime) -> RuntimeExplanationCache:
    cache_key = f"{sequence:064x}"
    row = RuntimeExplanationCache.objects.create(
        cache_key=cache_key,
        packet_hash=f"{sequence + 1000:064x}",
        prompt_version="runtime-explanation-v1",
        schema_version="runtime-explanation-schema-v1",
        provider="google",
        model="gemini-3.1-flash-lite",
        provider_model_version="gemini-3.1-flash-lite-2026-05",
        locale="en",
        result={"headline": f"Cached explanation {sequence}"},
        provider_response_id=f"response-{sequence}",
    )
    RuntimeExplanationCache.objects.filter(cache_key=cache_key).update(created_at=created_at)
    row.refresh_from_db()
    return row


@pytest.mark.django_db
def test_dry_run_reports_only_rows_strictly_older_than_cutoff() -> None:
    old = _create_cache_row(sequence=1, created_at=NOW - timedelta(days=31))
    boundary = _create_cache_row(sequence=2, created_at=NOW - timedelta(days=30))
    recent = _create_cache_row(sequence=3, created_at=NOW - timedelta(days=29))
    stdout = StringIO()

    with patch(
        "apps.exchange.management.commands.prune_runtime_explanation_cache.timezone.now",
        return_value=NOW,
    ):
        call_command(
            "prune_runtime_explanation_cache",
            older_than_days=30,
            dry_run=True,
            stdout=stdout,
        )

    assert "DRY RUN: 1 runtime explanation cache row(s)" in stdout.getvalue()
    assert RuntimeExplanationCache.objects.filter(cache_key=old.cache_key).exists()
    assert RuntimeExplanationCache.objects.filter(cache_key=boundary.cache_key).exists()
    assert RuntimeExplanationCache.objects.filter(cache_key=recent.cache_key).exists()


@pytest.mark.django_db
def test_pruning_deletes_all_eligible_rows_across_small_batches() -> None:
    old_rows = [
        _create_cache_row(
            sequence=sequence,
            created_at=NOW - timedelta(days=40 + sequence),
        )
        for sequence in range(1, 6)
    ]
    boundary = _create_cache_row(sequence=20, created_at=NOW - timedelta(days=30))
    recent = _create_cache_row(sequence=21, created_at=NOW - timedelta(days=2))
    stdout = StringIO()

    with patch(
        "apps.exchange.management.commands.prune_runtime_explanation_cache.timezone.now",
        return_value=NOW,
    ):
        call_command(
            "prune_runtime_explanation_cache",
            older_than_days=30,
            batch_size=2,
            stdout=stdout,
        )

    assert "APPLIED: deleted 5 runtime explanation cache row(s)" in stdout.getvalue()
    assert not RuntimeExplanationCache.objects.filter(
        cache_key__in=[row.cache_key for row in old_rows]
    ).exists()
    assert RuntimeExplanationCache.objects.filter(cache_key=boundary.cache_key).exists()
    assert RuntimeExplanationCache.objects.filter(cache_key=recent.cache_key).exists()


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"older_than_days": 0}, "--older-than-days must be at least 1"),
        ({"older_than_days": -1}, "--older-than-days must be at least 1"),
        (
            {"older_than_days": 30, "batch_size": 0},
            "--batch-size must be between 1 and 5000",
        ),
        (
            {"older_than_days": 30, "batch_size": 5001},
            "--batch-size must be between 1 and 5000",
        ),
    ],
)
def test_invalid_pruning_parameters_fail_before_deleting(
    kwargs: dict[str, int],
    message: str,
) -> None:
    row = _create_cache_row(sequence=50, created_at=NOW - timedelta(days=90))

    with (
        patch(
            "apps.exchange.management.commands.prune_runtime_explanation_cache.timezone.now",
            return_value=NOW,
        ),
        pytest.raises(CommandError, match=message),
    ):
        call_command("prune_runtime_explanation_cache", **kwargs)

    assert RuntimeExplanationCache.objects.filter(cache_key=row.cache_key).exists()
