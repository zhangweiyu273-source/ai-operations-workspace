from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, File, Query, Response, UploadFile, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_organization_id
from app.db.session import get_db
from app.schemas.operation_metric import (
    ImportResult,
    MetricStatistics,
    OperationMetricCreate,
    OperationMetricFilters,
    OperationMetricListQuery,
    OperationMetricListResponse,
    OperationMetricResponse,
    OperationMetricUpdate,
)
from app.services.operation_metric import OperationMetricService

router = APIRouter()
Db = Annotated[Session, Depends(get_db)]
Org = Annotated[UUID, Depends(get_current_organization_id)]


@router.get("", response_model=OperationMetricListResponse)
def list_metrics(
    session: Db,
    organization_id: Org,
    query: Annotated[OperationMetricListQuery, Query()],
):
    return OperationMetricService(session).list_metrics(
        organization_id,
        page=query.page,
        page_size=query.page_size,
        sort_by=query.sort_by,
        sort_order=query.sort_order,
        **query.filter_kwargs(),
    )


@router.get("/statistics", response_model=MetricStatistics)
def statistics(
    session: Db,
    organization_id: Org,
    filters: Annotated[OperationMetricFilters, Query()],
):
    return OperationMetricService(session).statistics(
        organization_id,
        **filters.repository_kwargs(),
    )


@router.post("/import", response_model=ImportResult)
async def import_metrics(
    session: Db, organization_id: Org, file: Annotated[UploadFile, File()], confirm: bool = False
):
    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        return Response(status_code=413)
    return OperationMetricService(session).import_file(
        organization_id, file.filename or "", content, confirm
    )


@router.get("/export")
def export_metrics(
    session: Db,
    organization_id: Org,
    filters: Annotated[OperationMetricFilters, Query()],
):
    content = OperationMetricService(session).export_csv(
        organization_id,
        **filters.repository_kwargs(),
    )
    return Response(
        content=content.encode("utf-8"),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="operation-metrics.csv"'},
    )


@router.post("", response_model=OperationMetricResponse, status_code=status.HTTP_201_CREATED)
def create_metric(data: OperationMetricCreate, session: Db, organization_id: Org):
    return OperationMetricService(session).create(organization_id, data)


@router.get("/{metric_id}", response_model=OperationMetricResponse)
def get_metric(metric_id: UUID, session: Db, organization_id: Org):
    metric, name = OperationMetricService(session).get_metric(organization_id, metric_id)
    return OperationMetricService.response(metric, name)


@router.put("/{metric_id}", response_model=OperationMetricResponse)
def update_metric(metric_id: UUID, data: OperationMetricUpdate, session: Db, organization_id: Org):
    return OperationMetricService(session).update(organization_id, metric_id, data)


@router.delete("/{metric_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_metric(metric_id: UUID, session: Db, organization_id: Org):
    OperationMetricService(session).delete(organization_id, metric_id)
    return Response(status_code=204)
