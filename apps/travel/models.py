from __future__ import annotations

from django.conf import settings
from django.db import models

from apps.countries.models import Country, Currency


class FavouritePair(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favourite_pairs",
    )
    source_currency = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT,
        related_name="+",
    )
    destination_currency = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT,
        related_name="+",
    )
    source_country = models.ForeignKey(
        Country,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="+",
    )
    destination_country = models.ForeignKey(
        Country,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="+",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-updated_at", "-id")
        constraints = [
            models.UniqueConstraint(
                fields=(
                    "user",
                    "source_currency",
                    "destination_currency",
                    "source_country",
                    "destination_country",
                ),
                name="unique_user_favourite_pair",
                nulls_distinct=False,
            )
        ]
        indexes = [
            models.Index(
                fields=("user", "-updated_at"),
                name="travel_fav_user_updated_idx",
            )
        ]

    def __str__(self) -> str:
        return f"{self.user_id}: {self.source_currency.code} → {self.destination_currency.code}"
