from datetime import date, datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import and_, exists, func, or_, select
from sqlalchemy.orm import Session

from app.models import Account, Keyword, Knowledge, OperationReview, OperationTask, Topic


class DashboardRepository:
    """Read-only aggregate queries for the workbench landing page."""

    def __init__(self, session: Session) -> None:
        self.session = session

    @staticmethod
    def _active(model, organization_id: UUID) -> list[object]:
        return [model.organization_id == organization_id, model.is_deleted.is_(False)]

    def get(self, organization_id: UUID) -> dict[str, object]:
        now = datetime.now(timezone.utc)
        today = now.date()
        task_filters = self._active(OperationTask, organization_id)
        review_filters = self._active(OperationReview, organization_id)
        topic_filters = self._active(Topic, organization_id)
        keyword_filters = self._active(Keyword, organization_id)
        account_filters = self._active(Account, organization_id)
        knowledge_filters = self._active(Knowledge, organization_id)
        terminal_statuses = ["已完成", "已取消"]
        today_task_condition = or_(
            OperationTask.start_date == today,
            func.date(OperationTask.deadline) == today,
        )

        task_counts = self.session.execute(
            select(
                func.count(OperationTask.id).filter(today_task_condition),
                func.count(OperationTask.id).filter(OperationTask.status == "进行中"),
                func.count(OperationTask.id).filter(
                    OperationTask.deadline < now,
                    OperationTask.status.not_in(terminal_statuses),
                ),
                func.count(OperationTask.id).filter(
                    and_(
                        OperationTask.status == "已完成",
                        ~exists(
                            select(OperationReview.id).where(
                                OperationReview.task_id == OperationTask.id,
                                OperationReview.is_deleted.is_(False),
                            )
                        ),
                    )
                ),
            ).where(*task_filters)
        ).one()
        topic_counts = self.session.execute(
            select(
                func.count(Topic.id),
                func.count(Topic.id).filter(Topic.status == "待创作"),
                func.count(Topic.id).filter(Topic.status == "制作中"),
                func.count(Topic.id).filter(Topic.status == "已发布"),
            ).where(*topic_filters)
        ).one()
        keyword_counts = self.session.execute(
            select(
                func.count(Keyword.id),
                func.count(Keyword.id).filter(Keyword.commercial_intent == "高"),
                func.count(Keyword.id).filter(Keyword.content_status == "未使用"),
                func.count(Keyword.id).filter(Keyword.created_at >= now - timedelta(days=7)),
            ).where(*keyword_filters)
        ).one()
        account_total = self.session.scalar(select(func.count(Account.id)).where(*account_filters)) or 0
        platforms = self.session.execute(
            select(Account.platform, func.count(Account.id)).where(*account_filters).group_by(Account.platform)
        ).all()
        recent_account = self.session.execute(
            select(Account).where(*account_filters).order_by(Account.updated_at.desc(), Account.id).limit(1)
        ).scalar_one_or_none()
        knowledge_counts = self.session.execute(
            select(func.count(Knowledge.id), func.count(func.distinct(Knowledge.category))).where(*knowledge_filters)
        ).one()
        recent_knowledge = self.session.execute(
            select(Knowledge).where(*knowledge_filters).order_by(Knowledge.updated_at.desc(), Knowledge.id).limit(1)
        ).scalar_one_or_none()
        task_rows = self.session.execute(
            select(OperationTask, Account.account_name, Topic.title)
            .outerjoin(Account, Account.id == OperationTask.related_account_id)
            .outerjoin(Topic, Topic.id == OperationTask.related_topic_id)
            .where(*task_filters, today_task_condition)
            .order_by(OperationTask.deadline.asc(), OperationTask.updated_at.desc())
            .limit(8)
        ).all()
        review_rows = self.session.execute(
            select(OperationReview, OperationTask.title)
            .outerjoin(OperationTask, OperationTask.id == OperationReview.task_id)
            .where(*review_filters, OperationReview.problem.is_not(None), OperationReview.problem != "")
            .order_by(OperationReview.review_date.desc(), OperationReview.updated_at.desc())
            .limit(5)
        ).all()
        return {
            "tasks": {"today": task_counts[0], "in_progress": task_counts[1], "overdue": task_counts[2], "pending_review": task_counts[3]},
            "content": {"total": topic_counts[0], "pending_creation": topic_counts[1], "in_production": topic_counts[2], "published": topic_counts[3]},
            "keywords": {"total": keyword_counts[0], "high_commercial_intent": keyword_counts[1], "unused": keyword_counts[2], "recently_added": keyword_counts[3]},
            "accounts": {
                "total": account_total,
                "platform_distribution": dict(platforms),
                "recently_updated": (
                    {"id": recent_account.id, "account_name": recent_account.account_name, "platform": recent_account.platform, "updated_at": recent_account.updated_at}
                    if recent_account else None
                ),
            },
            "knowledge": {
                "total": knowledge_counts[0],
                "category_count": knowledge_counts[1],
                "recently_updated": (
                    {"id": recent_knowledge.id, "title": recent_knowledge.title, "category": recent_knowledge.category, "updated_at": recent_knowledge.updated_at}
                    if recent_knowledge else None
                ),
            },
            "today_tasks": [
                {"id": task.id, "title": task.title, "task_type": task.task_type, "account_name": account_name, "topic_title": topic_title, "priority": task.priority, "status": task.status, "deadline": task.deadline, "is_overdue": task.deadline is not None and task.deadline < now and task.status not in terminal_statuses}
                for task, account_name, topic_title in task_rows
            ],
            "review_reminders": [
                {"id": review.id, "title": review.title, "task_title": task_title, "review_date": review.review_date, "problem_summary": review.problem}
                for review, task_title in review_rows
            ],
        }
