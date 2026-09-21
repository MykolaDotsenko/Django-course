from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError

from apps.media.models import MediaAsset
from apps.media.services import MediaPublicationError, create_responsive_derivative
from apps.media.validation import MediaValidationError


class Command(BaseCommand):
    help = (
        "Create one sanitized WebP responsive derivative from reviewed managed media. "
        "The derivative is never auto-published."
    )

    def add_arguments(self, parser):
        parser.add_argument("--asset-id", type=int, required=True)
        parser.add_argument("--width", type=int, required=True)

    def handle(self, *args, **options):
        source = MediaAsset.objects.filter(pk=options["asset_id"]).first()
        if source is None:
            raise CommandError("MediaAsset does not exist.")
        try:
            derivative = create_responsive_derivative(source, width=options["width"])
        except (MediaPublicationError, MediaValidationError) as exc:
            raise CommandError(str(exc)) from exc

        self.stdout.write(
            self.style.SUCCESS(
                f"CREATED: derivative={derivative.pk} source={source.pk} "
                f"size={derivative.width}x{derivative.height}; status={derivative.status}"
            )
        )
