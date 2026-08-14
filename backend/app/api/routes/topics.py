from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_organization_id
from app.db.session import get_db
from app.schemas.topic import (
    TopicCreate,
    TopicFilters,
    TopicListQuery,
    TopicListResponse,
    TopicResponse,
    TopicStats,
    TopicUpdate,
)
from app.services.topic import TopicService

router = APIRouter()
Db = Annotated[Session, Depends(get_db)]
Org = Annotated[UUID, Depends(get_current_organization_id)]


@router.get("", response_model=TopicListResponse)
def list_topics(session: Db, organization_id: Org, query: Annotated[TopicListQuery, Query()]):
    return TopicService(session).list(
        organization_id,
        page=query.page,
        page_size=query.page_size,
        sort_by=query.sort_by,
        sort_order=query.sort_order,
        **query.filters(),
    )


@router.get("/stats", response_model=TopicStats)
def stats(session: Db, organization_id: Org, filters: Annotated[TopicFilters, Query()]):
    return TopicService(session).stats(organization_id, **filters.values())


@router.post("", response_model=TopicResponse, status_code=status.HTTP_201_CREATED)
def create(data: TopicCreate, session: Db, organization_id: Org):
    return TopicService(session).create(organization_id, data)


@router.get("/{topic_id}", response_model=TopicResponse)
def get(topic_id: UUID, session: Db, organization_id: Org):
    return TopicService(session).response(TopicService(session).get(organization_id, topic_id))


@router.put("/{topic_id}", response_model=TopicResponse)
def update(topic_id: UUID, data: TopicUpdate, session: Db, organization_id: Org):
    return TopicService(session).update(organization_id, topic_id, data)


@router.delete("/{topic_id}", status_code=204)
def delete(topic_id: UUID, session: Db, organization_id: Org):
    TopicService(session).delete(organization_id, topic_id)
    return Response(status_code=204)


@router.post("/{topic_id}/keywords", response_model=TopicResponse)
def add_keyword(topic_id: UUID, keyword_id: UUID, session: Db, organization_id: Org):
    return TopicService(session).add_keyword(organization_id, topic_id, keyword_id)


@router.delete("/{topic_id}/keywords/{keyword_id}", status_code=204)
def remove_keyword(topic_id: UUID, keyword_id: UUID, session: Db, organization_id: Org):
    TopicService(session).remove_keyword(organization_id, topic_id, keyword_id)
    return Response(status_code=204)
