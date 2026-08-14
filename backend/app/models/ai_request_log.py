from sqlalchemy import Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, BusinessModelMixin


class AIRequestLog(BusinessModelMixin, Base):
    __tablename__ = "ai_request_logs"
    __table_args__ = (
        Index("ix_ai_request_logs_org_created", "organization_id", "created_at"),
        Index("ix_ai_request_logs_org_status", "organization_id", "status"),
    )

    provider: Mapped[str] = mapped_column(String(40), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    feature: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    prompt_tokens: Mapped[int | None] = mapped_column(Integer)
    completion_tokens: Mapped[int | None] = mapped_column(Integer)
    total_tokens: Mapped[int | None] = mapped_column(Integer)
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    error_type: Mapped[str | None] = mapped_column(String(80))
