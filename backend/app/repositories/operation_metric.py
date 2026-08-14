from datetime import date
from uuid import UUID

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session

from app.models import Account, OperationMetric


class OperationMetricRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    @staticmethod
    def filters(
        organization_id: UUID,
        *,
        date_from: date | None = None,
        date_to: date | None = None,
        platform: str | None = None,
        account_id: UUID | None = None,
        content_type: str | None = None,
        search: str | None = None,
    ):
        values = [
            OperationMetric.organization_id == organization_id,
            OperationMetric.is_deleted.is_(False),
        ]
        if date_from:
            values.append(OperationMetric.metric_date >= date_from)
        if date_to:
            values.append(OperationMetric.metric_date <= date_to)
        if platform:
            values.append(OperationMetric.platform == platform)
        if account_id:
            values.append(OperationMetric.account_id == account_id)
        if content_type:
            values.append(OperationMetric.content_type == content_type)
        if search:
            values.append(
                or_(
                    OperationMetric.content_title.contains(search, autoescape=True),
                    OperationMetric.notes.contains(search, autoescape=True),
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
        **filters,
    ):
        where = self.filters(organization_id, **filters)
        total = self.session.scalar(select(func.count(OperationMetric.id)).where(*where)) or 0
        columns = {
            "date": OperationMetric.metric_date,
            "exposure": OperationMetric.exposure,
            "views": OperationMetric.views,
            "revenue": OperationMetric.revenue,
            "updated_at": OperationMetric.updated_at,
        }
        column = columns[sort_by]
        order = column.asc() if sort_order == "asc" else column.desc()
        statement = (
            select(OperationMetric, Account.account_name)
            .join(Account, Account.id == OperationMetric.account_id)
            .where(*where)
            .order_by(order, OperationMetric.id)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(self.session.execute(statement)), total

    def get(self, organization_id: UUID, metric_id: UUID):
        return self.session.execute(
            select(OperationMetric, Account.account_name)
            .join(Account, Account.id == OperationMetric.account_id)
            .where(
                OperationMetric.id == metric_id,
                OperationMetric.organization_id == organization_id,
                OperationMetric.is_deleted.is_(False),
            )
        ).first()

    def account(self, organization_id: UUID, account_id: UUID):
        return self.session.scalar(
            select(Account).where(
                Account.id == account_id,
                Account.organization_id == organization_id,
                Account.is_deleted.is_(False),
            )
        )

    def accounts_by_name(self, organization_id: UUID):
        rows = self.session.scalars(
            select(Account).where(
                Account.organization_id == organization_id, Account.is_deleted.is_(False)
            )
        ).all()
        result: dict[str, list[Account]] = {}
        for account in rows:
            result.setdefault(account.account_name, []).append(account)
        return result

    def duplicate_exists(
        self,
        organization_id: UUID,
        account_id: UUID,
        metric_date: date,
        dedup_key: str,
        exclude_id: UUID | None = None,
    ) -> bool:
        statement: Select = select(OperationMetric.id).where(
            OperationMetric.organization_id == organization_id,
            OperationMetric.account_id == account_id,
            OperationMetric.metric_date == metric_date,
            OperationMetric.dedup_key == dedup_key,
            OperationMetric.is_deleted.is_(False),
        )
        if exclude_id:
            statement = statement.where(OperationMetric.id != exclude_id)
        return self.session.scalar(statement) is not None

    def statistics(self, organization_id: UUID, **filters):
        where = self.filters(organization_id, **filters)
        sum_ = lambda column: func.coalesce(func.sum(column), 0)
        return self.session.execute(
            select(
                sum_(OperationMetric.exposure),
                sum_(OperationMetric.views),
                sum_(OperationMetric.likes),
                sum_(OperationMetric.comments),
                sum_(OperationMetric.favorites),
                sum_(OperationMetric.shares),
                sum_(OperationMetric.new_leads),
                sum_(OperationMetric.valid_leads),
                sum_(OperationMetric.high_intent_leads),
                sum_(OperationMetric.trial_bookings),
                sum_(OperationMetric.deals),
                sum_(OperationMetric.revenue),
            ).where(*where)
        ).one()

    def add(self, metric: OperationMetric):
        self.session.add(metric)
