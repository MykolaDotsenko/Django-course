from __future__ import annotations

import logging

from django.db import DatabaseError

from apps.common.presentation.media_view_models import ImageViewModel
from apps.countries.models import Country
from apps.media.models import MediaRole
from apps.media.presentation import select_media_for_display

logger = logging.getLogger("cultural_currency.culture")


def select_destination_hero_image(country_code: str) -> ImageViewModel | None:
    """Return reviewed current destination photography without making media mandatory."""

    normalized = country_code.upper().strip()
    if not normalized:
        return None

    try:
        country = Country.objects.filter(iso2=normalized).first()
        if country is None:
            return None

        selection = select_media_for_display(
            role=MediaRole.COUNTRY_HERO,
            country=country,
        )
    except DatabaseError as exc:
        logger.warning(
            "Destination hero media lookup failed",
            extra={
                "culture.country": normalized,
                "error_code": exc.__class__.__name__,
            },
        )
        return None

    return selection.image if selection is not None else None
