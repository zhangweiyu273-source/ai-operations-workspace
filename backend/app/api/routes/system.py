from fastapi import APIRouter, HTTPException, status

from app.core.config import get_settings
from app.db.session import engine
from app.schemas.health import SystemStatusResponse
from app.services.health import DatabaseUnavailableError, check_database

router = APIRouter()


@router.get("", response_model=SystemStatusResponse)
def system_status() -> SystemStatusResponse:
    settings = get_settings()
    try:
        database_status = check_database(engine)
    except DatabaseUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="database unavailable",
        ) from exc
    return SystemStatusResponse(
        name=settings.app_name,
        version=settings.app_version,
        environment=settings.app_env,
        database=database_status,
    )
