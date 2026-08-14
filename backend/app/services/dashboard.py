from uuid import UUID

from sqlalchemy.orm import Session

from app.repositories.dashboard import DashboardRepository
from app.schemas.dashboard import DashboardResponse


class DashboardService:
    def __init__(self, session: Session) -> None:
        self.repository = DashboardRepository(session)

    def get(self, organization_id: UUID) -> DashboardResponse:
        return DashboardResponse.model_validate(self.repository.get(organization_id))
