import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("countries", "0002_currency_coverage_bounds"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="FavouritePair",
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
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
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
                        related_name="favourite_pairs",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ("-updated_at", "-id"),
                "indexes": [
                    models.Index(
                        fields=["user", "-updated_at"],
                        name="travel_fav_user_updated_idx",
                    )
                ],
                "constraints": [
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
                ],
            },
        ),
    ]
