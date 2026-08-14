from typing import Annotated
from uuid import UUID
from fastapi import APIRouter,Depends,Query,Response,status
from sqlalchemy.orm import Session
from app.api.dependencies import get_current_organization_id
from app.db.session import get_db
from app.schemas.operation import TaskWrite,ReviewWrite
from app.services.operation_task_service import OperationTaskService
from app.services.operation_review_service import OperationReviewService
Db=Annotated[Session,Depends(get_db)];Org=Annotated[UUID,Depends(get_current_organization_id)];tasks=APIRouter();reviews=APIRouter()
@tasks.get('')
def list_tasks(s:Db,org:Org,page:int=1,page_size:int=20,search:str|None=None,status_:str|None=Query(None,alias='status'),task_type:str|None=None,priority:str|None=None,assignee:str|None=None,related_account_id:UUID|None=None,related_topic_id:UUID|None=None):return OperationTaskService(s).list(org,page=page,page_size=page_size,search=search,status=status_,task_type=task_type,priority=priority,assignee=assignee,related_account_id=related_account_id,related_topic_id=related_topic_id)
@tasks.get('/stats')
def stats(s:Db,org:Org):return OperationTaskService(s).stats(org)
@tasks.post('',status_code=201)
def create(d:TaskWrite,s:Db,org:Org):return OperationTaskService(s).create(org,d)
@tasks.get('/{id}')
def get(id:UUID,s:Db,org:Org):return OperationTaskService(s).response(OperationTaskService(s).get(org,id))
@tasks.put('/{id}')
def update(id:UUID,d:TaskWrite,s:Db,org:Org):return OperationTaskService(s).update(org,id,d)
@tasks.delete('/{id}',status_code=204)
def delete(id:UUID,s:Db,org:Org):OperationTaskService(s).delete(org,id);return Response(status_code=204)
@reviews.get('')
def list_reviews(s:Db,org:Org,page:int=1,page_size:int=20,task_id:UUID|None=None,search:str|None=None):return OperationReviewService(s).list(org,page=page,page_size=page_size,task_id=task_id,search=search)
@reviews.get('/stats')
def review_stats(s:Db,org:Org):return OperationReviewService(s).stats(org)
@reviews.post('',status_code=201)
def create_review(d:ReviewWrite,s:Db,org:Org):return OperationReviewService(s).create(org,d)
@reviews.get('/{id}')
def get_review(id:UUID,s:Db,org:Org):return OperationReviewService(s).get(org,id)
@reviews.put('/{id}')
def update_review(id:UUID,d:ReviewWrite,s:Db,org:Org):return OperationReviewService(s).update(org,id,d)
@reviews.delete('/{id}',status_code=204)
def delete_review(id:UUID,s:Db,org:Org):OperationReviewService(s).delete(org,id);return Response(status_code=204)
