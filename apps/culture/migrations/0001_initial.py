import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("countries", "0002_currency_coverage_bounds"),
    ]

    operations = [
        migrations.CreateModel(
            name="StoryMoment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("currency_introduction", "Currency introduction"),
                            ("currency_retirement", "Currency retirement"),
                            ("redenomination", "Redenomination"),
                            ("monetary_union", "Monetary union"),
                            ("cash_changeover", "Cash changeover"),
                            ("central_bank", "Central bank"),
                            ("cultural_money_fact", "Cultural money fact"),
                            ("sourced_economic_context", "Sourced economic context"),
                        ],
                        max_length=32,
                    ),
                ),
                ("title", models.CharField(max_length=240)),
                (
                    "summary",
                    models.TextField(
                        validators=[django.core.validators.MaxLengthValidator(2000)]
                    ),
                ),
                ("start_date", models.DateField(blank=True, null=True)),
                ("end_date", models.DateField(blank=True, null=True)),
                (
                    "date_precision",
                    models.CharField(
                        choices=[
                            ("exact_day", "Exact day"),
                            ("month", "Month"),
                            ("year", "Year"),
                            ("range", "Range"),
                            ("era", "Era"),
                            ("unknown", "Unknown"),
                        ],
                        default="unknown",
                        max_length=16,
                    ),
                ),
                (
                    "source_kind",
                    models.CharField(
                        choices=[
                            ("official", "Official public source"),
                            ("institution", "Institution / archive"),
                            ("wikidata", "Wikidata"),
                            ("manual", "Manual curated source"),
                        ],
                        max_length=24,
                    ),
                ),
                ("source_name", models.CharField(max_length=200)),
                ("source_url", models.URLField(max_length=700)),
                ("external_id", models.CharField(blank=True, max_length=120)),
                ("source_published_at", models.DateField(blank=True, null=True)),
                ("source_retrieved_at", models.DateTimeField(blank=True, null=True)),
                ("verified_at", models.DateTimeField(blank=True, null=True)),
                (
                    "relevance_weight",
                    models.PositiveSmallIntegerField(
                        default=50,
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(100),
                        ],
                    ),
                ),
                ("supports_causality", models.BooleanField(default=False)),
                ("causal_support_note", models.TextField(blank=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("candidate", "Candidate"),
                            ("needs_review", "Needs review"),
                            ("approved", "Approved"),
                            ("published", "Published"),
                            ("retired", "Retired"),
                            ("rejected", "Rejected"),
                        ],
                        db_index=True,
                        default="candidate",
                        max_length=20,
                    ),
                ),
                ("reviewed_at", models.DateTimeField(blank=True, null=True)),
                ("published_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "countries",
                    models.ManyToManyField(
                        blank=True,
                        related_name="story_moments",
                        to="countries.country",
                    ),
                ),
                (
                    "currencies",
                    models.ManyToManyField(
                        blank=True,
                        related_name="story_moments",
                        to="countries.currency",
                    ),
                ),
            ],
            options={
                "ordering": ("-relevance_weight", "-start_date", "title"),
                "constraints": [
                    models.CheckConstraint(
                        condition=models.Q(
                            ("start_date__isnull", True),
                            ("end_date__isnull", True),
                            ("end_date__gte", models.F("start_date")),
                            _connector="OR",
                        ),
                        name="story_moment_valid_date_range",
                    ),
                    models.UniqueConstraint(
                        condition=models.Q(("external_id", ""), _negated=True),
                        fields=("source_kind", "external_id"),
                        name="story_unique_external_identity",
                    ),
                ],
            },
        ),
    ]
