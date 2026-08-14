from datetime import date
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.ai_analysis import AIAnalysis


class AIAnalysisRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, analysis: AIAnalysis) -> AIAnalysis:
        self.session.add(analysis)
        return analysis

    def get(self, organization_id: UUID, analysis_id: UUID) -> AIAnalysis | None:
        return self.session.scalar(select(AIAnalysis).where(AIAnalysis.id == analysis_id, AIAnalysis.organization_id == organization_id, AIAnalysis.is_deleted.is_(False)))

    def list(self, organization_id: UUID, *, page: int, page_size: int, analysis_type: str | None = None) -> tuple[list[AIAnalysis], int]:
        filters = [AIAnalysis.organization_id == organization_id, AIAnalysis.is_deleted.is_(False)]
        if analysis_type:
            filters.append(AIAnalysis.analysis_type == analysis_type)
        total = self.session.scalar(select(func.count(AIAnalysis.id)).where(*filters)) or 0
        items = list(self.session.scalars(select(AIAnalysis).where(*filters).order_by(AIAnalysis.created_at.desc()).offset((page - 1) * page_size).limit(page_size)))
        return items, total

    def soft_delete(self, analysis: AIAnalysis) -> None:
        analysis.is_deleted = True

