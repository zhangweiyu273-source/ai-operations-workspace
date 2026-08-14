from sqlalchemy import Engine, text
from sqlalchemy.exc import SQLAlchemyError


class DatabaseUnavailableError(RuntimeError):
    pass


def check_database(db_engine: Engine) -> str:
    try:
        with db_engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        raise DatabaseUnavailableError("database unavailable") from exc
    return "connected"
