from uuid import UUID
from sqlalchemy import ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, BusinessModelMixin, TimestampMixin, UUIDPrimaryKeyMixin


class Knowledge(BusinessModelMixin, Base):
    __tablename__ = "knowledge"
    __table_args__ = (
        Index("ix_knowledge_org_category", "organization_id", "category"),
        Index("ix_knowledge_org_status", "organization_id", "status"),
        Index("ix_knowledge_org_updated", "organization_id", "updated_at"),
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    source_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    priority: Mapped[str] = mapped_column(String(10), nullable=False, default="中", server_default="中")
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="启用", server_default="启用")


class KnowledgeTag(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "knowledge_tags"
    __table_args__ = (UniqueConstraint("knowledge_id", "tag_name", name="uq_knowledge_tags_knowledge_tag"),)
    knowledge_id: Mapped[UUID] = mapped_column(ForeignKey("knowledge.id", ondelete="CASCADE"), nullable=False)
    tag_name: Mapped[str] = mapped_column(String(80), nullable=False)
