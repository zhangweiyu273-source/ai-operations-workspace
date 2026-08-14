from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, MetaData, func
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


class UUIDPrimaryKeyMixin:
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )


class SoftDeleteMixin:
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="false", nullable=False
    )


class OrganizationScopeMixin:
    @declared_attr
    def organization_id(cls) -> Mapped[UUID]:
        return mapped_column(ForeignKey("organizations.id"), index=True, nullable=False)


class AuditActorMixin:
    @declared_attr
    def created_by(cls) -> Mapped[UUID | None]:
        return mapped_column(ForeignKey("users.id"), nullable=True)

    @declared_attr
    def updated_by(cls) -> Mapped[UUID | None]:
        return mapped_column(ForeignKey("users.id"), nullable=True)


class BusinessModelMixin(
    UUIDPrimaryKeyMixin,
    OrganizationScopeMixin,
    AuditActorMixin,
    TimestampMixin,
    SoftDeleteMixin,
):
    """Shared columns for future organization-owned business entities."""

    __abstract__ = True
