from __future__ import annotations

from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from apps.exchange.models import RuntimeExplanationCache

_DEFAULT_BATCH_SIZE = 500
_MAX_BATCH_SIZE = 5000


class Command(BaseCommand):
    help = (
        "Delete persisted runtime AI explanations older than an explicit retention window. "
        "Use --dry-run to inspect the eligible row count without deleting anything."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--older-than-days",
            type=int,
            required=True,
            help="Delete rows strictly older than this many days.",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=_DEFAULT_BATCH_SIZE,
            help=f"Rows selected per delete batch (1-{_MAX_BATCH_SIZE}).",
        )
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        older_than_days = options["older_than_days"]
        batch_size = options["batch_size"]
        dry_run = bool(options["dry_run"])

        if older_than_days < 1:
            raise CommandError("--older-than-days must be at least 1.")
        if not 1 <= batch_size <= _MAX_BATCH_SIZE:
            raise CommandError(f"--batch-size must be between 1 and {_MAX_BATCH_SIZE}.")

        cutoff = timezone.now() - timedelta(days=older_than_days)
        eligible = RuntimeExplanationCache.objects.filter(created_at__lt=cutoff)

        if dry_run:
            count = eligible.count()
            self.stdout.write(
                self.style.SUCCESS(
                    f"DRY RUN: {count} runtime explanation cache row(s) older than "
                    f"{cutoff.isoformat()}."
                )
            )
            return

        deleted_total = 0
        while True:
            cache_keys = list(
                eligible.order_by("created_at", "cache_key").values_list(
                    "cache_key",
                    flat=True,
                )[:batch_size]
            )
            if not cache_keys:
                break

            deleted, _details = RuntimeExplanationCache.objects.filter(
                cache_key__in=cache_keys,
                created_at__lt=cutoff,
            ).delete()
            deleted_total += deleted

        self.stdout.write(
            self.style.SUCCESS(
                f"APPLIED: deleted {deleted_total} runtime explanation cache row(s) older than "
                f"{cutoff.isoformat()}."
            )
        )
