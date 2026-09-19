"""URL configuration for Cultural Currency Converter."""

from django.contrib import admin
from django.urls import path

from apps.common.views import media_preview

urlpatterns = [
    path("admin/", admin.site.urls),
    path("_design/media/", media_preview, name="media_preview"),
]
