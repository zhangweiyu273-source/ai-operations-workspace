import logging
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.exceptions import AppError
from app.models.account import Account
from app.repositories.account import AccountRepository
from app.schemas.account import (
    AccountCreate,
    AccountListResponse,
    AccountResponse,
    AccountSummary,
    AccountUpdate,
)

logger = logging.getLogger(__name__)


class AccountService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repository = AccountRepository(session)

    def list_accounts(
        self,
        organization_id: UUID,
        *,
        page: int,
        page_size: int,
        search: str | None,
        platform: str | None,
        account_type: str | None,
        status: str | None,
    ) -> AccountListResponse:
        items, total = self.repository.list(
            organization_id,
            page=page,
            page_size=page_size,
            search=search.strip() if search else None,
            platform=platform,
            account_type=account_type,
            status=status,
        )
        account_count, platform_count, active_count = self.repository.summary(organization_id)
        return AccountListResponse.create(
            items=[AccountResponse.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
            summary=AccountSummary(
                account_count=account_count,
                platform_count=platform_count,
                active_count=active_count,
            ),
        )

    def get_account(self, organization_id: UUID, account_id: UUID) -> Account:
        account = self.repository.get(organization_id, account_id)
        if account is None:
            raise AppError("账号不存在", status_code=404, code="ACCOUNT_NOT_FOUND")
        return account

    def create_account(self, organization_id: UUID, data: AccountCreate) -> Account:
        try:
            account = self.repository.create(organization_id, data)
            self.session.commit()
            self.session.refresh(account)
            return account
        except Exception:
            self.session.rollback()
            logger.exception("Account create failed organization_id=%s", organization_id)
            raise

    def update_account(
        self, organization_id: UUID, account_id: UUID, data: AccountUpdate
    ) -> Account:
        account = self.get_account(organization_id, account_id)
        try:
            self.repository.update(account, data)
            self.session.commit()
            self.session.refresh(account)
            return account
        except Exception:
            self.session.rollback()
            logger.exception(
                "Account update failed organization_id=%s account_id=%s",
                organization_id,
                account_id,
            )
            raise

    def delete_account(self, organization_id: UUID, account_id: UUID) -> None:
        account = self.get_account(organization_id, account_id)
        try:
            self.repository.soft_delete(account)
            self.session.commit()
        except Exception:
            self.session.rollback()
            logger.exception(
                "Account delete failed organization_id=%s account_id=%s",
                organization_id,
                account_id,
            )
            raise
