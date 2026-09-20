# Generated for the PR3 country/currency domain foundation.

import django.db.models.deletion
from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Country",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("iso2", models.CharField(max_length=2, unique=True)),
                ("iso3", models.CharField(max_length=3, unique=True)),
                ("name", models.CharField(max_length=120)),
                ("official_name", models.CharField(blank=True, max_length=180)),
                ("capital", models.CharField(blank=True, max_length=120)),
                ("region", models.CharField(blank=True, max_length=80)),
                ("subregion", models.CharField(blank=True, max_length=120)),
                ("flag_url", models.URLField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
                ("metadata_source", models.CharField(blank=True, max_length=80)),
                ("metadata_fetched_at", models.DateTimeField(blank=True, null=True)),
                ("metadata_verified_at", models.DateTimeField(blank=True, null=True)),
            ],
            options={"ordering": ("name", "iso2")},
        ),
        migrations.CreateModel(
            name="Currency",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(max_length=3, unique=True)),
                ("name", models.CharField(max_length=120)),
                ("symbol", models.CharField(blank=True, max_length=16)),
                ("minor_units", models.PositiveSmallIntegerField(default=2)),
                ("is_active", models.BooleanField(default=True)),
                ("active_from", models.DateField(blank=True, null=True)),
                ("active_to", models.DateField(blank=True, null=True)),
            ],
            options={"ordering": ("code",)},
        ),
        migrations.CreateModel(
            name="CountryCurrency",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("is_primary", models.BooleanField(default=False)),
                ("valid_from", models.DateField(blank=True, null=True)),
                ("valid_to", models.DateField(blank=True, null=True)),
                ("usage_role", models.CharField(blank=True, max_length=80)),
                ("source", models.CharField(max_length=160)),
                ("country", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="currency_links", to="countries.country")),
                ("currency", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="country_links", to="countries.currency")),
            ],
            options={"ordering": ("country__name", "-is_primary", "currency__code")},
        ),
        migrations.AddConstraint(
            model_name="countrycurrency",
            constraint=models.CheckConstraint(
                condition=Q(("valid_from__isnull", True), ("valid_to__isnull", True), ("valid_to__gte", models.F("valid_from")), _connector="OR"),
                name="country_currency_valid_date_range",
            ),
        ),
        migrations.AddConstraint(
            model_name="countrycurrency",
            constraint=models.UniqueConstraint(
                condition=Q(("valid_to__isnull", True)),
                fields=("country", "currency"),
                name="unique_active_country_currency",
            ),
        ),
        migrations.AddConstraint(
            model_name="countrycurrency",
            constraint=models.UniqueConstraint(
                condition=Q(("is_primary", True), ("valid_to__isnull", True)),
                fields=("country",),
                name="unique_active_primary_currency_per_country",
            ),
        ),
    ]
