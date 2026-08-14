from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models import Keyword


class KeywordRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    @staticmethod
    def filters(organization_id: UUID, **params):
        values = [Keyword.organization_id == organization_id, Keyword.is_deleted.is_(False)]
        for field in (
            "platform",
            "source",
            "city",
            "school_stage",
            "grade",
            "subject",
            "search_intent",
            "commercial_intent",
            "content_status",
            "status",
        ):
            if value := params.get(field):
                values.append(getattr(Keyword, field) == value)
        if search := params.get("search"):
            values.append(
                or_(
                    Keyword.keyword.contains(search, autoescape=True),
                    Keyword.pain_point.contains(search, autoescape=True),
                    Keyword.notes.contains(search, autoescape=True),
                )
            )
        return values

    def list(
        self,
        organization_id: UUID,
        *,
        page: int,
        page_size: int,
        sort_by: str,
        sort_order: str,
        **params,
    ):
        where = self.filters(organization_id, **params)
        total = self.session.scalar(select(func.count(Keyword.id)).where(*where)) or 0
        column = {
            "updated_at": Keyword.updated_at,
            "created_at": Keyword.created_at,
            "keyword": Keyword.keyword,
        }[sort_by]
        order = column.asc() if sort_order == "asc" else column.desc()
        items = self.session.scalars(
            select(Keyword)
            .where(*where)
            .order_by(order, Keyword.id)
            .offset((page - 1) * page_size)
            .limit(page_size)
        ).all()
        return items, total

    def get(self, organization_id: UUID, keyword_id: UUID):
        return self.session.scalar(
            select(Keyword).where(
                Keyword.id == keyword_id,
                Keyword.organization_id == organization_id,
                Keyword.is_deleted.is_(False),
            )
        )

    def duplicate_exists(
        self, organization_id: UUID, normalized_keyword: str, exclude_id: UUID | None = None
    ) -> bool:
        statement = select(Keyword.id).where(
            Keyword.organization_id == organization_id,
            Keyword.normalized_keyword == normalized_keyword,
            Keyword.is_deleted.is_(False),
        )
        if exclude_id:
            statement = statement.where(Keyword.id != exclude_id)
        return self.session.scalar(statement) is not None

    def add(self, keyword: Keyword) -> None:
        self.session.add(keyword)

    def statistics(self, organization_id: UUID, **params):
        where = self.filters(organization_id, **params)
        return self.session.execute(
            select(
                func.count(Keyword.id),
                func.count(Keyword.id).filter(Keyword.commercial_intent == "高"),
                func.count(Keyword.id).filter(Keyword.content_status == "未使用"),
                func.count(Keyword.id).filter(Keyword.content_status == "已进入选题"),
                func.count(func.distinct(Keyword.platform)),
                func.count(func.distinct(Keyword.subject)),
            ).where(*where)
        ).one()
