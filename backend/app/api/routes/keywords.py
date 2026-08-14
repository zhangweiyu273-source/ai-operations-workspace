from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Query, Response, UploadFile, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_organization_id
from app.db.session import get_db
from app.schemas.keyword import (
    KeywordCreate,
    KeywordFilters,
    KeywordImportResult,
    KeywordListQuery,
    KeywordListResponse,
    KeywordResponse,
    KeywordStatistics,
    KeywordUpdate,
)
from app.services.keyword import KeywordService

router = APIRouter()
Db = Annotated[Session, Depends(get_db)]
Org = Annotated[UUID, Depends(get_current_organization_id)]


@router.get("", response_model=KeywordListResponse)
def list_keywords(session: Db, organization_id: Org, query: Annotated[KeywordListQuery, Query()]):
    return KeywordService(session).list_keywords(
        organization_id,
        page=query.page,
        page_size=query.page_size,
        sort_by=query.sort_by,
        sort_order=query.sort_order,
        **query.filter_kwargs(),
    )


@router.get("/stats", response_model=KeywordStatistics)
def stats(session: Db, organization_id: Org, filters: Annotated[KeywordFilters, Query()]):
    return KeywordService(session).statistics(organization_id, **filters.repository_kwargs())


@router.post("/import", response_model=KeywordImportResult)
async def import_keywords(
    session: Db, organization_id: Org, file: Annotated[UploadFile, File()], confirm: bool = False
):
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        return Response(status_code=413)
    return KeywordService(session).import_file(
        organization_id, file.filename or "", content, confirm
    )


@router.get("/export")
def export_keywords(session: Db, organization_id: Org, filters: Annotated[KeywordFilters, Query()]):
    return Response(
        content=KeywordService(session)
        .export_csv(organization_id, **filters.repository_kwargs())
        .encode("utf-8"),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="keywords.csv"'},
    )


@router.post("", response_model=KeywordResponse, status_code=status.HTTP_201_CREATED)
def create(data: KeywordCreate, session: Db, organization_id: Org):
    return KeywordService(session).create(organization_id, data)


@router.get("/{keyword_id}", response_model=KeywordResponse)
def get(keyword_id: UUID, session: Db, organization_id: Org):
    return KeywordResponse.model_validate(KeywordService(session).get(organization_id, keyword_id))


@router.put("/{keyword_id}", response_model=KeywordResponse)
def update(keyword_id: UUID, data: KeywordUpdate, session: Db, organization_id: Org):
    return KeywordService(session).update(organization_id, keyword_id, data)


@router.delete("/{keyword_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete(keyword_id: UUID, session: Db, organization_id: Org):
    KeywordService(session).delete(organization_id, keyword_id)
    return Response(status_code=204)
