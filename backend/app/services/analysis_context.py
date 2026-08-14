from datetime import date
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Account, Keyword, OperationMetric, OperationReview, OperationTask, Topic

CONTEXT_VERSION = "v1"


class AnalysisContextBuilder:
    """Produces bounded, factual aggregates. Never sends raw database records to a provider."""

    def __init__(self, session: Session) -> None:
        self.session = session

    @staticmethod
    def _filters(model, organization_id: UUID) -> list[object]:
        return [model.organization_id == organization_id, model.is_deleted.is_(False)]

    def build(self, organization_id: UUID, *, analysis_type: str, date_start: date | None, date_end: date | None, account_ids: list[UUID] | None, platform: str | None) -> dict:
        metric_filters = self._filters(OperationMetric, organization_id)
        if date_start: metric_filters.append(OperationMetric.metric_date >= date_start)
        if date_end: metric_filters.append(OperationMetric.metric_date <= date_end)
        if account_ids: metric_filters.append(OperationMetric.account_id.in_(account_ids))
        if platform: metric_filters.append(OperationMetric.platform == platform)
        totals = self.session.execute(select(
            func.count(OperationMetric.id), func.coalesce(func.sum(OperationMetric.exposure), 0), func.coalesce(func.sum(OperationMetric.views), 0),
            func.coalesce(func.sum(OperationMetric.likes + OperationMetric.comments + OperationMetric.favorites + OperationMetric.shares), 0),
            func.coalesce(func.sum(OperationMetric.valid_leads), 0), func.coalesce(func.sum(OperationMetric.trial_bookings), 0),
            func.coalesce(func.sum(OperationMetric.deals), 0), func.coalesce(func.sum(OperationMetric.revenue), 0),
        ).where(*metric_filters)).one()
        rows = self.session.execute(select(OperationMetric.content_title, OperationMetric.platform, OperationMetric.views, OperationMetric.exposure, OperationMetric.valid_leads, OperationMetric.deals)
            .where(*metric_filters).order_by(OperationMetric.views.desc(), OperationMetric.id).limit(5)).all()
        low_rows = self.session.execute(select(OperationMetric.content_title, OperationMetric.platform, OperationMetric.views, OperationMetric.exposure)
            .where(*metric_filters).order_by(OperationMetric.views.asc(), OperationMetric.id).limit(5)).all()
        platform_rows = self.session.execute(select(OperationMetric.platform, func.count(OperationMetric.id), func.coalesce(func.sum(OperationMetric.views), 0), func.coalesce(func.sum(OperationMetric.valid_leads), 0))
            .where(*metric_filters).group_by(OperationMetric.platform).order_by(func.sum(OperationMetric.views).desc())).all()
        keyword_filters = self._filters(Keyword, organization_id)
        keyword_summary = self.session.execute(select(func.count(Keyword.id), func.count(Keyword.id).filter(Keyword.commercial_intent == "高"), func.count(Keyword.id).filter(Keyword.content_status == "未使用"))
            .where(*keyword_filters)).one()
        topic_filters = self._filters(Topic, organization_id)
        topic_summary = self.session.execute(select(func.count(Topic.id), func.count(Topic.id).filter(Topic.status == "待创作"), func.count(Topic.id).filter(Topic.status == "已发布"))
            .where(*topic_filters)).one()
        task_filters = self._filters(OperationTask, organization_id)
        task_summary = self.session.execute(select(func.count(OperationTask.id), func.count(OperationTask.id).filter(OperationTask.status == "已完成"), func.count(OperationTask.id).filter(OperationTask.status == "进行中"))
            .where(*task_filters)).one()
        review_count = self.session.scalar(select(func.count(OperationReview.id)).where(*self._filters(OperationReview, organization_id))) or 0
        account_count = self.session.scalar(select(func.count(Account.id)).where(*self._filters(Account, organization_id))) or 0
        interaction = int(totals[3]); views = int(totals[2]); valid_leads = int(totals[4]); trials = int(totals[5]); deals = int(totals[6])
        return {
            "context_version": CONTEXT_VERSION, "analysis_type": analysis_type,
            "date_range": {"start": str(date_start) if date_start else None, "end": str(date_end) if date_end else None},
            "filters": {"platform": platform, "account_ids": [str(x) for x in account_ids or []]},
            "metrics": {"content_count": int(totals[0]), "total_exposure": int(totals[1]), "total_views": views, "total_interactions": interaction, "valid_leads": valid_leads, "trials": trials, "deals": deals, "revenue": float(totals[7]), "interaction_rate": round(interaction / views, 4) if views else 0, "lead_rate": round(valid_leads / views, 4) if views else 0, "trial_rate": round(trials / valid_leads, 4) if valid_leads else 0, "deal_rate": round(deals / trials, 4) if trials else 0},
            "top_content": [{"title": r[0], "platform": r[1], "views": int(r[2]), "exposure": int(r[3]), "valid_leads": int(r[4]), "deals": int(r[5])} for r in rows],
            "low_content": [{"title": r[0], "platform": r[1], "views": int(r[2]), "exposure": int(r[3])} for r in low_rows],
            "platform_summary": [{"platform": r[0], "content_count": int(r[1]), "views": int(r[2]), "valid_leads": int(r[3])} for r in platform_rows],
            "assets": {"accounts": account_count, "keywords": {"total": int(keyword_summary[0]), "high_commercial_intent": int(keyword_summary[1]), "unused": int(keyword_summary[2])}, "topics": {"total": int(topic_summary[0]), "pending_creation": int(topic_summary[1]), "published": int(topic_summary[2])}, "tasks": {"total": int(task_summary[0]), "completed": int(task_summary[1]), "in_progress": int(task_summary[2])}, "reviews": review_count},
        }
