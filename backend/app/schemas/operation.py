from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

TaskType = Literal["内容策划", "内容创作", "内容发布", "数据分析", "运营复盘", "活动运营", "其他"]
TaskStatus = Literal["待开始", "进行中", "待审核", "已完成", "已取消"]
Priority = Literal["高", "中", "低"]


class TaskWrite(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    task_type: TaskType
    related_topic_id: UUID | None = None
    related_account_id: UUID | None = None
    status: TaskStatus = "待开始"
    priority: Priority = "中"
    assignee: str | None = None
    start_date: date | None = None
    deadline: datetime | None = None


class TaskResponse(TaskWrite):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    organization_id: UUID
    completed_at: datetime | None
    created_at: datetime
    updated_at: datetime
    is_overdue: bool = False


class ReviewWrite(BaseModel):
    task_id: UUID
    title: str = Field(min_length=1, max_length=255)
    review_date: date
    goal: str | None = None
    result: str | None = None
    problem: str | None = None
    reason: str | None = None
    improvement: str | None = None
    next_action: str | None = None


class ReviewResponse(ReviewWrite):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    organization_id: UUID
    created_at: datetime
    updated_at: datetime
