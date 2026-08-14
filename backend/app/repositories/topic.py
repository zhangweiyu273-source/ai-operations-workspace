from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models import Account, Keyword, Topic


class TopicRepository:
    def __init__(self, session: Session):
        self.session = session

    def where(self, org: UUID, **p):
        values = [Topic.organization_id == org, Topic.is_deleted.is_(False)]
        for f in (
            "platform",
            "account_id",
            "status",
            "content_type",
            "subject",
            "school_stage",
            "priority",
        ):
            if p.get(f):
                values.append(getattr(Topic, f) == p[f])
        if p.get("search"):
            values.append(
                or_(
                    Topic.title.contains(p["search"], autoescape=True),
                    Topic.pain_point.contains(p["search"], autoescape=True),
                    Topic.notes.contains(p["search"], autoescape=True),
                )
            )
        return values

    def account(self, org, id):
        return self.session.scalar(
            select(Account).where(
                Account.id == id, Account.organization_id == org, Account.is_deleted.is_(False)
            )
        )

    def keywords(self, org, ids):
        return (
            self.session.scalars(
                select(Keyword).where(
                    Keyword.organization_id == org,
                    Keyword.id.in_(ids),
                    Keyword.is_deleted.is_(False),
                )
            ).all()
            if ids
            else []
        )

    def get(self, org, id):
        return self.session.scalar(
            select(Topic).where(
                Topic.id == id, Topic.organization_id == org, Topic.is_deleted.is_(False)
            )
        )

    def list(self, org, *, page, page_size, sort_by, sort_order, **p):
        where = self.where(org, **p)
        total = self.session.scalar(select(func.count(Topic.id)).where(*where)) or 0
        col = {
            "updated_at": Topic.updated_at,
            "publish_date": Topic.publish_date,
            "priority": Topic.priority,
        }[sort_by]
        order = col.asc() if sort_order == "asc" else col.desc()
        return self.session.scalars(
            select(Topic)
            .where(*where)
            .order_by(order, Topic.id)
            .offset((page - 1) * page_size)
            .limit(page_size)
        ).all(), total

    def stats(self, org, **p):
        w = self.where(org, **p)
        return self.session.execute(
            select(
                func.count(Topic.id),
                func.count(Topic.id).filter(Topic.status == "待创作"),
                func.count(Topic.id).filter(Topic.status == "制作中"),
                func.count(Topic.id).filter(Topic.status == "已发布"),
                func.count(Topic.id).filter(Topic.status == "已复盘"),
                func.count(func.distinct(Topic.platform)),
            ).where(*w)
        ).one()
