from app.core.config import Settings


def test_managed_postgres_url_uses_installed_psycopg_driver():
    settings = Settings(database_url="postgresql://user:password@internal-db:5432/ai_ops")

    assert settings.database_url == "postgresql+psycopg://user:password@internal-db:5432/ai_ops"


def test_existing_sqlalchemy_database_url_is_unchanged():
    database_url = "postgresql+psycopg://user:password@db:5432/ai_ops"

    assert Settings(database_url=database_url).database_url == database_url
