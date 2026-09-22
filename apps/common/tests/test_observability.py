from __future__ import annotations

import json
import logging
from uuid import UUID

from django.test import SimpleTestCase

from apps.common.observability import (
    JsonFormatter,
    bind_request_id,
    get_request_id,
    normalize_request_id,
    redact_log_text,
    reset_request_id,
)


class RequestCorrelationTests(SimpleTestCase):
    def test_missing_request_id_is_generated_and_returned(self) -> None:
        response = self.client.get("/health/live/")

        request_id = response["X-Request-ID"]
        UUID(request_id)
        self.assertIsNone(get_request_id())

    def test_valid_incoming_request_id_is_preserved(self) -> None:
        response = self.client.get(
            "/health/live/",
            headers={"X-Request-ID": "client-request_123.abc"},
        )

        self.assertEqual(response["X-Request-ID"], "client-request_123.abc")
        self.assertIsNone(get_request_id())

    def test_invalid_or_oversized_request_id_is_replaced(self) -> None:
        for invalid in ("contains spaces", "x" * 65, "/path-like", ""):
            with self.subTest(invalid=invalid):
                response = self.client.get(
                    "/health/live/",
                    headers={"X-Request-ID": invalid},
                )

                replacement = response["X-Request-ID"]
                self.assertNotEqual(replacement, invalid)
                UUID(replacement)

    def test_access_log_excludes_query_string_and_request_body(self) -> None:
        with self.assertLogs("cultural_currency.access", level="INFO") as captured:
            query_response = self.client.get("/health/live/?token=private-query-value")
            body_response = self.client.post(
                "/health/live/",
                data={"private_note": "private-body-value"},
            )

        self.assertEqual(query_response.status_code, 200)
        self.assertEqual(body_response.status_code, 405)

        records = captured.records
        self.assertEqual(len(records), 2)

        for record in records:
            self.assertEqual(record.path, "/health/live/")
            self.assertNotIn("private-query-value", record.getMessage())
            self.assertNotIn("private-body-value", record.getMessage())
            self.assertTrue(record.request_id)
            self.assertGreaterEqual(record.duration_ms, 0)

        self.assertEqual(records[0].route, "health_live")
        self.assertEqual(records[0].status_code, 200)
        self.assertEqual(records[1].route, "health_live")
        self.assertEqual(records[1].status_code, 405)


class RequestIdHelperTests(SimpleTestCase):
    def test_normalizer_accepts_bounded_opaque_identifier(self) -> None:
        self.assertEqual(normalize_request_id("abc-123_DEF.xyz"), "abc-123_DEF.xyz")

    def test_normalizer_rejects_invalid_identifier(self) -> None:
        generated = normalize_request_id("bad value")

        UUID(generated)


class JsonFormatterTests(SimpleTestCase):
    def test_redactor_removes_common_secret_forms_without_destroying_safe_urls(self) -> None:
        value = (
            "GET https://user:db-pass@example.test/data?"
            "wskey=europeana-key&api_key=gemini-key "
            "Authorization: Bearer bearer-secret token=session-secret "
            "safe=https://example.test/public"
        )

        redacted = redact_log_text(value)

        for secret in (
            "user",
            "db-pass",
            "europeana-key",
            "gemini-key",
            "bearer-secret",
            "session-secret",
        ):
            self.assertNotIn(secret, redacted)
        self.assertIn("https://[REDACTED]@example.test/data", redacted)
        self.assertIn("wskey=[REDACTED]", redacted)
        self.assertIn("api_key=[REDACTED]", redacted)
        self.assertIn("Bearer [REDACTED]", redacted)
        self.assertIn("token=[REDACTED]", redacted)
        self.assertIn("safe=https://example.test/public", redacted)

    def test_formatter_redacts_event_and_exception_text(self) -> None:
        try:
            raise RuntimeError(
                "provider failed at "
                "https://user:password@example.test/v1?api_key=top-secret "
                "Authorization: Bearer access-secret"
            )
        except RuntimeError:
            exc_info = __import__("sys").exc_info()

        record = logging.LogRecord(
            name="cultural_currency.exchange",
            level=logging.ERROR,
            pathname=__file__,
            lineno=1,
            msg="request token=event-secret failed",
            args=(),
            exc_info=exc_info,
        )
        record.path = "/conversion/explain/"

        payload = json.loads(JsonFormatter().format(record))
        serialized = json.dumps(payload)

        for secret in (
            "password",
            "top-secret",
            "access-secret",
            "event-secret",
        ):
            self.assertNotIn(secret, serialized)
        self.assertEqual(payload["event"], "request token=[REDACTED] failed")
        self.assertEqual(payload["path"], "/conversion/explain/")
        self.assertIn("[REDACTED]", payload["exception"])

    def test_formatter_emits_stable_machine_readable_fields(self) -> None:
        token = bind_request_id("request-42")
        try:
            record = logging.LogRecord(
                name="cultural_currency.access",
                level=logging.INFO,
                pathname=__file__,
                lineno=1,
                msg="http_request",
                args=(),
                exc_info=None,
            )
            record.method = "GET"
            record.path = "/health/live/"
            record.route = "health_live"
            record.status_code = 200
            record.duration_ms = 1.25

            payload = json.loads(JsonFormatter().format(record))
        finally:
            reset_request_id(token)

        self.assertEqual(payload["level"], "INFO")
        self.assertEqual(payload["logger"], "cultural_currency.access")
        self.assertEqual(payload["service"], "cultural-currency-converter")
        self.assertEqual(payload["request_id"], "request-42")
        self.assertEqual(payload["event"], "http_request")
        self.assertEqual(payload["method"], "GET")
        self.assertEqual(payload["path"], "/health/live/")
        self.assertEqual(payload["route"], "health_live")
        self.assertEqual(payload["status_code"], 200)
        self.assertEqual(payload["duration_ms"], 1.25)
        self.assertIn("timestamp", payload)
        self.assertNotIn("query", payload)
        self.assertNotIn("body", payload)
