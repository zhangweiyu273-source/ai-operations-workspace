from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session
from app.api.dependencies import get_current_organization_id
from app.db.session import get_db
from app.schemas.knowledge import KnowledgeCreate, KnowledgeListResponse, KnowledgeQuery, KnowledgeResponse, KnowledgeStats, KnowledgeUpdate
from app.services.knowledge import CATEGORIES, KnowledgeService
router=APIRouter(); Db=Annotated[Session,Depends(get_db)]; Org=Annotated[UUID,Depends(get_current_organization_id)]
@router.get("",response_model=KnowledgeListResponse)
def list_knowledge(session:Db,organization_id:Org,query:Annotated[KnowledgeQuery,Query()]): return KnowledgeService(session).list(organization_id,page=query.page,page_size=query.page_size,**query.filters())
@router.get("/categories")
def categories(): return {"items":CATEGORIES}
@router.get("/tags")
def tags(session:Db,organization_id:Org): return {"items":KnowledgeService(session).tags(organization_id)}
@router.get("/stats",response_model=KnowledgeStats)
def stats(session:Db,organization_id:Org): return KnowledgeService(session).stats(organization_id)
@router.post("",response_model=KnowledgeResponse,status_code=status.HTTP_201_CREATED)
def create(data:KnowledgeCreate,session:Db,organization_id:Org): return KnowledgeService(session).create(organization_id,data)
@router.get("/{knowledge_id}",response_model=KnowledgeResponse)
def get(knowledge_id:UUID,session:Db,organization_id:Org): return KnowledgeService(session).response(KnowledgeService(session).get(organization_id,knowledge_id))
@router.put("/{knowledge_id}",response_model=KnowledgeResponse)
def update(knowledge_id:UUID,data:KnowledgeUpdate,session:Db,organization_id:Org): return KnowledgeService(session).update(organization_id,knowledge_id,data)
@router.delete("/{knowledge_id}",status_code=204)
def delete_knowledge(knowledge_id:UUID,session:Db,organization_id:Org): KnowledgeService(session).delete(organization_id,knowledge_id); return Response(status_code=204)
