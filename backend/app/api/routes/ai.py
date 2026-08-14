from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_organization_id
from app.db.session import get_db
from app.schemas.ai import AITestRequest, AIResponse, AIStatistics, AIStatusResponse, AIMessage
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
