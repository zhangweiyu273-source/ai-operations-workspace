import logging
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.models import OperationTask
from app.repositories.operation_task_repository import OperationTaskRepository
from app.schemas.operation import TaskResponse, TaskWrite

logger = logging.getLogger(__name__)
TERMINAL_STATUSES = {"已完成", "已取消"}


class OperationTaskService:
    def __init__(self, session: Session):
        self.session = session
        self.repository = OperationTaskRepository(session)

    def get(self, organization_id: UUID, task_id: UUID) -> OperationTask:
        task = self.repository.get(organization_id, task_id)
        if task is None:
            raise AppError("任务不存在", 404, "TASK_NOT_FOUND")
        return task

    def _validate_relations(self, organization_id: UUID, data: TaskWrite) -> None:
        if data.related_topic_id and not self.repository.topic(organization_id, data.related_topic_id):
            raise AppError("关联选题不存在", 400, "TASK_TOPIC_NOT_FOUND")
        if data.related_account_id and not self.repository.account(organization_id, data.related_account_id):
            raise AppError("关联账号不存在", 400, "TASK_ACCOUNT_NOT_FOUND")

    @staticmethod
    def _completed_at(status: str, existing: datetime | None = None) -> datetime | None:
        if status == "已完成":
            return existing or datetime.now(timezone.utc)
        return None

    @staticmethod
    def _is_overdue(task: OperationTask) -> bool:
        if not task.deadline or task.status in TERMINAL_STATUSES:
            return False
        deadline = task.deadline
        if deadline.tzinfo is None:
            deadline = deadline.replace(tzinfo=timezone.utc)
        return deadline < datetime.now(timezone.utc)

    def response(self, task: OperationTask) -> TaskResponse:
        payload = {name: getattr(task, name) for name in TaskResponse.model_fields if name != "is_overdue"}
        return TaskResponse.model_validate({**payload, "is_overdue": self._is_overdue(task)})

    def create(self, organization_id: UUID, data: TaskWrite) -> TaskResponse:
        try:
            self._validate_relations(organization_id, data)
            task = OperationTask(organization_id=organization_id, **data.model_dump(), completed_at=self._completed_at(data.status))
            self.repository.add(task)
            self.session.commit()
            self.session.refresh(task)
            return self.response(task)
        except Exception:
            self.session.rollback()
            logger.exception("创建运营任务失败")
            raise

    def update(self, organization_id: UUID, task_id: UUID, data: TaskWrite) -> TaskResponse:
        try:
            task = self.get(organization_id, task_id)
            self._validate_relations(organization_id, data)
            for name, value in data.model_dump().items():
                setattr(task, name, value)
            task.completed_at = self._completed_at(data.status, task.completed_at)
            self.session.commit()
            self.session.refresh(task)
            return self.response(task)
        except Exception:
            self.session.rollback()
            logger.exception("更新运营任务失败", extra={"task_id": str(task_id)})
            raise

    def delete(self, organization_id: UUID, task_id: UUID) -> None:
        try:
            self.get(organization_id, task_id).is_deleted = True
            self.session.commit()
        except Exception:
            self.session.rollback()
            logger.exception("删除运营任务失败", extra={"task_id": str(task_id)})
            raise

    def list(self, organization_id: UUID, **params: object) -> dict[str, object]:
        items, total = self.repository.list(organization_id, **params)
        return {"items": [self.response(item) for item in items], "total": total, "page": params["page"], "page_size": params["page_size"]}

    def stats(self, organization_id: UUID) -> dict[str, int]:
        total, completed, in_progress, overdue = self.repository.stats(organization_id, datetime.now(timezone.utc))
        return {"total": total, "completed": completed, "in_progress": in_progress, "overdue": overdue}
