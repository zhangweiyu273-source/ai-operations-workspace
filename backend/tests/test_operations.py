from datetime import date, datetime, timedelta, timezone
from uuid import UUID

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.exceptions import AppError
from app.db.base import Base
from app.models import Account, OperationReview, OperationTask, Organization, Topic
from app.schemas.operation import ReviewWrite, TaskWrite
from app.services.operation_review_service import OperationReviewService
from app.services.operation_task_service import OperationTaskService

ORG_ID = UUID("00000000-0000-4000-8000-000000000088")


@pytest.fixture
def session() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    maker = sessionmaker(bind=engine, expire_on_commit=False)
    with maker() as value:
        value.add(Organization(id=ORG_ID, name="任务测试组织"))
        account = Account(organization_id=ORG_ID, platform="小红书", account_name="测试账号", account_type="品牌账号", status="启用")
        value.add(account)
        value.flush()
        value.add(Topic(organization_id=ORG_ID, title="测试选题", platform="小红书", account_id=account.id, content_type="图文", status="待规划", priority="中"))
        value.commit()
        yield value


def task_data(session: Session, **changes: object) -> TaskWrite:
    account_id = session.scalar(select(Account.id))
    topic_id = session.scalar(select(Topic.id))
    payload: dict[str, object] = {"title": "制作内容", "task_type": "内容创作", "status": "待开始", "priority": "高", "related_account_id": account_id, "related_topic_id": topic_id}
    payload.update(changes)
    return TaskWrite.model_validate(payload)


def test_task_service_crud_filters_stats_soft_delete_and_completion(session: Session) -> None:
    service = OperationTaskService(session)
    overdue = service.create(ORG_ID, task_data(session, title="逾期任务", deadline=datetime.now(timezone.utc) - timedelta(days=1)))
    created = service.create(ORG_ID, task_data(session, title="发布任务", task_type="内容发布", status="进行中", priority="中"))
    assert created.related_topic_id and created.related_account_id
    assert service.list(ORG_ID, page=1, page_size=1, search="发布", status=None, task_type=None, priority=None, assignee=None, related_account_id=None, related_topic_id=None)["total"] == 1
    assert service.list(ORG_ID, page=1, page_size=20, search=None, status="进行中", task_type="内容发布", priority="中", assignee=None, related_account_id=created.related_account_id, related_topic_id=created.related_topic_id)["total"] == 1
    assert service.response(service.get(ORG_ID, overdue.id)).is_overdue is True
    completed = service.update(ORG_ID, created.id, task_data(session, title="发布任务", status="已完成"))
    assert completed.completed_at is not None and completed.is_overdue is False
    reopened = service.update(ORG_ID, created.id, task_data(session, title="发布任务", status="进行中"))
    assert reopened.completed_at is None
    assert service.stats(ORG_ID) == {"total": 2, "completed": 0, "in_progress": 1, "overdue": 1}
    service.delete(ORG_ID, created.id)
    assert session.get(OperationTask, created.id).is_deleted is True
    assert service.list(ORG_ID, page=1, page_size=20, search=None, status=None, task_type=None, priority=None, assignee=None, related_account_id=None, related_topic_id=None)["total"] == 1


def test_task_service_rejects_invalid_relations_and_rolls_back(session: Session) -> None:
    service = OperationTaskService(session)
    missing = UUID("00000000-0000-4000-8000-000000000999")
    with pytest.raises(AppError) as topic_error:
        service.create(ORG_ID, task_data(session, related_topic_id=missing))
    assert topic_error.value.code == "TASK_TOPIC_NOT_FOUND"
    with pytest.raises(AppError) as account_error:
        service.create(ORG_ID, task_data(session, related_account_id=missing))
    assert account_error.value.code == "TASK_ACCOUNT_NOT_FOUND"
    assert session.scalar(select(OperationTask.id)) is None


def test_review_service_crud_pagination_stats_task_validation_and_soft_delete(session: Session) -> None:
    tasks = OperationTaskService(session)
    task = tasks.create(ORG_ID, task_data(session))
    reviews = OperationReviewService(session)
    first = reviews.create(ORG_ID, ReviewWrite(task_id=task.id, title="首日复盘", review_date=date.today(), result="完成"))
    second = reviews.create(ORG_ID, ReviewWrite(task_id=task.id, title="第二次复盘", review_date=date.today(), problem="节奏慢"))
    page = reviews.list(ORG_ID, page=1, page_size=1, task_id=task.id, search="复盘")
    assert page["total"] == 2 and len(page["items"]) == 1
    updated = reviews.update(ORG_ID, first.id, ReviewWrite(task_id=task.id, title="首日复盘更新", review_date=date.today(), result="达成"))
    assert updated.result == "达成"
    assert reviews.stats(ORG_ID)["total"] == 2
    reviews.delete(ORG_ID, second.id)
    assert session.get(OperationReview, second.id).is_deleted is True
    missing = UUID("00000000-0000-4000-8000-000000000998")
    with pytest.raises(AppError) as error:
        reviews.create(ORG_ID, ReviewWrite(task_id=missing, title="无效", review_date=date.today()))
    assert error.value.code == "TASK_NOT_FOUND"
