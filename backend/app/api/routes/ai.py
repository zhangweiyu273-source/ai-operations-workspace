from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_organization_id
from app.db.session import get_db
from app.schemas.ai import AITestRequest, AIResponse, AIStatistics, AIStatusResponse, AIMessage, AIAnalysisCreate, AIAnalysisList, AIAnalysisResponse, AnalysisType
from app.services.ai_analysis_service import AIAnalysisService
from app.services.ai_service import AIService

router = APIRouter()
Db = Annotated[Session, Depends(get_db)]
Org = Annotated[UUID, Depends(get_current_organization_id)]

@router.get("/status", response_model=AIStatusResponse)
def status(session: Db): return AIService(session).status()

@router.get("/statistics", response_model=AIStatistics)
def statistics(session: Db, organization_id: Org): return AIService(session).statistics(organization_id)

@router.post("/test", response_model=AIResponse)
def test_ai(data: AITestRequest, session: Db, organization_id: Org):
    return AIService(session).generate(organization_id, feature="connection_test", messages=[AIMessage(role="user", content=data.message)], temperature=0, max_tokens=100)

@router.get("/analysis/types")
def analysis_types():
    return {"items": [{"value": "operation", "label": "综合运营分析"}, {"value": "content", "label": "内容表现分析"}, {"value": "keyword", "label": "关键词分析"}, {"value": "topic", "label": "选题分析"}, {"value": "task_review", "label": "任务与复盘分析"}]}

@router.post("/analysis", response_model=AIAnalysisResponse)
def create_analysis(data: AIAnalysisCreate, session: Db, organization_id: Org):
    return AIAnalysisService(session).create(organization_id, data)

@router.get("/analysis", response_model=AIAnalysisList)
def list_analysis(session: Db, organization_id: Org, page: int = 1, page_size: int = 20, analysis_type: AnalysisType | None = None):
    return AIAnalysisService(session).list(organization_id, page=page, page_size=page_size, analysis_type=analysis_type)

@router.get("/analysis/{analysis_id}", response_model=AIAnalysisResponse)
def get_analysis(analysis_id: UUID, session: Db, organization_id: Org):
    return AIAnalysisService(session).get(organization_id, analysis_id)

@router.delete("/analysis/{analysis_id}", status_code=204)
def delete_analysis(analysis_id: UUID, session: Db, organization_id: Org):
    AIAnalysisService(session).delete(organization_id, analysis_id)
