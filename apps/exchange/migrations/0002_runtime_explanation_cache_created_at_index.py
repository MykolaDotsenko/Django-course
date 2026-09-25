from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("exchange", "0001_runtime_explanation_cache"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="runtimeexplanationcache",
            index=models.Index(fields=["created_at"], name="fx_ai_created_at_idx"),
        ),
    ]
