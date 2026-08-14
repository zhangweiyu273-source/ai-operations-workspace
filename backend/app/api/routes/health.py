import logging

from fastapi import APIRouter, HTTPException, status

from app.core.config import get_settings
from app.db.session import engine
from app.schemas.health import LivenessResponse, ReadinessResponse
from app.services.health import DatabaseUnavailableError, check_database

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/live", response_model=LivenessResponse)
def liveness() -> LivenessResponse:
    settings = get_settings()
    return LivenessResponse(status="ok", service=settings.app_name, version=settings.app_version)


@router.get("/ready", response_model=ReadinessResponse)
def readiness() -> ReadinessResponse:
    try:
        database_status = check_database(engine)
    except DatabaseUnavailableError as exc:
        logger.warning("Database readiness check failed", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="database unavailable",
        ) from exc
    return ReadinessResponse(status="ok", database=database_status)
