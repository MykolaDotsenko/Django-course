from __future__ import annotations

import re

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.exchange.ai.evals import RUNTIME_EXPLANATION_EVAL_CASES
from apps.exchange.ai.packets import build_explanation_packet
from apps.exchange.ai.providers.gemini import GeminiExplanationDrafter
from apps.exchange.ai.validation import ExplanationValidationError, validate_provider_payload
from integrations.gemini.client import GeminiStructuredClient
from integrations.gemini.errors import AIProviderError

_MODEL_RE = re.compile(r"^gemini-[a-z0-9][a-z0-9.-]{1,78}$")


class Command(BaseCommand):
    help = (
        "Validate the versioned runtime-explanation eval set. By default this is offline and "
        "uses stored outputs. --live explicitly calls Gemini and never runs in normal CI."
    )

    def add_arguments(self, parser):
        parser.add_argument("--live", action="store_true")
        parser.add_argument(
            "--model",
            action="append",
            dest="models",
            help=(
                "Gemini model to evaluate. Repeat to compare models. "
                "Defaults to the configured runtime model."
            ),
        )

    def handle(self, *args, **options):
        live = bool(options["live"])
        models = options["models"] or [settings.AI_TEXT_MODEL]
        for model in models:
            if not _MODEL_RE.fullmatch(model):
                raise CommandError(f"Invalid Gemini model identifier: {model}")

        if not live:
            self._run_offline()
            return

        if not settings.GEMINI_API_KEY:
            raise CommandError("GEMINI_API_KEY is required for --live evaluation.")

        for model in models:
            self._run_live(model)

    def _run_offline(self) -> None:
        failures: list[str] = []
        for case in RUNTIME_EXPLANATION_EVAL_CASES:
            packet = build_explanation_packet(case.snapshot)
            try:
                validate_provider_payload(case.stored_output, packet=packet)
            except ExplanationValidationError as exc:
                failures.append(f"{case.id}: {exc}")

        if failures:
            raise CommandError("Offline eval failures: " + " | ".join(failures))

        self.stdout.write(
            self.style.SUCCESS(
                f"OFFLINE PASS: {len(RUNTIME_EXPLANATION_EVAL_CASES)} runtime explanation cases"
            )
        )

    def _run_live(self, model: str) -> None:
        client = GeminiStructuredClient(
            api_key=settings.GEMINI_API_KEY,
            timeout_seconds=settings.AI_TIMEOUT_SECONDS,
            max_attempts=settings.AI_MAX_ATTEMPTS,
        )
        drafter = GeminiExplanationDrafter(client=client, model=model)
        failures: list[str] = []

        for case in RUNTIME_EXPLANATION_EVAL_CASES:
            packet = build_explanation_packet(case.snapshot)
            try:
                candidate = drafter.draft(packet)
                validate_provider_payload(candidate.payload, packet=packet)
            except (AIProviderError, ExplanationValidationError) as exc:
                failures.append(f"{case.id}: {exc}")

        if failures:
            raise CommandError(f"LIVE FAIL [{model}]: " + " | ".join(failures))

        self.stdout.write(
            self.style.SUCCESS(
                f"LIVE PASS [{model}]: {len(RUNTIME_EXPLANATION_EVAL_CASES)} cases"
            )
        )
