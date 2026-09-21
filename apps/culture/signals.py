from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from apps.culture.models import StoryMoment, StoryMomentStatus

_PROTECTED_STATUSES = {StoryMomentStatus.PUBLISHED, StoryMomentStatus.RETIRED}
_MUTATING_ACTIONS = {"pre_add", "pre_remove", "pre_clear"}


@receiver(m2m_changed, sender=StoryMoment.countries.through)
@receiver(m2m_changed, sender=StoryMoment.currencies.through)
def protect_published_story_relations(
    sender,
    instance: StoryMoment,
    action: str,
    **kwargs,
) -> None:
    if action in _MUTATING_ACTIONS and instance.status in _PROTECTED_STATUSES:
        raise ValidationError(
            "Published or retired story relationships are immutable; create a new reviewed "
            "story version instead."
        )
