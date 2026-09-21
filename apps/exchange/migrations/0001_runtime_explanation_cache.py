from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="RuntimeExplanationCache",
            fields=[
                ("cache_key", models.CharField(max_length=64, primary_key=True, serialize=False)),
                ("packet_hash", models.CharField(db_index=True, max_length=64)),
                ("prompt_version", models.CharField(max_length=80)),
                ("schema_version", models.CharField(max_length=80)),
                ("provider", models.CharField(max_length=40)),
                ("model", models.CharField(max_length=120)),
                ("provider_model_version", models.CharField(blank=True, max_length=160)),
                ("locale", models.CharField(default="en", max_length=16)),
                ("result", models.JSONField()),
                ("input_tokens", models.PositiveIntegerField(blank=True, null=True)),
                ("output_tokens", models.PositiveIntegerField(blank=True, null=True)),
                ("total_tokens", models.PositiveIntegerField(blank=True, null=True)),
                ("provider_response_id", models.CharField(blank=True, max_length=200)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ("-created_at",),
                "indexes": [
                    models.Index(
                        fields=["prompt_version", "model", "locale"],
                        name="fx_ai_prompt_model_idx",
                    )
                ],
            },
        ),
    ]
