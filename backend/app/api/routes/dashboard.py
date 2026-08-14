from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_organization_id
from app.db.session import get_db
from app.schemas.dashboard import DashboardResponse
from app.services.dashboard import DashboardService

router = APIRouter()
Db = Annotated[Session, Depends(get_db)]
Org = Annotated[UUID, Depends(get_current_organization_id)]


@router.get("", response_model=DashboardResponse)
def get_dashboard(session: Db, organization_id: Org) -> DashboardResponse:
    return DashboardService(session).get(organization_id)
