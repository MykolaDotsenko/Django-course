# Generated for Cultural Currency Converter PR7A media pipeline.

import apps.media.models
import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("countries", "0002_currency_coverage_bounds"),
    ]

    operations = [
        migrations.CreateModel(
            name="MediaAsset",
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
                    "kind",
                    models.CharField(
                        choices=[
                            ("contemporary_photo", "Contemporary photo"),
                            ("archival_photo", "Archival photo"),
                            ("artwork", "Artwork"),
                            ("heritage_object", "Heritage object"),
                            ("map", "Map"),
                            ("generated_illustration", "Generated illustration"),
                            ("decorative_pattern", "Decorative pattern"),
                            ("brand_asset", "Brand asset"),
                        ],
                        max_length=32,
                    ),
                ),
                (
                    "source_kind",
                    models.CharField(
                        choices=[
                            ("wikimedia_commons", "Wikimedia Commons"),
                            ("europeana", "Europeana"),
                            ("institution", "Institution / archive"),
                            ("manual", "Manual / owned"),
                            ("generated", "Generated"),
                        ],
                        max_length=32,
                    ),
                ),
                (
                    "role",
                    models.CharField(
                        choices=[
                            ("country_hero", "Country hero"),
                            ("country_teaser", "Country teaser"),
                            ("story_cover", "Story cover"),
                            ("story_chapter", "Story chapter"),
                            ("comparison_then", "Comparison then"),
                            ("comparison_now", "Comparison now"),
                            ("historical_timeline", "Historical timeline"),
                            ("social_preview", "Social preview"),
                            ("decorative_background", "Decorative background"),
                        ],
                        max_length=32,
                    ),
                ),
                ("city", models.CharField(blank=True, max_length=120)),
                ("valid_from", models.DateField(blank=True, null=True)),
                ("valid_to", models.DateField(blank=True, null=True)),
                (
                    "date_precision",
                    models.CharField(
                        choices=[
                            ("exact_day", "Exact day"),
                            ("month", "Month"),
                            ("year", "Year"),
                            ("decade", "Decade"),
                            ("range", "Range"),
                            ("era", "Era"),
                            ("unknown", "Unknown"),
                        ],
                        default="unknown",
                        max_length=16,
                    ),
                ),
                ("title", models.CharField(max_length=240)),
                ("alt_text", models.CharField(blank=True, max_length=500)),
                ("caption", models.TextField(blank=True)),
                (
                    "storage_file",
                    models.FileField(
                        blank=True,
                        max_length=500,
                        upload_to=apps.media.models._media_upload_to,
                    ),
                ),
                ("width", models.PositiveIntegerField(blank=True, null=True)),
                ("height", models.PositiveIntegerField(blank=True, null=True)),
                ("aspect_ratio", models.CharField(blank=True, max_length=32)),
                (
                    "focal_x",
                    models.DecimalField(
                        blank=True,
                        decimal_places=3,
                        max_digits=4,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(1),
                        ],
                    ),
                ),
                (
                    "focal_y",
                    models.DecimalField(
                        blank=True,
                        decimal_places=3,
                        max_digits=4,
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(0),
                            django.core.validators.MaxValueValidator(1),
                        ],
                    ),
                ),
                ("content_hash", models.CharField(blank=True, db_index=True, max_length=64)),
                ("variant_width", models.PositiveIntegerField(blank=True, null=True)),
                ("source_name", models.CharField(blank=True, max_length=200)),
                ("source_url", models.URLField(blank=True, max_length=500)),
                ("source_media_url", models.URLField(blank=True, max_length=1000)),
                ("external_id", models.CharField(blank=True, max_length=240)),
                ("creator", models.CharField(blank=True, max_length=300)),
                ("licence_id", models.CharField(blank=True, max_length=120)),
                ("licence_url", models.URLField(blank=True, max_length=500)),
                ("rights_statement", models.TextField(blank=True)),
                ("attribution_text", models.TextField(blank=True)),
                ("source_retrieved_at", models.DateTimeField(blank=True, null=True)),
                ("generated_by_ai", models.BooleanField(default=False)),
                ("ai_label", models.CharField(blank=True, max_length=160)),
                ("generation_provider", models.CharField(blank=True, max_length=120)),
                ("generation_model", models.CharField(blank=True, max_length=160)),
                ("prompt_version", models.CharField(blank=True, max_length=80)),
                ("prompt_hash", models.CharField(blank=True, max_length=64)),
                ("generated_at", models.DateTimeField(blank=True, null=True)),
                ("reviewed_at", models.DateTimeField(blank=True, null=True)),
                ("published_at", models.DateTimeField(blank=True, null=True)),
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
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "country",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="media_assets",
                        to="countries.country",
                    ),
                ),
                (
                    "currency",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="media_assets",
                        to="countries.currency",
                    ),
                ),
                (
                    "derivative_of",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="derivatives",
                        to="media.mediaasset",
                    ),
                ),
            ],
            options={
                "ordering": ("role", "-published_at", "-id"),
                "constraints": [
                    models.CheckConstraint(
                        condition=models.Q(
                            ("valid_from__isnull", True),
                            ("valid_to__isnull", True),
                            ("valid_to__gte", models.F("valid_from")),
                            _connector="OR",
                        ),
                        name="media_valid_date_range",
                    ),
                    models.CheckConstraint(
                        condition=models.Q(
                            ("focal_x__isnull", True),
                            models.Q(("focal_x__gte", 0), ("focal_x__lte", 1)),
                            _connector="OR",
                        ),
                        name="media_focal_x_normalized",
                    ),
                    models.CheckConstraint(
                        condition=models.Q(
                            ("focal_y__isnull", True),
                            models.Q(("focal_y__gte", 0), ("focal_y__lte", 1)),
                            _connector="OR",
                        ),
                        name="media_focal_y_normalized",
                    ),
                    models.UniqueConstraint(
                        condition=models.Q(("external_id", ""), _negated=True),
                        fields=("source_kind", "external_id"),
                        name="media_unique_external_identity",
                    ),
                    models.UniqueConstraint(
                        condition=models.Q(("content_hash", ""), _negated=True),
                        fields=("content_hash",),
                        name="media_unique_content_hash",
                    ),
                ],
            },
        ),
    ]
