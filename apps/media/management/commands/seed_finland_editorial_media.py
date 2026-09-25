from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from apps.countries.models import Country
from apps.media.catalog import FINLAND_COUNTRY_HERO
from apps.media.models import DatePrecision, MediaAsset, MediaStatus
from apps.media.services import (
    DuplicateMediaContentError,
    MediaPublicationError,
    attach_media_bytes,
)
from apps.media.sources import MediaSourceError, WikimediaCommonsClient
from apps.media.validation import MediaValidationError

_PROTECTED_STATUSES = {
    MediaStatus.APPROVED,
    MediaStatus.PUBLISHED,
    MediaStatus.RETIRED,
}


class Command(BaseCommand):
    help = (
        "Create/update the canonical reviewed-source candidate for the Finland destination hero. "
        "Optional download stays outside request handling and never auto-publishes the asset."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--download",
            action="store_true",
            help="Download and sanitize the pinned Wikimedia source into managed storage.",
        )
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--timeout-seconds", type=float, default=15.0)

    def handle(self, *args, **options):
        spec = FINLAND_COUNTRY_HERO
        country = Country.objects.filter(iso2=spec.country_code).first()
        if country is None:
            raise CommandError(
                "Finland reference data is missing. Run seed_reference_data before this command."
            )

        existing = MediaAsset.objects.filter(
            source_kind=spec.source_kind,
            external_id=spec.external_id,
        ).first()

        if existing is not None and existing.status in _PROTECTED_STATUSES:
            self.stdout.write(
                self.style.WARNING(
                    f"PROTECTED: asset={existing.pk} status={existing.status}; no changes applied."
                )
            )
            return

        if options["dry_run"]:
            action = "update" if existing is not None else "create"
            download = " + download" if options["download"] and not getattr(existing, "storage_file", None) else ""
            self.stdout.write(f"DRY RUN: would {action} Finland hero candidate{download}.")
            return

        downloaded = None
        if options["download"] and (existing is None or not existing.storage_file):
            try:
                downloaded = WikimediaCommonsClient(
                    timeout_seconds=options["timeout_seconds"]
                ).download_media(spec.source_media_url)
            except (MediaSourceError, ValueError) as exc:
                raise CommandError(str(exc)) from exc

        defaults = {
            "country": country,
            "currency": None,
            "kind": spec.kind,
            "role": spec.role,
            "city": spec.city,
            "valid_from": spec.observed_on,
            "valid_to": spec.observed_on,
            "date_precision": DatePrecision.EXACT_DAY,
            "title": spec.title,
            "alt_text": spec.alt_text,
            "caption": spec.caption,
            "focal_x": spec.focal_x,
            "focal_y": spec.focal_y,
            "source_name": spec.source_name,
            "source_url": spec.source_url,
            "source_media_url": spec.source_media_url,
            "creator": spec.creator,
            "licence_id": spec.licence_id,
            "licence_url": spec.licence_url,
            "rights_statement": spec.rights_statement,
            "attribution_text": spec.attribution_text,
            "generated_by_ai": False,
            "status": MediaStatus.NEEDS_REVIEW,
        }

        try:
            with transaction.atomic():
                asset, created = MediaAsset.objects.update_or_create(
                    source_kind=spec.source_kind,
                    external_id=spec.external_id,
                    defaults=defaults,
                )
                if downloaded is not None:
                    attach_media_bytes(
                        asset,
                        downloaded.data,
                        filename=downloaded.filename,
                    )
                    asset.source_retrieved_at = timezone.now()
                    asset.save(update_fields=("source_retrieved_at", "updated_at"))
        except (
            DuplicateMediaContentError,
            MediaPublicationError,
            MediaValidationError,
        ) as exc:
            raise CommandError(str(exc)) from exc

        action = "CREATED" if created else "UPDATED"
        detail = (
            f" sha256={asset.content_hash} size={asset.width}x{asset.height}"
            if asset.content_hash
            else " metadata-only"
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"{action}: asset={asset.pk}{detail}; status={asset.status}; "
                "editorial approval is still required before publication."
            )
        )
