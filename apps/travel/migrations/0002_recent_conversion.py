import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):
    dependencies = [
        ("travel", "0001_favourite_pair"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="RecentConversion",
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
                ("fingerprint", models.CharField(max_length=64)),
                ("input_amount", models.CharField(max_length=64)),
                ("output_amount", models.CharField(max_length=64)),
                (
                    "rate_mode",
                    models.CharField(
                        choices=[
                            ("latest", "Latest available"),
                            ("historical", "Historical"),
                        ],
                        max_length=10,
                    ),
                ),
                ("requested_date", models.DateField(blank=True, null=True)),
                ("effective_date", models.DateField()),
                ("converted_at", models.DateTimeField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "destination_country",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to="countries.country",
                    ),
                ),
                (
                    "destination_currency",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to="countries.currency",
                    ),
                ),
                (
                    "source_country",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to="countries.country",
                    ),
                ),
                (
                    "source_currency",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="+",
                        to="countries.currency",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="recent_conversions",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("-converted_at", "-id"),
                "indexes": [
                    models.Index(
                        fields=["user", "-converted_at"],
                        name="travel_recent_user_time_idx",
                    )
                ],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("user", "fingerprint"),
                        name="unique_user_recent_conversion",
                    ),
                    models.CheckConstraint(
                        condition=(
                            Q(rate_mode="historical", requested_date__isnull=False)
                            | Q(rate_mode="latest", requested_date__isnull=True)
                        ),
                        name="recent_requested_date_matches_mode",
                    ),
                ],
            },
        ),
    ]
