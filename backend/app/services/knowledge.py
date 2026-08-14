import logging
from uuid import UUID
from sqlalchemy import delete
from sqlalchemy.orm import Session
from app.core.exceptions import AppError
from app.models import Knowledge, KnowledgeTag
from app.repositories.knowledge import KnowledgeRepository
from app.schemas.knowledge import KnowledgeCreate, KnowledgeListResponse, KnowledgeResponse, KnowledgeStats, KnowledgeUpdate
logger=logging.getLogger(__name__)
CATEGORIES=["公司资料","课程资料","校区资料","老师资料","老板IP资料","用户洞察","销售话术","运营SOP","内容案例","行业资料","其他"]
class KnowledgeService:
 def __init__(self,s:Session): self.session=s; self.repo=KnowledgeRepository(s)
 def response(self,item): return KnowledgeResponse.model_validate({**item.__dict__,"tags":self.repo.tags(item.id)})
 def get(self,org,id):
  item=self.repo.get(org,id)
  if not item: raise AppError("知识不存在",404,"KNOWLEDGE_NOT_FOUND")
  return item
 def save(self,org,data,item=None):
  values=data.model_dump(exclude={"tags"})
  if item is None: item=Knowledge(organization_id=org,**values); self.session.add(item); self.session.flush()
  else:
   for key,value in values.items(): setattr(item,key,value)
  self.session.execute(delete(KnowledgeTag).where(KnowledgeTag.knowledge_id==item.id)); self.session.add_all([KnowledgeTag(knowledge_id=item.id,tag_name=t) for t in data.tags]); return item
 def create(self,org,data:KnowledgeCreate):
  try: item=self.save(org,data); self.session.commit(); self.session.refresh(item)
  except Exception: self.session.rollback(); logger.exception("Knowledge create failed organization_id=%s",org); raise
  return self.response(item)
 def update(self,org,id,data:KnowledgeUpdate):
  try: item=self.save(org,data,self.get(org,id)); self.session.commit(); self.session.refresh(item)
  except Exception: self.session.rollback(); logger.exception("Knowledge update failed organization_id=%s knowledge_id=%s",org,id); raise
  return self.response(item)
 def delete(self,org,id):
  try: self.get(org,id).is_deleted=True; self.session.commit()
  except Exception: self.session.rollback(); logger.exception("Knowledge delete failed organization_id=%s knowledge_id=%s",org,id); raise
 def list(self,org,**params):
  items,total=self.repo.list(org,**params); return KnowledgeListResponse.create(items=[self.response(v) for v in items],total=total,page=params["page"],page_size=params["page_size"])
 def stats(self,org):
  v=self.repo.stats(org); return KnowledgeStats(total=v[0],category_count=v[1],high_priority=v[2],recently_updated=v[3])
 def tags(self,org):
  return self.session.scalars(__import__('sqlalchemy').select(KnowledgeTag.tag_name).join(Knowledge,Knowledge.id==KnowledgeTag.knowledge_id).where(Knowledge.organization_id==org,Knowledge.is_deleted.is_(False)).distinct().order_by(KnowledgeTag.tag_name)).all()
