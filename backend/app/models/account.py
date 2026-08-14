from sqlalchemy import CheckConstraint, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, BusinessModelMixin


class Account(BusinessModelMixin, Base):
    __tablename__ = "accounts"
    __table_args__ = (
        CheckConstraint(
            "status IN ('启用', '停用', '测试中')",
            name="valid_status",
        ),
        Index("ix_accounts_org_deleted", "organization_id", "is_deleted"),
        Index("ix_accounts_org_platform", "organization_id", "platform"),
        Index("ix_accounts_org_status", "organization_id", "status"),
    )

    platform: Mapped[str] = mapped_column(String(30), nullable=False)
    account_name: Mapped[str] = mapped_column(String(120), nullable=False)
    account_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    account_avatar: Mapped[str | None] = mapped_column(String(500), nullable=True)
    account_type: Mapped[str] = mapped_column(String(40), nullable=False)
    positioning: Mapped[str | None] = mapped_column(String(255), nullable=True)
    target_user: Mapped[str | None] = mapped_column(String(255), nullable=True)
    operator: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), default="启用", server_default="启用", nullable=False
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
