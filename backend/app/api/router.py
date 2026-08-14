from fastapi import APIRouter

from app.api.routes.accounts import router as accounts_router
from app.api.routes.dashboard import router as dashboard_router
from app.api.routes.health import router as health_router
from app.api.routes.keywords import router as keywords_router
from app.api.routes.knowledge import router as knowledge_router
from app.api.routes.operation_metrics import router as operation_metrics_router
from app.api.routes.operations import tasks, reviews
from app.api.routes.system import router as system_router
from app.api.routes.topics import router as topics_router

api_router = APIRouter()
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(accounts_router, prefix="/accounts", tags=["accounts"])
api_router.include_router(
    operation_metrics_router, prefix="/operation-metrics", tags=["operation-metrics"]
)
api_router.include_router(keywords_router, prefix="/keywords", tags=["keywords"])
api_router.include_router(knowledge_router, prefix="/knowledge", tags=["knowledge"])
api_router.include_router(topics_router, prefix="/topics", tags=["topics"])
api_router.include_router(tasks, prefix="/tasks", tags=["tasks"])
api_router.include_router(reviews, prefix="/reviews", tags=["reviews"])
api_router.include_router(health_router, prefix="/health", tags=["health"])
api_router.include_router(system_router, prefix="/system", tags=["system"])
