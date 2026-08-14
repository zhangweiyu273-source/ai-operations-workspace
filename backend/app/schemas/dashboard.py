from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel


class DashboardTaskOverview(BaseModel):
    today: int
    in_progress: int
    overdue: int
    pending_review: int


class DashboardContentOverview(BaseModel):
    total: int
    pending_creation: int
    in_production: int
    published: int


class DashboardKeywordOverview(BaseModel):
    total: int
    high_commercial_intent: int
    unused: int
    recently_added: int


class DashboardAccountItem(BaseModel):
    id: UUID
    account_name: str
    platform: str
    updated_at: datetime


class DashboardAccountOverview(BaseModel):
    total: int
    platform_distribution: dict[str, int]
    recently_updated: DashboardAccountItem | None


class DashboardKnowledgeItem(BaseModel):
    id: UUID
    title: str
    category: str
    updated_at: datetime


class DashboardKnowledgeOverview(BaseModel):
    total: int
    category_count: int
    recently_updated: DashboardKnowledgeItem | None


class DashboardTaskItem(BaseModel):
    id: UUID
    title: str
    task_type: str
    account_name: str | None
    topic_title: str | None
    priority: str
    status: str
    deadline: datetime | None
    is_overdue: bool


class DashboardReviewItem(BaseModel):
    id: UUID
    title: str
    task_title: str | None
    review_date: date
    problem_summary: str | None


class DashboardResponse(BaseModel):
    tasks: DashboardTaskOverview
    content: DashboardContentOverview
    keywords: DashboardKeywordOverview
    accounts: DashboardAccountOverview
    knowledge: DashboardKnowledgeOverview
    today_tasks: list[DashboardTaskItem]
    review_reminders: list[DashboardReviewItem]
