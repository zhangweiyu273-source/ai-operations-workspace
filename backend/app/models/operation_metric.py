from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Numeric,
    String,
    Text,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, BusinessModelMixin


class OperationMetric(BusinessModelMixin, Base):
    __tablename__ = "operation_metrics"
    __table_args__ = (
        CheckConstraint(
            "exposure >= 0 AND views >= 0 AND likes >= 0 AND comments >= 0",
            name="non_negative_primary_metrics",
        ),
        CheckConstraint(
            "favorites >= 0 AND shares >= 0 AND private_messages >= 0",
            name="non_negative_interactions",
        ),
        CheckConstraint(
            "new_leads >= 0 AND valid_leads >= 0 AND high_intent_leads >= 0",
            name="non_negative_leads",
        ),
        CheckConstraint(
            "trial_bookings >= 0 AND deals >= 0 AND revenue >= 0", name="non_negative_conversions"
        ),
        Index("ix_operation_metrics_org_date", "organization_id", "metric_date"),
        Index("ix_operation_metrics_org_account", "organization_id", "account_id"),
        Index("ix_operation_metrics_org_platform", "organization_id", "platform"),
        Index("ix_operation_metrics_org_deleted", "organization_id", "is_deleted"),
        Index(
            "uq_operation_metrics_active_identity",
            "organization_id",
            "account_id",
            "metric_date",
            "dedup_key",
            unique=True,
            postgresql_where=text("is_deleted = false"),
            sqlite_where=text("is_deleted = 0"),
        ),
    )

    account_id: Mapped[UUID] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    metric_date: Mapped[date] = mapped_column(Date, nullable=False)
    platform: Mapped[str] = mapped_column(String(30), nullable=False)
    content_title: Mapped[str] = mapped_column(String(255), nullable=False)
    content_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    content_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    publish_time: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    exposure: Mapped[int] = mapped_column(BigInteger, default=0, server_default="0", nullable=False)
    views: Mapped[int] = mapped_column(BigInteger, default=0, server_default="0", nullable=False)
    likes: Mapped[int] = mapped_column(BigInteger, default=0, server_default="0", nullable=False)
    comments: Mapped[int] = mapped_column(BigInteger, default=0, server_default="0", nullable=False)
    favorites: Mapped[int] = mapped_column(
        BigInteger, default=0, server_default="0", nullable=False
    )
    shares: Mapped[int] = mapped_column(BigInteger, default=0, server_default="0", nullable=False)
    private_messages: Mapped[int] = mapped_column(
        BigInteger, default=0, server_default="0", nullable=False
    )
    new_leads: Mapped[int] = mapped_column(
        BigInteger, default=0, server_default="0", nullable=False
    )
    valid_leads: Mapped[int] = mapped_column(
        BigInteger, default=0, server_default="0", nullable=False
    )
    high_intent_leads: Mapped[int] = mapped_column(
        BigInteger, default=0, server_default="0", nullable=False
    )
    trial_bookings: Mapped[int] = mapped_column(
        BigInteger, default=0, server_default="0", nullable=False
    )
    deals: Mapped[int] = mapped_column(BigInteger, default=0, server_default="0", nullable=False)
    revenue: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), default=Decimal(0), server_default="0", nullable=False
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    dedup_key: Mapped[str] = mapped_column(String(64), nullable=False)
