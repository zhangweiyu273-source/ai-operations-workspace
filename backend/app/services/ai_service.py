import logging
import time
from uuid import UUID

from sqlalchemy.orm import Session

from app.ai.providers import DeepSeekProvider
from app.ai.providers.base import AIProviderError, BaseAIProvider
from app.core.config import get_settings
from app.core.exceptions import AppError
from app.models import AIRequestLog
from app.repositories.ai_request_log import AIRequestLogRepository
from app.schemas.ai import AIMessage, AIResponse, AIStatistics, AIStatusResponse

logger = logging.getLogger(__name__)


class AIService:
    def __init__(self, session: Session, provider: BaseAIProvider | None = None) -> None:
        self.session, self.settings = session, get_settings()
        self.provider = provider or self._provider()
        self.logs = AIRequestLogRepository(session)

    def _provider(self) -> BaseAIProvider:
        if self.settings.ai_provider != "deepseek":
            raise AppError("AI Provider is not supported", 503, "AI_PROVIDER_UNSUPPORTED")
        return DeepSeekProvider(api_key=self.settings.deepseek_api_key, base_url=self.settings.deepseek_base_url, model=self.settings.deepseek_model, timeout=self.settings.ai_timeout, max_retries=self.settings.ai_max_retries)

    def status(self) -> AIStatusResponse:
        if self.settings.ai_provider != "deepseek": return AIStatusResponse(configured=False, provider=self.settings.ai_provider, model=None, provider_status="unsupported")
        return AIStatusResponse(configured=self.provider.configured(), provider=self.provider.name, model=self.settings.deepseek_model, provider_status="configured" if self.provider.configured() else "not_configured")

    def generate(self, organization_id: UUID, *, feature: str, messages: list[AIMessage], temperature: float = 0.2, max_tokens: int = 512) -> AIResponse:
        started = time.perf_counter()
        try:
            result = self.provider.chat(messages, temperature=temperature, max_tokens=max_tokens)
            self._record(organization_id, feature, "success", result, None, round((time.perf_counter() - started) * 1000))
            return result
        except AIProviderError as exc:
            self._record(organization_id, feature, "failed", None, exc.error_type, round((time.perf_counter() - started) * 1000))
            raise AppError("AI service is unavailable", 503 if exc.error_type != "AUTHENTICATION" else 401, f"AI_{exc.error_type}") from exc

    def _record(self, organization_id: UUID, feature: str, status: str, result: AIResponse | None, error_type: str | None, latency_ms: int) -> None:
        try:
            usage = result.usage if result else None
            self.logs.add(AIRequestLog(organization_id=organization_id, provider=self.settings.ai_provider, model=self.settings.deepseek_model, feature=feature, status=status, prompt_tokens=usage.prompt_tokens if usage else None, completion_tokens=usage.completion_tokens if usage else None, total_tokens=usage.total_tokens if usage else None, latency_ms=result.latency_ms if result and result.latency_ms is not None else latency_ms, error_type=error_type))
            self.session.commit()
        except Exception:
            self.session.rollback(); logger.exception("AI request log write failed organization_id=%s feature=%s", organization_id, feature)

    def statistics(self, organization_id: UUID) -> AIStatistics:
        values = self.logs.statistics(organization_id)
        return AIStatistics(today_calls=values[0], success_count=values[1], failure_count=values[2], total_tokens=values[3], average_latency_ms=float(values[4]) if values[4] is not None else None)
