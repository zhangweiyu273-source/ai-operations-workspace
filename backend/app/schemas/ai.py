from datetime import datetime
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
