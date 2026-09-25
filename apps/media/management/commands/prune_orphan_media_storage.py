from __future__ import annotations

from collections.abc import Iterator
from datetime import timedelta

from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from apps.media.models import MediaAsset

_MANAGED_PREFIXES = ("sourced", "generated")


def _walk_storage(prefix: str) -> Iterator[str]:
    try:
        directories, files = default_storage.listdir(prefix)
    except FileNotFoundError:
        return
    except Exception as exc:
        raise CommandError(f"Media storage cannot list {prefix!r}.") from exc

    for filename in files:
        yield f"{prefix}/{filename}"
    for directory in directories:
        yield from _walk_storage(f"{prefix}/{directory}")


def _modified_at(name: str):
    try:
        value = default_storage.get_modified_time(name)
    except Exception as exc:
        raise CommandError(f"Media storage cannot read modified time for {name!r}.") from exc

    if timezone.is_naive(value):
        value = timezone.make_aware(value, timezone.get_current_timezone())
    return value


class Command(BaseCommand):
    help = (
        "Find unreferenced managed media objects and optionally delete only objects older "
        "than a safety window. Dry-run is the default."
    )

    def add_arguments(self, parser):
        parser.add_argument("--apply", action="store_true")
        parser.add_argument("--older-than-hours", type=int, default=24)
        parser.add_argument("--max-objects", type=int, default=10_000)

    def handle(self, *args, **options):
        older_than_hours = options["older_than_hours"]
        max_objects = options["max_objects"]
        apply = options["apply"]

        if older_than_hours < 1:
            raise CommandError("--older-than-hours must be at least 1.")
        if max_objects < 1:
            raise CommandError("--max-objects must be at least 1.")

        referenced = set(
            MediaAsset.objects.exclude(storage_file="").values_list("storage_file", flat=True)
        )
        cutoff = timezone.now() - timedelta(hours=older_than_hours)

        scanned = candidates = deleted = skipped_young = 0
        for prefix in _MANAGED_PREFIXES:
            names = _walk_storage(prefix)
            for name in names:
                    scanned += 1
                    if scanned > max_objects:
                        raise CommandError(
                            "Media storage scan exceeded --max-objects; increase the explicit "
                            "limit after reviewing bucket size."
                        )

                    if name in referenced:
                        continue

                    if _modified_at(name) > cutoff:
                        skipped_young += 1
                        continue

                    candidates += 1
                    if not apply:
                        self.stdout.write(f"ORPHAN: {name}")
                        continue

                    if MediaAsset.objects.filter(storage_file=name).exists():
                        self.stdout.write(f"SKIPPED-REFERENCED: {name}")
                        continue

                    try:
                        default_storage.delete(name)
                    except Exception as exc:
                        raise CommandError(f"Failed to delete orphan media {name!r}.") from exc
                    deleted += 1
                    self.stdout.write(f"DELETED: {name}")

        mode = "APPLIED" if apply else "DRY RUN"
        self.stdout.write(
            self.style.SUCCESS(
                f"{mode}: scanned={scanned} orphan_candidates={candidates} "
                f"deleted={deleted} skipped_young={skipped_young}"
            )
        )
