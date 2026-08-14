from abc import ABC, abstractmethod

from app.schemas.ai import AIMessage, AIResponse


class AIProviderError(Exception):
    def __init__(self, error_type: str, message: str, retryable: bool = False) -> None:
        self.error_type, self.message, self.retryable = error_type, message, retryable
        super().__init__(message)


class BaseAIProvider(ABC):
    name: str

    @abstractmethod
    def chat(self, messages: list[AIMessage], *, temperature: float, max_tokens: int) -> AIResponse: ...

    @abstractmethod
    def configured(self) -> bool: ...
