import logging
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.models import OperationReview
from app.repositories.operation_review_repository import OperationReviewRepository
from app.schemas.operation import ReviewResponse, ReviewWrite
from app.services.operation_task_service import OperationTaskService

logger = logging.getLogger(__name__)


class OperationReviewService:
    def __init__(self, session: Session):
        self.session = session
        self.repository = OperationReviewRepository(session)
        self.tasks = OperationTaskService(session)

    def get(self, organization_id: UUID, review_id: UUID) -> OperationReview:
        review = self.repository.get(organization_id, review_id)
        if review is None:
            raise AppError("复盘不存在", 404, "REVIEW_NOT_FOUND")
        return review

    def _validate_task(self, organization_id: UUID, data: ReviewWrite) -> None:
        self.tasks.get(organization_id, data.task_id)

    def create(self, organization_id: UUID, data: ReviewWrite) -> ReviewResponse:
        try:
            self._validate_task(organization_id, data)
            review = OperationReview(organization_id=organization_id, **data.model_dump())
            self.repository.add(review)
            self.session.commit()
            self.session.refresh(review)
            return ReviewResponse.model_validate(review)
        except Exception:
            self.session.rollback()
            logger.exception("创建运营复盘失败")
            raise

    def update(self, organization_id: UUID, review_id: UUID, data: ReviewWrite) -> ReviewResponse:
        try:
            review = self.get(organization_id, review_id)
            self._validate_task(organization_id, data)
            for name, value in data.model_dump().items():
                setattr(review, name, value)
            self.session.commit()
            self.session.refresh(review)
            return ReviewResponse.model_validate(review)
        except Exception:
            self.session.rollback()
            logger.exception("更新运营复盘失败", extra={"review_id": str(review_id)})
            raise

    def delete(self, organization_id: UUID, review_id: UUID) -> None:
        try:
            self.get(organization_id, review_id).is_deleted = True
            self.session.commit()
        except Exception:
            self.session.rollback()
            logger.exception("删除运营复盘失败", extra={"review_id": str(review_id)})
            raise

    def list(self, organization_id: UUID, **params: object) -> dict[str, object]:
        items, total = self.repository.list(organization_id, **params)
        return {"items": [ReviewResponse.model_validate(item) for item in items], "total": total, "page": params["page"], "page_size": params["page_size"]}

    def stats(self, organization_id: UUID) -> dict[str, object]:
        total, latest_review_date = self.repository.stats(organization_id)
        return {"total": total, "latest_review_date": latest_review_date}
