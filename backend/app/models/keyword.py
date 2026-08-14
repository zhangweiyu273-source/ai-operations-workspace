from sqlalchemy import Index, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, BusinessModelMixin


class Keyword(BusinessModelMixin, Base):
    __tablename__ = "keywords"
    __table_args__ = (
        Index("ix_keywords_org_platform", "organization_id", "platform"),
        Index("ix_keywords_org_city", "organization_id", "city"),
        Index("ix_keywords_org_subject", "organization_id", "subject"),
        Index("ix_keywords_org_deleted", "organization_id", "is_deleted"),
        Index(
            "uq_keywords_active_normalized",
            "organization_id",
            "normalized_keyword",
            unique=True,
            postgresql_where=text("is_deleted = false"),
            sqlite_where=text("is_deleted = 0"),
        ),
    )

    keyword: Mapped[str] = mapped_column(String(255), nullable=False)
    normalized_keyword: Mapped[str] = mapped_column(String(255), nullable=False)
    platform: Mapped[str | None] = mapped_column(String(30), nullable=True)
    source: Mapped[str | None] = mapped_column(String(50), nullable=True)
    city: Mapped[str | None] = mapped_column(String(60), nullable=True)
    school_stage: Mapped[str | None] = mapped_column(String(30), nullable=True)
    grade: Mapped[str | None] = mapped_column(String(30), nullable=True)
    subject: Mapped[str | None] = mapped_column(String(30), nullable=True)
    need_type: Mapped[str | None] = mapped_column(String(60), nullable=True)
    pain_point: Mapped[str | None] = mapped_column(Text, nullable=True)
    search_intent: Mapped[str | None] = mapped_column(String(40), nullable=True)
    commercial_intent: Mapped[str | None] = mapped_column(String(10), nullable=True)
    content_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="启用", server_default="启用"
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
