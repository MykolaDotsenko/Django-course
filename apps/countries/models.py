from __future__ import annotations

from datetime import date

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


class Country(models.Model):
    iso2 = models.CharField(max_length=2, unique=True)
    iso3 = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=120)
    official_name = models.CharField(max_length=180, blank=True)
    capital = models.CharField(max_length=120, blank=True)
    region = models.CharField(max_length=80, blank=True)
    subregion = models.CharField(max_length=120, blank=True)
    flag_url = models.URLField(blank=True)
    is_active = models.BooleanField(default=True)
    metadata_source = models.CharField(max_length=80, blank=True)
    metadata_fetched_at = models.DateTimeField(null=True, blank=True)
    metadata_verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("name", "iso2")

    def save(self, *args, **kwargs):
        self.iso2 = self.iso2.upper()
        self.iso3 = self.iso3.upper()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.name} ({self.iso2})"


class Currency(models.Model):
    code = models.CharField(max_length=3, unique=True)
    name = models.CharField(max_length=120)
    symbol = models.CharField(max_length=16, blank=True)
    minor_units = models.PositiveSmallIntegerField(default=2)
    is_active = models.BooleanField(default=True)
    active_from = models.DateField(null=True, blank=True)
    active_to = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ("code",)

    def clean(self):
        if self.active_from and self.active_to and self.active_to < self.active_from:
            raise ValidationError({"active_to": "Currency active_to cannot precede active_from."})

    def save(self, *args, **kwargs):
        self.code = self.code.upper()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"


class CountryCurrencyQuerySet(models.QuerySet):
    def current(self):
        return self.filter(
            country__is_active=True,
            currency__is_active=True,
            valid_to__isnull=True,
        )

    def on_date(self, selected_date: date):
        return self.filter(
            Q(valid_from__isnull=True) | Q(valid_from__lte=selected_date),
            Q(valid_to__isnull=True) | Q(valid_to__gte=selected_date),
        )

    def primary(self):
        return self.filter(is_primary=True)


class CountryCurrency(models.Model):
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name="currency_links")
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, related_name="country_links")
    is_primary = models.BooleanField(default=False)
    valid_from = models.DateField(null=True, blank=True)
    valid_to = models.DateField(null=True, blank=True)
    usage_role = models.CharField(max_length=80, blank=True)
    source = models.CharField(max_length=160)

    objects = CountryCurrencyQuerySet.as_manager()

    class Meta:
        ordering = ("country__name", "-is_primary", "currency__code")
        constraints = [
            models.CheckConstraint(
                condition=Q(valid_from__isnull=True)
                | Q(valid_to__isnull=True)
                | Q(valid_to__gte=models.F("valid_from")),
                name="country_currency_valid_date_range",
            ),
            models.UniqueConstraint(
                fields=("country", "currency"),
                condition=Q(valid_to__isnull=True),
                name="unique_active_country_currency",
            ),
            models.UniqueConstraint(
                fields=("country",),
                condition=Q(is_primary=True, valid_to__isnull=True),
                name="unique_active_primary_currency_per_country",
            ),
        ]

    def clean(self):
        if self.valid_from and self.valid_to and self.valid_to < self.valid_from:
            raise ValidationError({"valid_to": "valid_to cannot precede valid_from."})

    def __str__(self) -> str:
        return f"{self.country.iso2} → {self.currency.code}"


def primary_currency_for(country_code: str, selected_date: date | None = None) -> Currency | None:
    links = CountryCurrency.objects.filter(country__iso2=country_code.upper()).primary()
    links = links.current() if selected_date is None else links.on_date(selected_date)
    link = links.select_related("currency").order_by("-valid_from").first()
    return link.currency if link else None
