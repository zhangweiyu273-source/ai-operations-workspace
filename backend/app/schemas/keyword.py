from datetime import datetime
from math import ceil
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class KeywordWrite(BaseModel):
    keyword: str = Field(min_length=1, max_length=255)
    platform: str | None = Field(default=None, max_length=30)
    source: str | None = Field(default=None, max_length=50)
    city: str | None = Field(default=None, max_length=60)
    school_stage: str | None = Field(default=None, max_length=30)
    grade: str | None = Field(default=None, max_length=30)
    subject: str | None = Field(default=None, max_length=30)
    need_type: str | None = Field(default=None, max_length=60)
    pain_point: str | None = None
    search_intent: str | None = Field(default=None, max_length=40)
    commercial_intent: Literal["低", "中", "高"] | None = None
    content_status: Literal["未使用", "已进入选题", "已发布", "已复盘"] | None = None
    status: Literal["启用", "停用", "待审核"] = "启用"
    notes: str | None = None

    @field_validator("keyword")
    @classmethod
    def keyword_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("关键词不能为空")
        return value.strip()

    @field_validator(
        "platform",
        "source",
        "city",
        "school_stage",
        "grade",
        "subject",
        "need_type",
        "pain_point",
        "search_intent",
        "notes",
    )
    @classmethod
    def normalize_optional(cls, value: str | None) -> str | None:
        return value.strip() or None if value is not None else None


class KeywordCreate(KeywordWrite):
    pass


class KeywordUpdate(KeywordWrite):
    pass


class KeywordResponse(KeywordWrite):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    organization_id: UUID
    created_by: UUID | None
    updated_by: UUID | None
    created_at: datetime
    updated_at: datetime


class KeywordListResponse(BaseModel):
    items: list[KeywordResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

    @classmethod
    def create(cls, *, items: list[KeywordResponse], total: int, page: int, page_size: int):
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=ceil(total / page_size) if total else 0,
        )


class KeywordFilters(BaseModel):
    platform: str | None = None
    source: str | None = None
    city: str | None = None
    school_stage: str | None = None
    grade: str | None = None
    subject: str | None = None
    search_intent: str | None = None
    commercial_intent: Literal["低", "中", "高"] | None = None
    content_status: Literal["未使用", "已进入选题", "已发布", "已复盘"] | None = None
    status: Literal["启用", "停用", "待审核"] | None = None
    search: str | None = Field(default=None, max_length=255)

    @field_validator("search")
    @classmethod
    def strip_search(cls, value: str | None) -> str | None:
        return value.strip() or None if value else None

    def repository_kwargs(self) -> dict[str, object]:
        return self.model_dump()


class KeywordListQuery(KeywordFilters):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    sort_by: Literal["updated_at", "created_at", "keyword"] = "updated_at"
    sort_order: Literal["asc", "desc"] = "desc"

    def filter_kwargs(self) -> dict[str, object]:
        return self.model_dump(exclude={"page", "page_size", "sort_by", "sort_order"})


class KeywordStatistics(BaseModel):
    total: int
    high_commercial_intent: int
    unused: int
    in_topics: int
    platform_count: int
    subject_count: int


class ImportErrorDetail(BaseModel):
    row: int
    field: str
    message: str


class KeywordImportPreview(BaseModel):
    row: int
    keyword: str
    platform: str | None = None
    source: str | None = None


class KeywordImportResult(BaseModel):
    total_rows: int
    success_count: int
    failed_count: int
    duplicate_count: int
    errors: list[ImportErrorDetail]
    preview: list[KeywordImportPreview] = []
    can_import: bool
