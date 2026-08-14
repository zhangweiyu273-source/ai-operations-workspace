from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_organization_id
from app.db.session import get_db
from app.schemas.account import (
    AccountCreate,
    AccountListResponse,
    AccountResponse,
    AccountStatus,
    AccountUpdate,
)
from app.services.account import AccountService

router = APIRouter()
SessionDependency = Annotated[Session, Depends(get_db)]
OrganizationDependency = Annotated[UUID, Depends(get_current_organization_id)]


@router.get("", response_model=AccountListResponse)
def list_accounts(
    session: SessionDependency,
    organization_id: OrganizationDependency,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    search: Annotated[str | None, Query(max_length=120)] = None,
    platform: Annotated[str | None, Query(max_length=30)] = None,
    account_type: Annotated[str | None, Query(max_length=40)] = None,
    account_status: Annotated[AccountStatus | None, Query(alias="status")] = None,
) -> AccountListResponse:
    return AccountService(session).list_accounts(
        organization_id,
        page=page,
        page_size=page_size,
        search=search,
        platform=platform,
        account_type=account_type,
        status=account_status.value if account_status else None,
    )


@router.post("", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
def create_account(
    data: AccountCreate,
    session: SessionDependency,
    organization_id: OrganizationDependency,
) -> AccountResponse:
    return AccountResponse.model_validate(
        AccountService(session).create_account(organization_id, data)
    )


@router.get("/{account_id}", response_model=AccountResponse)
def get_account(
    account_id: UUID,
    session: SessionDependency,
    organization_id: OrganizationDependency,
) -> AccountResponse:
    return AccountResponse.model_validate(
        AccountService(session).get_account(organization_id, account_id)
    )


@router.put("/{account_id}", response_model=AccountResponse)
def update_account(
    account_id: UUID,
    data: AccountUpdate,
    session: SessionDependency,
    organization_id: OrganizationDependency,
) -> AccountResponse:
    return AccountResponse.model_validate(
        AccountService(session).update_account(organization_id, account_id, data)
    )


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(
    account_id: UUID,
    session: SessionDependency,
    organization_id: OrganizationDependency,
) -> Response:
    AccountService(session).delete_account(organization_id, account_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
