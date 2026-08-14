from datetime import datetime
from math import ceil
from typing import Literal
from uuid import UUID
from pydantic import BaseModel, Field, field_validator

KnowledgeCategory = Literal["公司资料", "课程资料", "校区资料", "老师资料", "老板IP资料", "用户洞察", "销售话术", "运营SOP", "内容案例", "行业资料", "其他"]
Priority = Literal["高", "中", "低"]
Status = Literal["启用", "停用", "草稿"]

class KnowledgeWrite(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    category: KnowledgeCategory
    content: str = Field(min_length=1)
    summary: str | None = None
    source_type: str | None = Field(default=None, max_length=50)
    source_name: str | None = Field(default=None, max_length=255)
    priority: Priority = "中"
    status: Status = "启用"
    tags: list[str] = []
    @field_validator("title", "content")
    @classmethod
    def non_blank(cls, value: str):
        if not value.strip(): raise ValueError("标题和正文不能为空")
        return value.strip()
    @field_validator("tags")
    @classmethod
    def tags_clean(cls, values):
        return list(dict.fromkeys(value.strip() for value in values if value.strip()))

class KnowledgeCreate(KnowledgeWrite): pass
class KnowledgeUpdate(KnowledgeWrite): pass
class KnowledgeResponse(KnowledgeWrite):
    id: UUID; organization_id: UUID; created_at: datetime; updated_at: datetime; created_by: UUID | None; updated_by: UUID | None
class KnowledgeListResponse(BaseModel):
    items: list[KnowledgeResponse]; total: int; page: int; page_size: int; total_pages: int
    @classmethod
    def create(cls, *, items, total, page, page_size): return cls(items=items,total=total,page=page,page_size=page_size,total_pages=ceil(total/page_size) if total else 0)
class KnowledgeQuery(BaseModel):
    page: int = Field(1, ge=1); page_size: int = Field(20, ge=1, le=100); category: KnowledgeCategory | None = None; status: Status | None = None; priority: Priority | None = None; tag: str | None = None; search: str | None = None
    def filters(self): return self.model_dump(exclude={"page", "page_size"})
class KnowledgeStats(BaseModel): total: int; category_count: int; high_priority: int; recently_updated: int
