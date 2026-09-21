from __future__ import annotations

from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.media.models import MediaAsset
from apps.media.services import (
    DuplicateMediaContentError,
    MediaPublicationError,
    attach_media_bytes,
)
from apps.media.validation import MediaValidationError


class Command(BaseCommand):
    help = (
        "Validate, sanitize and attach a local raster file to an unpublished MediaAsset. "
        "The stored file is content-hashed and the asset remains review-gated."
    )

    def add_arguments(self, parser):
        parser.add_argument("--asset-id", type=int, required=True)
        parser.add_argument("--path", required=True)

    def handle(self, *args, **options):
        asset = MediaAsset.objects.filter(pk=options["asset_id"]).first()
        if asset is None:
            raise CommandError("MediaAsset does not exist.")

        path = Path(options["path"]).expanduser()
        if not path.is_file():
            raise CommandError("Media file path does not exist or is not a file.")

        try:
            payload = path.read_bytes()
            attach_media_bytes(asset, payload, filename=path.name)
        except (
            OSError,
            DuplicateMediaContentError,
            MediaPublicationError,
            MediaValidationError,
        ) as exc:
            raise CommandError(str(exc)) from exc

        self.stdout.write(
            self.style.SUCCESS(
                f"ATTACHED: asset={asset.pk} sha256={asset.content_hash} "
                f"size={asset.width}x{asset.height}; status={asset.status}"
            )
        )
