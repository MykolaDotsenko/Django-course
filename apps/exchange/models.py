from __future__ import annotations

from django.db import models


class RuntimeExplanationCache(models.Model):
    cache_key = models.CharField(max_length=64, primary_key=True)
    packet_hash = models.CharField(max_length=64, db_index=True)
    prompt_version = models.CharField(max_length=80)
    schema_version = models.CharField(max_length=80)
    provider = models.CharField(max_length=40)
    model = models.CharField(max_length=120)
    provider_model_version = models.CharField(max_length=160, blank=True)
    locale = models.CharField(max_length=16, default="en")
    result = models.JSONField()
    input_tokens = models.PositiveIntegerField(null=True, blank=True)
    output_tokens = models.PositiveIntegerField(null=True, blank=True)
    total_tokens = models.PositiveIntegerField(null=True, blank=True)
    provider_response_id = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(
                fields=("prompt_version", "model", "locale"),
                name="fx_ai_prompt_model_idx",
            )
        ]

    def __str__(self) -> str:
        return f"{self.model} · {self.packet_hash[:12]}"
