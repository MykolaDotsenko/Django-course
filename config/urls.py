"""URL configuration for Cultural Currency Converter."""

from django.contrib import admin
from django.urls import path

from apps.common.health import health_live, health_ready
from apps.common.views import converter_preview, media_preview, rate_series_preview, shell_preview
from apps.exchange.views import converter, historical_series, picker_options

urlpatterns = [
    path("", converter, name="converter"),
    path("picker/options/", picker_options, name="picker_options"),
    path("historical/series/", historical_series, name="historical_series"),
    path("health/live/", health_live, name="health_live"),
    path("health/ready/", health_ready, name="health_ready"),
    path("admin/", admin.site.urls),
    path("_design/media/", media_preview, name="media_preview"),
    path("_design/shell/", shell_preview, name="shell_preview"),
    path("_design/converter/", converter_preview, name="converter_preview"),
    path("_design/rate-series/", rate_series_preview, name="rate_series_preview"),
]
