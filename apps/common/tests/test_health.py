from __future__ import annotations

from unittest.mock import patch

from django.db import DatabaseError
from django.test import SimpleTestCase, TestCase


class HealthLivenessTests(SimpleTestCase):
    def test_liveness_is_healthy_without_database_access(self) -> None:
        response = self.client.get("/health/live/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_liveness_supports_head(self) -> None:
        response = self.client.head("/health/live/")

        self.assertEqual(response.status_code, 200)


class HealthReadinessTests(TestCase):
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
