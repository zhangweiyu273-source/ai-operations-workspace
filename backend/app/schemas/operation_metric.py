from datetime import date, datetime
from decimal import Decimal
from math import ceil
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class OperationMetricWrite(BaseModel):
    account_id: UUID
    metric_date: date
    content_title: str = Field(min_length=1, max_length=255)
    content_url: str | None = Field(default=None, max_length=500)
    content_type: str | None = Field(default=None, max_length=50)
    publish_time: datetime | None = None
    exposure: int = Field(default=0, ge=0)
    views: int = Field(default=0, ge=0)
    likes: int = Field(default=0, ge=0)
    comments: int = Field(default=0, ge=0)
    favorites: int = Field(default=0, ge=0)
    shares: int = Field(default=0, ge=0)
    private_messages: int = Field(default=0, ge=0)
    new_leads: int = Field(default=0, ge=0)
    valid_leads: int = Field(default=0, ge=0)
    high_intent_leads: int = Field(default=0, ge=0)
    trial_bookings: int = Field(default=0, ge=0)
    deals: int = Field(default=0, ge=0)
    revenue: Decimal = Field(default=Decimal(0), ge=0, max_digits=14, decimal_places=2)
    notes: str | None = None

    @field_validator("content_title")
    @classmethod
    def title_not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("内容标题不能为空")
        return value

    @field_validator("content_url", "content_type", "notes")
    @classmethod
    def normalize_optional(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None


class OperationMetricCreate(OperationMetricWrite):
    pass


class OperationMetricUpdate(OperationMetricWrite):
    pass


class OperationMetricResponse(OperationMetricWrite):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    platform: str
    account_name: str
    created_by: UUID | None
    updated_by: UUID | None
    created_at: datetime
    updated_at: datetime


class MetricStatistics(BaseModel):
    exposure: int
    views: int
    interactions: int
    new_leads: int
    valid_leads: int
    high_intent_leads: int
    trial_bookings: int
    deals: int
    revenue: Decimal
    interaction_rate: Decimal
    valid_lead_rate: Decimal
    trial_conversion_rate: Decimal
    deal_rate: Decimal


class OperationMetricListResponse(BaseModel):
    items: list[OperationMetricResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

    @classmethod
    def create(cls, *, items: list[OperationMetricResponse], total: int, page: int, page_size: int):
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=ceil(total / page_size) if total else 0,
        )


class OperationMetricFilters(BaseModel):
    date_from: date | None = None
    date_to: date | None = None
    platform: str | None = None
    account_id: UUID | None = None
    content_type: str | None = None
    search: str | None = Field(default=None, max_length=255)

    @field_validator("search")
    @classmethod
    def normalize_search(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        return value or None

    def repository_kwargs(self) -> dict[str, object]:
        return self.model_dump()


class OperationMetricListQuery(OperationMetricFilters):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    sort_by: Literal["date", "exposure", "views", "revenue", "updated_at"] = "date"
    sort_order: Literal["asc", "desc"] = "desc"

    def filter_kwargs(self) -> dict[str, object]:
        return self.model_dump(exclude={"page", "page_size", "sort_by", "sort_order"})


class ImportErrorDetail(BaseModel):
    row: int
    field: str
    message: str


class ImportPreviewRow(BaseModel):
    row: int
    metric_date: date
    account_name: str
    content_title: str
    platform: str


class ImportResult(BaseModel):
    total_rows: int
    success_count: int
    failed_count: int
    duplicate_count: int
    errors: list[ImportErrorDetail]
    preview: list[ImportPreviewRow] = []
    can_import: bool
