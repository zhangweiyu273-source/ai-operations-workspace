from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class AIMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(min_length=1, max_length=20_000)


class AIUsage(BaseModel):
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None


class AIResponse(BaseModel):
    provider: str
    model: str
    content: str
    usage: AIUsage | None = None
    latency_ms: int | None = None
    request_id: str | None = None
    status: Literal["success"] = "success"


class AITestRequest(BaseModel):
    message: str = Field(min_length=1, max_length=500)


class AIStatusResponse(BaseModel):
    configured: bool
    provider: str
    model: str | None
    provider_status: Literal["configured", "not_configured", "unsupported"]


class AIStatistics(BaseModel):
    today_calls: int
    success_count: int
    failure_count: int
    total_tokens: int
    average_latency_ms: float | None


AnalysisType = Literal["operation", "content", "keyword", "topic", "task_review"]

class AIAnalysisCreate(BaseModel):
    analysis_type: AnalysisType
    date_start: date | None = None
    date_end: date | None = None
    account_ids: list[UUID] = Field(default_factory=list, max_length=20)
    platform: str | None = Field(default=None, max_length=30)

class AIAnalysisResult(BaseModel):
    key_findings: list[str] = Field(default_factory=list)
    positive_signals: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    possible_causes: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)
    data_limitations: list[str] = Field(default_factory=list)
    confidence: str = "低"

class AIAnalysisResponse(BaseModel):
    id: UUID
    analysis_type: AnalysisType
    title: str
    date_start: date | None
    date_end: date | None
    summary: str
    result_json: dict
    provider: str
    model: str
    prompt_version: str
    context_version: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}

class AIAnalysisList(BaseModel):
    items: list[AIAnalysisResponse]
    total: int
    page: int
    page_size: int
