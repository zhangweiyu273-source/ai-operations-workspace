from datetime import datetime
from enum import StrEnum
from math import ceil
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AccountStatus(StrEnum):
    ENABLED = "启用"
    DISABLED = "停用"
    TESTING = "测试中"


class AccountWrite(BaseModel):
    platform: str = Field(min_length=1, max_length=30)
    account_name: str = Field(min_length=1, max_length=120)
    account_url: str | None = Field(default=None, max_length=500)
    account_avatar: str | None = Field(default=None, max_length=500)
    account_type: str = Field(min_length=1, max_length=40)
    positioning: str | None = Field(default=None, max_length=255)
    target_user: str | None = Field(default=None, max_length=255)
    operator: str | None = Field(default=None, max_length=100)
    status: AccountStatus = AccountStatus.ENABLED
    description: str | None = None

    @field_validator("platform", "account_name", "account_type")
    @classmethod
    def required_text_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("字段不能为空")
        return value

    @field_validator(
        "account_url", "account_avatar", "positioning", "target_user", "operator", "description"
    )
    @classmethod
    def normalize_optional_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None


class AccountCreate(AccountWrite):
    pass


class AccountUpdate(AccountWrite):
    pass


class AccountResponse(AccountWrite):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    created_by: UUID | None
    updated_by: UUID | None
    created_at: datetime
    updated_at: datetime


class AccountSummary(BaseModel):
    account_count: int
    platform_count: int
    active_count: int


class AccountListResponse(BaseModel):
    items: list[AccountResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    summary: AccountSummary

    @classmethod
    def create(
        cls,
        *,
        items: list[AccountResponse],
        total: int,
        page: int,
        page_size: int,
        summary: AccountSummary,
    ) -> "AccountListResponse":
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=ceil(total / page_size) if total else 0,
            summary=summary,
        )
