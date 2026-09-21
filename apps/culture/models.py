from __future__ import annotations

from datetime import date

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q


class StoryMomentCategory(models.TextChoices):
    CURRENCY_INTRODUCTION = "currency_introduction", "Currency introduction"
    CURRENCY_RETIREMENT = "currency_retirement", "Currency retirement"
    REDENOMINATION = "redenomination", "Redenomination"
    MONETARY_UNION = "monetary_union", "Monetary union"
    CASH_CHANGEOVER = "cash_changeover", "Cash changeover"
    CENTRAL_BANK = "central_bank", "Central bank"
    CULTURAL_MONEY_FACT = "cultural_money_fact", "Cultural money fact"
    SOURCED_ECONOMIC_CONTEXT = "sourced_economic_context", "Sourced economic context"


class StorySourceKind(models.TextChoices):
    OFFICIAL = "official", "Official public source"
    INSTITUTION = "institution", "Institution / archive"
    WIKIDATA = "wikidata", "Wikidata"
    MANUAL = "manual", "Manual curated source"


class StoryMomentStatus(models.TextChoices):
    CANDIDATE = "candidate", "Candidate"
    NEEDS_REVIEW = "needs_review", "Needs review"
    APPROVED = "approved", "Approved"
    PUBLISHED = "published", "Published"
    RETIRED = "retired", "Retired"
    REJECTED = "rejected", "Rejected"


class StoryDatePrecision(models.TextChoices):
    EXACT_DAY = "exact_day", "Exact day"
    MONTH = "month", "Month"
    YEAR = "year", "Year"
    RANGE = "range", "Range"
    ERA = "era", "Era"
    UNKNOWN = "unknown", "Unknown"


class StoryMomentQuerySet(models.QuerySet):
    def published(self):
        return self.filter(status=StoryMomentStatus.PUBLISHED)

    def relevant_on(self, selected_date: date, *, historical: bool):
        if not historical:
            return self
        return self.filter(start_date__isnull=False, start_date__lte=selected_date).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=selected_date)
        )


class StoryMoment(models.Model):
    category = models.CharField(max_length=32, choices=StoryMomentCategory.choices)
    title = models.CharField(max_length=240)
    summary = models.TextField()
    countries = models.ManyToManyField(
        "countries.Country",
        blank=True,
        related_name="story_moments",
    )
    currencies = models.ManyToManyField(
        "countries.Currency",
        blank=True,
        related_name="story_moments",
    )

    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    date_precision = models.CharField(
        max_length=16,
        choices=StoryDatePrecision.choices,
        default=StoryDatePrecision.UNKNOWN,
    )

    source_kind = models.CharField(max_length=24, choices=StorySourceKind.choices)
    source_name = models.CharField(max_length=200)
    source_url = models.URLField(max_length=700)
    external_id = models.CharField(max_length=120, blank=True)
    source_published_at = models.DateField(null=True, blank=True)
    source_retrieved_at = models.DateTimeField(null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    relevance_weight = models.PositiveSmallIntegerField(
        default=50,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    supports_causality = models.BooleanField(default=False)
    causal_support_note = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=StoryMomentStatus.choices,
        default=StoryMomentStatus.CANDIDATE,
        db_index=True,
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = StoryMomentQuerySet.as_manager()

    class Meta:
        ordering = ("-relevance_weight", "-start_date", "title")
        constraints = [
            models.CheckConstraint(
                condition=Q(start_date__isnull=True)
                | Q(end_date__isnull=True)
                | Q(end_date__gte=models.F("start_date")),
                name="story_moment_valid_date_range",
            ),
            models.UniqueConstraint(
                fields=("source_kind", "external_id"),
                condition=~Q(external_id=""),
                name="story_unique_external_identity",
            ),
        ]

    def clean(self) -> None:
        super().clean()
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError({"end_date": "Story end_date cannot precede start_date."})
        if self.start_date and self.date_precision == StoryDatePrecision.UNKNOWN:
            raise ValidationError(
                {"date_precision": "Dated story moments require explicit temporal precision."}
            )
        if not self.start_date and self.end_date:
            raise ValidationError({"start_date": "end_date requires start_date."})

    @property
    def is_published(self) -> bool:
        return self.status == StoryMomentStatus.PUBLISHED

    def __str__(self) -> str:
        return f"{self.title} [{self.category}]"
