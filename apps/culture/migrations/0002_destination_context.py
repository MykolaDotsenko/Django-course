import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("countries", "0002_currency_coverage_bounds"),
        ("culture", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="CulturalProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "summary",
                    models.TextField(
                        blank=True, validators=[django.core.validators.MaxLengthValidator(1200)]
                    ),
                ),
                (
                    "payment_customs",
                    models.TextField(
                        blank=True, validators=[django.core.validators.MaxLengthValidator(1200)]
                    ),
                ),
                (
                    "cash_usage",
                    models.TextField(
                        blank=True, validators=[django.core.validators.MaxLengthValidator(1200)]
                    ),
                ),
                (
                    "tipping",
                    models.TextField(
                        blank=True, validators=[django.core.validators.MaxLengthValidator(1200)]
                    ),
                ),
                (
                    "atm_notes",
                    models.TextField(
                        blank=True, validators=[django.core.validators.MaxLengthValidator(1200)]
                    ),
                ),
                (
                    "dcc_warning",
                    models.TextField(
                        blank=True, validators=[django.core.validators.MaxLengthValidator(1200)]
                    ),
                ),
                ("source_name", models.CharField(blank=True, max_length=200)),
                ("source_url", models.URLField(blank=True, max_length=700)),
                (
                    "source_notes",
                    models.TextField(
                        blank=True, validators=[django.core.validators.MaxLengthValidator(2000)]
                    ),
                ),
                ("verified_at", models.DateTimeField(blank=True, null=True)),
                ("is_published", models.BooleanField(db_index=True, default=False)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "country",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="cultural_profile",
                        to="countries.country",
                    ),
                ),
            ],
            options={"ordering": ("country__name",)},
        ),
        migrations.CreateModel(
            name="TypicalPrice",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("city", models.CharField(blank=True, max_length=120)),
                (
                    "category",
                    models.CharField(
                        choices=[
                            ("coffee", "Coffee"),
                            ("casual_meal", "Casual meal"),
                            ("transit", "Transit"),
                            ("groceries", "Groceries"),
                            ("other", "Other"),
                        ],
                        max_length=24,
                    ),
                ),
                ("label", models.CharField(max_length=160)),
                ("amount_low", models.DecimalField(decimal_places=2, max_digits=12)),
                (
                    "amount_high",
                    models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
                ),
                ("source_name", models.CharField(max_length=200)),
                ("source_url", models.URLField(max_length=700)),
                ("observed_at", models.DateField()),
                ("verified_at", models.DateTimeField(blank=True, null=True)),
                (
                    "source_class",
                    models.CharField(
                        choices=[
                            ("authoritative", "Authoritative"),
                            ("curated_factual", "Curated factual"),
                            ("approximate_contextual", "Approximate contextual"),
                        ],
                        default="approximate_contextual",
                        max_length=24,
                    ),
                ),
                (
                    "confidence",
                    models.CharField(
                        choices=[("low", "Low"), ("medium", "Medium"), ("high", "High")],
                        default="medium",
                        max_length=12,
                    ),
                ),
                (
                    "notes",
                    models.TextField(
                        blank=True, validators=[django.core.validators.MaxLengthValidator(1200)]
                    ),
                ),
                ("display_order", models.PositiveSmallIntegerField(default=100)),
                ("is_published", models.BooleanField(db_index=True, default=False)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "country",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="typical_prices",
                        to="countries.country",
                    ),
                ),
                (
                    "currency",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="typical_prices",
                        to="countries.currency",
                    ),
                ),
            ],
            options={
                "ordering": ("display_order", "city", "label", "pk"),
                "constraints": [
                    models.CheckConstraint(
                        condition=models.Q(("amount_low__gt", 0)),
                        name="typical_price_low_positive",
                    ),
                    models.CheckConstraint(
                        condition=models.Q(
                            ("amount_high__isnull", True),
                            ("amount_high__gte", models.F("amount_low")),
                            _connector="OR",
                        ),
                        name="typical_price_range_ordered",
                    ),
                    models.UniqueConstraint(
                        fields=("country", "city", "category", "label", "observed_at"),
                        name="typical_price_observation_identity",
                    ),
                ],
            },
        ),
    ]
