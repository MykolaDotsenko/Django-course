from __future__ import annotations

from django.contrib import admin, messages

from apps.culture.models import StoryMoment
from apps.culture.services import (
    StoryPublicationError,
    approve_story_moment,
    publish_story_moment,
    reject_story_moment,
    retire_story_moment,
)


@admin.register(StoryMoment)
class StoryMomentAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "status",
        "relevance_weight",
        "start_date",
        "source_name",
        "verified_at",
    )
    list_filter = ("status", "category", "source_kind", "supports_causality")
    search_fields = ("title", "summary", "source_name", "external_id")
    filter_horizontal = ("countries", "currencies")
    readonly_fields = (
        "status",
        "reviewed_at",
        "published_at",
        "created_at",
        "updated_at",
    )
    actions = (
        "approve_selected",
        "publish_selected",
        "retire_selected",
        "reject_selected",
    )

    @admin.action(description="Approve selected story moments")
    def approve_selected(self, request, queryset):
        self._run_transition(request, queryset, approve_story_moment, "approved")

    @admin.action(description="Publish selected approved story moments")
    def publish_selected(self, request, queryset):
        self._run_transition(request, queryset, publish_story_moment, "published")

    @admin.action(description="Retire selected published story moments")
    def retire_selected(self, request, queryset):
        self._run_transition(request, queryset, retire_story_moment, "retired")

    @admin.action(description="Reject selected unpublished story moments")
    def reject_selected(self, request, queryset):
        self._run_transition(request, queryset, reject_story_moment, "rejected")

    def _run_transition(self, request, queryset, transition, label: str) -> None:
        succeeded = 0
        failures: list[str] = []
        for moment in queryset:
            try:
                transition(moment)
                succeeded += 1
            except StoryPublicationError as exc:
                failures.append(f"{moment.pk}: {exc}")

        if succeeded:
            self.message_user(
                request,
                f"{succeeded} story moment(s) {label}.",
                level=messages.SUCCESS,
            )
        if failures:
            self.message_user(
                request,
                "Skipped story moments: " + " | ".join(failures[:8]),
                level=messages.WARNING,
            )
