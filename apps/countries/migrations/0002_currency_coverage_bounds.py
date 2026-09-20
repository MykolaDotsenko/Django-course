# Generated for PR6B historical lifecycle/provider coverage separation.

import django.db.models.expressions
from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):
    dependencies = [
        ("countries", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="currency",
            name="coverage_from",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="currency",
            name="coverage_to",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="currency",
            name="coverage_source",
            field=models.CharField(blank=True, max_length=80),
        ),
        migrations.AddField(
            model_name="currency",
            name="coverage_fetched_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="currency",
            name="coverage_to_is_terminal",
            field=models.BooleanField(default=False),
        ),
        migrations.AddConstraint(
            model_name="currency",
            constraint=models.CheckConstraint(
                condition=Q(active_from__isnull=True)
                | Q(active_to__isnull=True)
                | Q(active_to__gte=django.db.models.expressions.F("active_from")),
                name="currency_active_date_range",
            ),
        ),
        migrations.AddConstraint(
            model_name="currency",
            constraint=models.CheckConstraint(
                condition=Q(coverage_from__isnull=True)
                | Q(coverage_to__isnull=True)
                | Q(coverage_to__gte=django.db.models.expressions.F("coverage_from")),
                name="currency_coverage_date_range",
            ),
        ),
    ]
