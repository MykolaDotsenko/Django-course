from __future__ import annotations

from datetime import timedelta
from io import StringIO
import os
from pathlib import Path

import pytest
from django.core.files.base import ContentFile
from django.core.files.storage import storages
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import override_settings
from django.utils import timezone

from apps.media.models import MediaAsset, MediaKind, MediaRole, MediaSourceKind


@pytest.fixture
def media_storage(tmp_path: Path):
    storage_settings = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
    with override_settings(
        MEDIA_ROOT=tmp_path,
        MEDIA_URL="/media/",
        STORAGES=storage_settings,
    ):
        storage = storages["default"]
        yield storage


def _asset_with_file(name: str) -> MediaAsset:
    return MediaAsset.objects.create(
        kind=MediaKind.CONTEMPORARY_PHOTO,
        source_kind=MediaSourceKind.MANUAL,
        role=MediaRole.COUNTRY_HERO,
        title="Referenced media",
        storage_file=name,
    )


def _make_old(path: Path, *, hours: int = 48) -> None:
    timestamp = (timezone.now() - timedelta(hours=hours)).timestamp()
    path.touch(exist_ok=True)
    os.utime(path, (timestamp, timestamp))


@pytest.mark.django_db
def test_orphan_prune_treats_missing_managed_prefixes_as_empty(media_storage) -> None:
    stdout = StringIO()

    call_command("prune_orphan_media_storage", stdout=stdout)

    assert "scanned=0" in stdout.getvalue()
    assert "orphan_candidates=0" in stdout.getvalue()


@pytest.mark.django_db
def test_orphan_prune_defaults_to_dry_run_and_preserves_referenced_media(
    media_storage,
    tmp_path: Path,
) -> None:
    referenced = "sourced/aa/referenced.webp"
    orphan = "sourced/bb/orphan.webp"
    media_storage.save(referenced, ContentFile(b"referenced"))
    media_storage.save(orphan, ContentFile(b"orphan"))
    _asset_with_file(referenced)
    _make_old(tmp_path / orphan)

    stdout = StringIO()
    call_command(
        "prune_orphan_media_storage",
        older_than_hours=24,
        stdout=stdout,
    )

    assert media_storage.exists(referenced)
    assert media_storage.exists(orphan)
    assert f"ORPHAN: {orphan}" in stdout.getvalue()
    assert "DRY RUN:" in stdout.getvalue()


@pytest.mark.django_db
def test_orphan_prune_apply_deletes_only_old_unreferenced_managed_objects(
    media_storage,
    tmp_path: Path,
) -> None:
    old_orphan = "generated/aa/old.webp"
    young_orphan = "generated/bb/young.webp"
    unmanaged = "other/keep.webp"

    media_storage.save(old_orphan, ContentFile(b"old"))
    media_storage.save(young_orphan, ContentFile(b"young"))
    media_storage.save(unmanaged, ContentFile(b"unmanaged"))
    _make_old(tmp_path / old_orphan)

    stdout = StringIO()
    call_command(
        "prune_orphan_media_storage",
        apply=True,
        older_than_hours=24,
        stdout=stdout,
    )

    assert not media_storage.exists(old_orphan)
    assert media_storage.exists(young_orphan)
    assert media_storage.exists(unmanaged)
    assert f"DELETED: {old_orphan}" in stdout.getvalue()
    assert "skipped_young=1" in stdout.getvalue()


@pytest.mark.django_db
def test_orphan_prune_rechecks_reference_before_delete(
    media_storage,
    tmp_path: Path,
    monkeypatch,
) -> None:
    candidate = "sourced/cc/race.webp"
    media_storage.save(candidate, ContentFile(b"race"))
    _make_old(tmp_path / candidate)

    from apps.media.management.commands import prune_orphan_media_storage as command_module

    original_modified_at = command_module._modified_at

    def attach_reference_during_scan(name: str):
        value = original_modified_at(name)
        _asset_with_file(name)
        return value

    monkeypatch.setattr(command_module, "_modified_at", attach_reference_during_scan)

    stdout = StringIO()
    call_command(
        "prune_orphan_media_storage",
        apply=True,
        older_than_hours=24,
        stdout=stdout,
    )

    assert media_storage.exists(candidate)
    assert f"SKIPPED-REFERENCED: {candidate}" in stdout.getvalue()


@pytest.mark.django_db
def test_orphan_prune_respects_scan_cap(media_storage, tmp_path: Path) -> None:
    first = "sourced/a/one.webp"
    second = "sourced/b/two.webp"
    media_storage.save(first, ContentFile(b"one"))
    media_storage.save(second, ContentFile(b"two"))
    _make_old(tmp_path / first)
    _make_old(tmp_path / second)

    with pytest.raises(CommandError, match="exceeded --max-objects"):
        call_command(
            "prune_orphan_media_storage",
            max_objects=1,
            older_than_hours=24,
        )


@pytest.mark.parametrize(
    ("argument", "value", "message"),
    [
        ("older_than_hours", 0, "--older-than-hours must be at least 1"),
        ("max_objects", 0, "--max-objects must be at least 1"),
    ],
)
@pytest.mark.django_db
def test_orphan_prune_rejects_unsafe_limits(argument: str, value: int, message: str) -> None:
    kwargs = {
        "older_than_hours": 24,
        "max_objects": 10,
        argument: value,
    }

    with pytest.raises(CommandError, match=message):
        call_command("prune_orphan_media_storage", **kwargs)
