import json
import logging
from datetime import date
from uuid import UUID

from sqlalchemy.orm import Session

from app.ai.prompts import get_prompt
from app.ai.prompts.operation_analysis import build_prompt
from app.core.exceptions import AppError
from app.models.ai_analysis import AIAnalysis
from app.repositories.ai_analysis import AIAnalysisRepository
from app.schemas.ai import AIAnalysisCreate, AIAnalysisList, AIAnalysisResponse, AIMessage
from app.services.ai_service import AIService
from app.services.analysis_context import CONTEXT_VERSION, AnalysisContextBuilder

logger = logging.getLogger(__name__)


class AIAnalysisService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = AIAnalysisRepository(session)
        self.context_builder = AnalysisContextBuilder(session)
        self.ai_service = AIService(session)

    def create(self, organization_id: UUID, data: AIAnalysisCreate) -> AIAnalysisResponse:
        if data.date_start and data.date_end and data.date_start > data.date_end:
            raise AppError("date_start must be before date_end", 422, "INVALID_DATE_RANGE")
        context = self.context_builder.build(organization_id, analysis_type=data.analysis_type, date_start=data.date_start, date_end=data.date_end, account_ids=data.account_ids, platform=data.platform)
        system_prompt, prompt_version = get_prompt(data.analysis_type)
        response = self.ai_service.generate(organization_id, feature=f"{data.analysis_type}_analysis", messages=[AIMessage(role="system", content=system_prompt), AIMessage(role="user", content=build_prompt(context))], temperature=0.2, max_tokens=1200)
        result = self._parse_result(response.content)
        title = str(result.get("title") or self._title(data.analysis_type))[:255]
        summary = str(result.get("summary") or "模型未返回摘要。")
        analysis = AIAnalysis(organization_id=organization_id, analysis_type=data.analysis_type, title=title, date_start=data.date_start, date_end=data.date_end, summary=summary, result_json=result, provider=response.provider, model=response.model, prompt_version=prompt_version, context_version=CONTEXT_VERSION, status="completed")
        try:
            self.repository.add(analysis)
            self.session.commit()
            self.session.refresh(analysis)
        except Exception as exc:
            self.session.rollback()
            logger.exception("AI analysis persistence failed organization_id=%s type=%s", organization_id, data.analysis_type)
            raise AppError("Failed to save analysis result", 500, "AI_ANALYSIS_SAVE_FAILED") from exc
        return AIAnalysisResponse.model_validate(analysis)

    def list(self, organization_id: UUID, *, page: int, page_size: int, analysis_type: str | None) -> AIAnalysisList:
        items, total = self.repository.list(organization_id, page=page, page_size=page_size, analysis_type=analysis_type)
        return AIAnalysisList(items=[AIAnalysisResponse.model_validate(item) for item in items], total=total, page=page, page_size=page_size)

    def get(self, organization_id: UUID, analysis_id: UUID) -> AIAnalysisResponse:
        analysis = self.repository.get(organization_id, analysis_id)
        if not analysis:
            raise AppError("Analysis not found", 404, "AI_ANALYSIS_NOT_FOUND")
        return AIAnalysisResponse.model_validate(analysis)

    def delete(self, organization_id: UUID, analysis_id: UUID) -> None:
        analysis = self.repository.get(organization_id, analysis_id)
        if not analysis:
            raise AppError("Analysis not found", 404, "AI_ANALYSIS_NOT_FOUND")
        try:
            self.repository.soft_delete(analysis)
            self.session.commit()
        except Exception as exc:
            self.session.rollback()
            logger.exception("AI analysis deletion failed organization_id=%s analysis_id=%s", organization_id, analysis_id)
            raise AppError("Failed to delete analysis", 500, "AI_ANALYSIS_DELETE_FAILED") from exc

    @staticmethod
    def _title(analysis_type: str) -> str:
        return {"operation": "综合运营分析", "content": "内容表现分析", "keyword": "关键词分析", "topic": "选题分析", "task_review": "任务与复盘分析"}[analysis_type]

    @staticmethod
    def _parse_result(content: str) -> dict:
        value = content.strip()
        if value.startswith("```"):
            value = value.split("\n", 1)[1] if "\n" in value else value
            value = value.rsplit("```", 1)[0].strip()
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as exc:
            raise AppError("AI returned an invalid structured result", 502, "AI_ANALYSIS_INVALID_RESPONSE") from exc
        if not isinstance(parsed, dict):
            raise AppError("AI returned an invalid structured result", 502, "AI_ANALYSIS_INVALID_RESPONSE")
        for key in ("key_findings", "positive_signals", "risks", "possible_causes", "recommendations", "next_actions", "data_limitations"):
            parsed[key] = [str(item) for item in parsed.get(key, [])][:10] if isinstance(parsed.get(key, []), list) else []
        parsed["confidence"] = str(parsed.get("confidence") or "低")
        return parsed
