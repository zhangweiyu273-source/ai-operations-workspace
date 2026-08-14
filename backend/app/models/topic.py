from datetime import date
from uuid import UUID

from sqlalchemy import Date, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, BusinessModelMixin, TimestampMixin, UUIDPrimaryKeyMixin


class Topic(BusinessModelMixin, Base):
    __tablename__ = "topics"
    __table_args__ = (
        Index("ix_topics_org_platform", "organization_id", "platform"),
        Index("ix_topics_org_status", "organization_id", "status"),
        Index("ix_topics_org_account", "organization_id", "account_id"),
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(30), nullable=False)
    platform: Mapped[str] = mapped_column(String(30), nullable=False)
    account_id: Mapped[UUID] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="待规划", server_default="待规划"
    )
    target_user: Mapped[str | None] = mapped_column(String(120))
    school_stage: Mapped[str | None] = mapped_column(String(30))
    subject: Mapped[str | None] = mapped_column(String(30))
    city: Mapped[str | None] = mapped_column(String(60))
    pain_point: Mapped[str | None] = mapped_column(Text)
    content_goal: Mapped[str | None] = mapped_column(String(40))
    priority: Mapped[str] = mapped_column(
        String(10), nullable=False, default="中", server_default="中"
    )
    publish_date: Mapped[date | None] = mapped_column(Date)
    content_id: Mapped[str | None] = mapped_column(String(100))
    notes: Mapped[str | None] = mapped_column(Text)


class TopicKeyword(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "topic_keywords"
    __table_args__ = (
        UniqueConstraint("topic_id", "keyword_id", name="uq_topic_keywords_topic_keyword"),
    )
    topic_id: Mapped[UUID] = mapped_column(
        ForeignKey("topics.id", ondelete="CASCADE"), nullable=False
    )
    keyword_id: Mapped[UUID] = mapped_column(ForeignKey("keywords.id"), nullable=False)
