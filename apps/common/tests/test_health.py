from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

from django.db import DatabaseError
from django.test import SimpleTestCase, TestCase, override_settings


class HealthLivenessTests(SimpleTestCase):
    def test_liveness_is_healthy_without_database_access(self) -> None:
        response = self.client.get("/health/live/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_liveness_supports_head(self) -> None:
        response = self.client.head("/health/live/")

        self.assertEqual(response.status_code, 200)


class HealthReadinessTests(TestCase):
    @override_settings(CACHE_CONFIG=SimpleNamespace(shared=False))
    def test_readiness_checks_database_connectivity(self) -> None:
        response = self.client.get("/health/ready/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "status": "ok",
                "checks": {"database": "ok"},
            },
        )

    @patch("apps.common.health.connection.cursor")
    def test_readiness_returns_503_without_database_exception_details(self, cursor) -> None:
        cursor.side_effect = DatabaseError("postgresql://user:secret@private-host/db")

        response = self.client.get("/health/ready/")

        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.json(),
            {
                "status": "unavailable",
                "checks": {"database": "unavailable"},
            },
        )
        self.assertNotContains(response, "secret", status_code=503)
        self.assertNotContains(response, "private-host", status_code=503)

    @override_settings(CACHE_CONFIG=SimpleNamespace(shared=True))
    @patch("apps.common.health.cache.delete")
    @patch("apps.common.health.cache.get")
    @patch("apps.common.health.cache.set")
    def test_readiness_reports_shared_cache_when_available(
        self,
        cache_set,
        cache_get,
        cache_delete,
    ) -> None:
        cache_get.side_effect = lambda key: cache_set.call_args.args[1]

        response = self.client.get("/health/ready/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "status": "ok",
                "checks": {
                    "database": "ok",
                    "cache": "ok",
                },
            },
        )
        cache_set.assert_called_once()
        key, marker = cache_set.call_args.args
        self.assertTrue(key.startswith("health:readiness:"))
        self.assertTrue(marker)
        self.assertEqual(cache_set.call_args.kwargs, {"timeout": 5})
        cache_get.assert_called_once_with(key)
        cache_delete.assert_called_once_with(key)

    @override_settings(CACHE_CONFIG=SimpleNamespace(shared=True))
    @patch("apps.common.health.cache.set", side_effect=RuntimeError("redis unavailable"))
    def test_cache_outage_is_degraded_but_does_not_remove_readiness(self, cache_set) -> None:
        with self.assertLogs("cultural_currency.health", level="WARNING") as captured:
            response = self.client.get("/health/ready/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "status": "degraded",
                "checks": {
                    "database": "ok",
                    "cache": "unavailable",
                },
            },
        )
        record = next(record for record in captured.records if record.msg == "readiness_degraded")
        self.assertEqual(record.dependency, "cache")
        self.assertEqual(record.outcome, "degraded")
        self.assertEqual(record.error_code, "cache_unavailable")
        cache_set.assert_called_once()

    @override_settings(CACHE_CONFIG=SimpleNamespace(shared=True))
    @patch("apps.common.health.cache.set")
    @patch("apps.common.health.connection.cursor")
    def test_database_failure_remains_hard_unready_without_cache_probe(
        self,
        cursor,
        cache_set,
    ) -> None:
        cursor.side_effect = DatabaseError("database unavailable")

        response = self.client.get("/health/ready/")

        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.json(),
            {
                "status": "unavailable",
                "checks": {"database": "unavailable"},
            },
        )
        cache_set.assert_not_called()
