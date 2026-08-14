from fastapi import APIRouter

from app.api.routes.accounts import router as accounts_router
from app.api.routes.health import router as health_router
from app.api.routes.keywords import router as keywords_router
from app.api.routes.operation_metrics import router as operation_metrics_router
from app.api.routes.system import router as system_router

api_router = APIRouter()
api_router.include_router(accounts_router, prefix="/accounts", tags=["accounts"])
api_router.include_router(
    operation_metrics_router, prefix="/operation-metrics", tags=["operation-metrics"]
)
api_router.include_router(keywords_router, prefix="/keywords", tags=["keywords"])
api_router.include_router(health_router, prefix="/health", tags=["health"])
api_router.include_router(system_router, prefix="/system", tags=["system"])
