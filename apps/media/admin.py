from django.contrib import admin

from apps.media.models import MediaAsset


@admin.register(MediaAsset)
class MediaAssetAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "kind",
        "role",
        "source_kind",
        "status",
        "country",
        "currency",
        "published_at",
    )
    list_filter = ("status", "kind", "role", "source_kind", "generated_by_ai")
    search_fields = (
        "title",
        "caption",
        "source_name",
        "creator",
        "external_id",
        "content_hash",
    )
    readonly_fields = (
        "content_hash",
        "width",
        "height",
        "aspect_ratio",
        "created_at",
        "updated_at",
    )
    autocomplete_fields = ("country", "currency", "derivative_of")
