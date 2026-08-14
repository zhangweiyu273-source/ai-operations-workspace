from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.models.account import Account
from app.schemas.account import AccountCreate, AccountUpdate


class AccountRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    @staticmethod
    def _filters(
        organization_id: UUID,
        *,
        search: str | None = None,
        platform: str | None = None,
        account_type: str | None = None,
        status: str | None = None,
    ) -> list[object]:
        filters: list[object] = [
            Account.organization_id == organization_id,
            Account.is_deleted.is_(False),
        ]
        if search:
            filters.append(
                or_(
                    Account.account_name.contains(search, autoescape=True),
                    Account.positioning.contains(search, autoescape=True),
                    Account.target_user.contains(search, autoescape=True),
                )
            )
        if platform:
            filters.append(Account.platform == platform)
        if account_type:
            filters.append(Account.account_type == account_type)
        if status:
            filters.append(Account.status == status)
        return filters

    def list(
        self,
        organization_id: UUID,
        *,
        page: int,
        page_size: int,
        search: str | None,
        platform: str | None,
        account_type: str | None,
        status: str | None,
    ) -> tuple[list[Account], int]:
        filters = self._filters(
            organization_id,
            search=search,
            platform=platform,
            account_type=account_type,
            status=status,
        )
        total = self.session.scalar(select(func.count(Account.id)).where(*filters)) or 0
        statement = (
            select(Account)
            .where(*filters)
            .order_by(Account.updated_at.desc(), Account.id)
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        return list(self.session.scalars(statement)), total

    def summary(self, organization_id: UUID) -> tuple[int, int, int]:
        base = [Account.organization_id == organization_id, Account.is_deleted.is_(False)]
        account_count = self.session.scalar(select(func.count(Account.id)).where(*base)) or 0
        platform_count = (
            self.session.scalar(select(func.count(func.distinct(Account.platform))).where(*base))
            or 0
        )
        active_count = (
            self.session.scalar(
                select(func.count(Account.id)).where(*base, Account.status == "启用")
            )
            or 0
        )
        return account_count, platform_count, active_count

    def get(self, organization_id: UUID, account_id: UUID) -> Account | None:
        return self.session.scalar(
            select(Account).where(
                Account.id == account_id,
                Account.organization_id == organization_id,
                Account.is_deleted.is_(False),
            )
        )

    def create(self, organization_id: UUID, data: AccountCreate) -> Account:
        account = Account(organization_id=organization_id, **data.model_dump(mode="json"))
        self.session.add(account)
        self.session.flush()
        return account

    def update(self, account: Account, data: AccountUpdate) -> Account:
        for field, value in data.model_dump(mode="json").items():
            setattr(account, field, value)
        self.session.flush()
        return account

    def soft_delete(self, account: Account) -> None:
        account.is_deleted = True
        self.session.flush()
