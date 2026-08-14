import time

import httpx

from app.ai.providers.base import AIProviderError, BaseAIProvider
from app.schemas.ai import AIMessage, AIResponse, AIUsage


class DeepSeekProvider(BaseAIProvider):
    name = "deepseek"

    def __init__(self, *, api_key: str | None, base_url: str, model: str, timeout: float, max_retries: int, client: httpx.Client | None = None) -> None:
        self.api_key, self.base_url, self.model = api_key, base_url.rstrip("/"), model
        self.timeout, self.max_retries = timeout, max_retries
        self.client = client or httpx.Client(timeout=timeout)

    def configured(self) -> bool:
        return bool(self.api_key)

    def chat(self, messages: list[AIMessage], *, temperature: float = 0.2, max_tokens: int = 512) -> AIResponse:
        if not self.configured():
            raise AIProviderError("NOT_CONFIGURED", "AI Provider is not configured")
        payload = {"model": self.model, "messages": [message.model_dump() for message in messages], "temperature": temperature, "max_tokens": max_tokens}
        started = time.perf_counter()
        for attempt in range(self.max_retries + 1):
            try:
                response = self.client.post(f"{self.base_url}/chat/completions", headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}, json=payload)
                if response.status_code in (401, 403): raise AIProviderError("AUTHENTICATION", "AI Provider authentication failed")
                if response.status_code == 429: raise AIProviderError("RATE_LIMITED", "AI Provider rate limit reached", retryable=True)
                if response.status_code >= 500: raise AIProviderError("PROVIDER_UNAVAILABLE", "AI Provider is temporarily unavailable", retryable=True)
                response.raise_for_status(); body = response.json()
                content = body["choices"][0]["message"]["content"]
                usage = body.get("usage", {})
                return AIResponse(provider=self.name, model=body.get("model", self.model), content=content, usage=AIUsage(prompt_tokens=usage.get("prompt_tokens"), completion_tokens=usage.get("completion_tokens"), total_tokens=usage.get("total_tokens")), latency_ms=round((time.perf_counter() - started) * 1000), request_id=response.headers.get("x-request-id"))
            except AIProviderError as exc:
                if not exc.retryable or attempt == self.max_retries: raise
            except httpx.TimeoutException as exc:
                if attempt == self.max_retries: raise AIProviderError("TIMEOUT", "AI Provider request timed out", retryable=True) from exc
            except (httpx.NetworkError, httpx.HTTPError, ValueError, KeyError, TypeError) as exc:
                if attempt == self.max_retries: raise AIProviderError("PROVIDER_ERROR", "AI Provider returned an invalid response", retryable=True) from exc
            time.sleep(min(0.25 * (2 ** attempt), 1.0))
        raise AIProviderError("PROVIDER_ERROR", "AI Provider request failed")
