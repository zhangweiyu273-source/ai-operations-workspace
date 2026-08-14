from datetime import date
from uuid import UUID

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.exceptions import AppError
from app.db.base import Base
from app.models import AIAnalysis, Account, Organization, Topic
from app.schemas.ai import AIAnalysisCreate, AIResponse
from app.services.ai_analysis_service import AIAnalysisService
from app.ai.prompts import get_prompt

ORG = UUID("00000000-0000-4000-8000-0000000000ab")

class FakeAIService:
    def generate(self, organization_id, *, feature, messages, temperature, max_tokens):
        assert organization_id == ORG and feature == "operation_analysis"
        return AIResponse(provider="fake", model="fake-model", content='{"title":"运营分析","summary":"基于测试数据的摘要","key_findings":["事实：播放为 10"],"positive_signals":[],"risks":[],"possible_causes":["假设：需要更多数据"],"recommendations":["建议：继续观察"],"next_actions":["核验数据"],"data_limitations":["样本有限"],"confidence":"中"}')

@pytest.fixture
def session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    with sessionmaker(bind=engine, expire_on_commit=False)() as value:
        value.add(Organization(id=ORG, name="测试组织")); value.commit(); yield value

def test_analysis_context_is_aggregated_and_bounded(session: Session) -> None:
    service = AIAnalysisService(session)
    context = service.context_builder.build(ORG, analysis_type="operation", date_start=None, date_end=None, account_ids=None, platform=None)
    assert context["metrics"]["content_count"] == 0
    assert context["top_content"] == [] and context["context_version"] == "v1"

def test_analysis_persists_and_soft_deletes_result(session: Session) -> None:
    service = AIAnalysisService(session); service.ai_service = FakeAIService()
    created = service.create(ORG, AIAnalysisCreate(analysis_type="operation", date_start=date(2026, 8, 1), date_end=date(2026, 8, 14)))
    row = session.scalar(select(AIAnalysis).where(AIAnalysis.id == created.id))
    assert row is not None and row.result_json["confidence"] == "中" and row.prompt_version == "v1"
    assert service.list(ORG, page=1, page_size=20, analysis_type="operation").total == 1
    service.delete(ORG, created.id)
    assert row.is_deleted is True and service.list(ORG, page=1, page_size=20, analysis_type=None).total == 0

def test_analysis_rejects_invalid_range_and_invalid_model_structure(session: Session) -> None:
    service = AIAnalysisService(session); service.ai_service = FakeAIService()
    with pytest.raises(AppError) as date_error: service.create(ORG, AIAnalysisCreate(analysis_type="operation", date_start=date(2026, 8, 2), date_end=date(2026, 8, 1)))
    assert date_error.value.code == "INVALID_DATE_RANGE"
    with pytest.raises(AppError) as json_error: service._parse_result("not-json")
    assert json_error.value.code == "AI_ANALYSIS_INVALID_RESPONSE"

def test_analysis_type_uses_a_versioned_specialized_prompt() -> None:
    content_prompt, version = get_prompt("content")
    keyword_prompt, _ = get_prompt("keyword")
    assert version == "v1" and "内容表现" in content_prompt and "关键词" in keyword_prompt
