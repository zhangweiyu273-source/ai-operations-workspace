import os
from urllib.parse import urlparse

import pytest
from sqlalchemy import create_engine, inspect, text


def test_database_connection_and_migrated_schema() -> None:
    database_url = os.getenv("TEST_DATABASE_URL")
    if not database_url:
        pytest.skip("TEST_DATABASE_URL is required for PostgreSQL integration test")

    database_name = urlparse(database_url.replace("postgresql+psycopg", "postgresql")).path.lstrip("/")
    assert database_name.endswith("_test"), "TEST_DATABASE_URL must point to a *_test database"
    development_url = os.getenv("DATABASE_URL")
    if development_url:
        assert database_url != development_url, "test and development database URLs must differ"

    engine = create_engine(database_url, pool_pre_ping=True)
    try:
        with engine.connect() as connection:
            assert connection.execute(text("SELECT 1")).scalar_one() == 1
            assert (
                connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one()
                == "20260814_0009"
            )

        table_names = set(inspect(engine).get_table_names())
        assert {
            "accounts",
            "operation_metrics",
            "keywords",
            "topics",
            "topic_keywords",
            "knowledge",
            "knowledge_tags",
            "operation_tasks",
            "operation_reviews",
            "ai_request_logs",
            "alembic_version",
            "organizations",
            "users",
        }.issubset(table_names)

        with engine.connect() as connection:
            assert (
                connection.execute(text("SELECT name FROM organizations")).scalar_one()
                == "默认组织"
            )
    finally:
        engine.dispose()
