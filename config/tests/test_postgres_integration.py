from __future__ import annotations

import os

import pytest
from django.db import connection


@pytest.mark.django_db(transaction=True)
def test_postgresql_integration_lane_uses_real_postgresql() -> None:
    if not os.environ.get("DATABASE_URL"):
        pytest.skip("PostgreSQL integration assertion runs only when DATABASE_URL is configured.")

    assert connection.vendor == "postgresql"

    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        assert cursor.fetchone() == (1,)
