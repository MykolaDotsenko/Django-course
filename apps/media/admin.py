from __future__ import annotations

from django.contrib import admin, messages

from apps.media.models import MediaAsset
from apps.media.services import (
    MediaPublicationError,
    approve_media_asset,
    publish_media_asset,
    reject_media_asset,
    retire_media_asset,
)


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
        "storage_file",
        "content_hash",
        "width",
        "height",
        "aspect_ratio",
        "status",
        "reviewed_at",
        "published_at",
        "created_at",
        "updated_at",
    )
    autocomplete_fields = ("country", "currency", "derivative_of")
    actions = (
        "approve_selected",
        "publish_selected",
        "retire_selected",
        "reject_selected",
    )

    @admin.action(description="Approve selected media")
    def approve_selected(self, request, queryset):
        self._run_transition(request, queryset, approve_media_asset, "approved")

    @admin.action(description="Publish selected approved media")
    def publish_selected(self, request, queryset):
        self._run_transition(request, queryset, publish_media_asset, "published")

    @admin.action(description="Retire selected published media")
    def retire_selected(self, request, queryset):
        self._run_transition(request, queryset, retire_media_asset, "retired")

    @admin.action(description="Reject selected unpublished media")
    def reject_selected(self, request, queryset):
        self._run_transition(request, queryset, reject_media_asset, "rejected")

    def _run_transition(self, request, queryset, transition, label: str) -> None:
        succeeded = 0
        failures: list[str] = []
        for asset in queryset:
            try:
                transition(asset)
                succeeded += 1
            except MediaPublicationError as exc:
                failures.append(f"{asset.pk}: {exc}")

        if succeeded:
            self.message_user(
                request,
                f"{succeeded} media asset(s) {label}.",
                level=messages.SUCCESS,
            )
        if failures:
            self.message_user(
                request,
                "Skipped assets: " + " | ".join(failures[:8]),
                level=messages.WARNING,
            )
