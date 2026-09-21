from django.apps import AppConfig


class CultureConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.culture"
    verbose_name = "Money and culture"

    def ready(self) -> None:
        import apps.culture.signals  # noqa: F401
