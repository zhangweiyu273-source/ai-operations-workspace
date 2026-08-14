from datetime import date, datetime
from math import ceil
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

TopicStatus = Literal["待规划", "待创作", "制作中", "待发布", "已发布", "已复盘", "暂停"]


class TopicWrite(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    platform: str = Field(min_length=1, max_length=30)
    account_id: UUID
    content_type: Literal["图文", "短视频", "直播", "文章", "朋友圈"]
    status: TopicStatus = "待规划"
    target_user: str | None = None
    school_stage: str | None = None
    subject: str | None = None
    city: str | None = None
    pain_point: str | None = None
    content_goal: Literal["涨粉", "搜索获客", "建立信任", "转化咨询", "品牌曝光"] | None = None
    priority: Literal["高", "中", "低"] = "中"
    publish_date: date | None = None
    notes: str | None = None
    keyword_ids: list[UUID] = []

    @field_validator("title")
    @classmethod
    def title_not_blank(cls, v: str):
        if not v.strip():
            raise ValueError("选题标题不能为空")
        return v.strip()

    @field_validator(
        "target_user", "school_stage", "subject", "city", "pain_point", "notes", mode="before"
    )
    @classmethod
    def optional_strip(cls, v):
        return v.strip() or None if isinstance(v, str) else v


class TopicCreate(TopicWrite):
    pass


class TopicUpdate(TopicWrite):
    pass


class TopicKeywordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    keyword: str
    platform: str | None = None


class TopicResponse(TopicWrite):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    organization_id: UUID
    account_name: str
    keyword_count: int
    keywords: list[TopicKeywordResponse] = []
    created_by: UUID | None
    updated_by: UUID | None
    created_at: datetime
    updated_at: datetime


class TopicListResponse(BaseModel):
    items: list[TopicResponse]
    total: int
    page: int
    page_size: int
    total_pages: int

    @classmethod
    def create(cls, *, items, total, page, page_size):
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=ceil(total / page_size) if total else 0,
        )


class TopicFilters(BaseModel):
    platform: str | None = None
    account_id: UUID | None = None
    status: TopicStatus | None = None
    content_type: str | None = None
    subject: str | None = None
    school_stage: str | None = None
    priority: Literal["高", "中", "低"] | None = None
    search: str | None = None

    def values(self):
        return self.model_dump()


class TopicListQuery(TopicFilters):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    sort_by: Literal["updated_at", "publish_date", "priority"] = "updated_at"
    sort_order: Literal["asc", "desc"] = "desc"

    def filters(self):
        return self.model_dump(exclude={"page", "page_size", "sort_by", "sort_order"})


class TopicStats(BaseModel):
    total: int
    pending_creation: int
    in_production: int
    published: int
    reviewed: int
    platform_count: int
