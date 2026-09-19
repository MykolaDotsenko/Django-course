"""URL configuration for Cultural Currency Converter."""

from django.contrib import admin
from django.urls import path

from apps.common.health import health_live, health_ready
from apps.common.views import media_preview, shell_preview

urlpatterns = [
    path("health/live/", health_live, name="health_live"),
    path("health/ready/", health_ready, name="health_ready"),
    path("admin/", admin.site.urls),
    path("_design/media/", media_preview, name="media_preview"),
    path("_design/shell/", shell_preview, name="shell_preview"),
]
