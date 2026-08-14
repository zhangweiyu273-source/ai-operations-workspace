from uuid import UUID

import httpx
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.ai.providers.base import AIProviderError, BaseAIProvider
from app.ai.providers.deepseek import DeepSeekProvider
from app.core.exceptions import AppError
from app.db.base import Base
from app.models import AIRequestLog, Organization
from app.schemas.ai import AIMessage, AIResponse, AIUsage
from app.services.ai_service import AIService
from app.main import app

ORG = UUID("00000000-0000-4000-8000-0000000000aa")

class FakeProvider(BaseAIProvider):
    name = "fake"
    def __init__(self, error: AIProviderError | None = None): self.error = error
    def configured(self): return True
    def chat(self, messages, *, temperature, max_tokens):
        if self.error: raise self.error
        return AIResponse(provider="fake", model="fake-model", content="ok", usage=AIUsage(prompt_tokens=2, completion_tokens=3, total_tokens=5), latency_ms=12)

@pytest.fixture
def session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool); Base.metadata.create_all(engine)
    with sessionmaker(bind=engine, expire_on_commit=False)() as value:
        value.add(Organization(id=ORG, name="AI测试组织")); value.commit(); yield value

def test_ai_service_records_success_and_failure_without_prompt_content(session: Session) -> None:
    service = AIService(session, provider=FakeProvider())
    result = service.generate(ORG, feature="connection_test", messages=[AIMessage(role="user", content="测试")])
    assert result.content == "ok"
    row = session.scalar(select(AIRequestLog)); assert row.status == "success" and row.total_tokens == 5 and not hasattr(row, "prompt")
    with pytest.raises(AppError) as error: AIService(session, provider=FakeProvider(AIProviderError("RATE_LIMITED", "hidden", True))).generate(ORG, feature="connection_test", messages=[AIMessage(role="user", content="测试")])
    assert error.value.code == "AI_RATE_LIMITED"
    assert session.scalars(select(AIRequestLog).where(AIRequestLog.status == "failed")).one().error_type == "RATE_LIMITED"

@pytest.mark.parametrize("status,error_type", [(401, "AUTHENTICATION"), (429, "RATE_LIMITED"), (503, "PROVIDER_UNAVAILABLE")])
def test_deepseek_provider_converts_http_errors(status: int, error_type: str) -> None:
    client = httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(status, request=request)))
    provider = DeepSeekProvider(api_key="test-key", base_url="https://example.invalid", model="test", timeout=1, max_retries=0, client=client)
    with pytest.raises(AIProviderError) as error: provider.chat([AIMessage(role="user", content="test")], temperature=0, max_tokens=10)
    assert error.value.error_type == error_type

def test_deepseek_provider_parses_response_and_timeout() -> None:
    def ok(request): return httpx.Response(200, json={"model": "deepseek-chat", "choices": [{"message": {"content": "AI运营工作台连接测试成功。"}}], "usage": {"prompt_tokens": 1, "completion_tokens": 2, "total_tokens": 3}}, request=request)
    provider = DeepSeekProvider(api_key="test-key", base_url="https://example.invalid", model="test", timeout=1, max_retries=0, client=httpx.Client(transport=httpx.MockTransport(ok)))
    assert provider.chat([AIMessage(role="user", content="test")], temperature=0, max_tokens=10).usage.total_tokens == 3
    provider.client = httpx.Client(transport=httpx.MockTransport(lambda request: (_ for _ in ()).throw(httpx.ReadTimeout("timeout", request=request))))
    with pytest.raises(AIProviderError) as error: provider.chat([AIMessage(role="user", content="test")], temperature=0, max_tokens=10)
    assert error.value.error_type == "TIMEOUT"

def test_deepseek_provider_retries_rate_limit_once() -> None:
    calls = 0
    def handler(request):
        nonlocal calls; calls += 1
        if calls == 1: return httpx.Response(429, request=request)
        return httpx.Response(200, json={"choices": [{"message": {"content": "ok"}}]}, request=request)
    provider = DeepSeekProvider(api_key="test-key", base_url="https://example.invalid", model="test", timeout=1, max_retries=1, client=httpx.Client(transport=httpx.MockTransport(handler)))
    assert provider.chat([AIMessage(role="user", content="test")], temperature=0, max_tokens=10).content == "ok" and calls == 2

def test_ai_status_api_never_exposes_key() -> None:
    response = TestClient(app).get("/api/v1/ai/status")
    assert response.status_code == 200
    assert "key" not in response.text.lower() and "api_key" not in response.text.lower()
