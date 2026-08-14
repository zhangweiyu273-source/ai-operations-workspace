from datetime import datetime, timedelta, timezone
from uuid import UUID
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session
from app.models import Knowledge, KnowledgeTag

class KnowledgeRepository:
 def __init__(self, session: Session): self.session=session
 def filters(self, org: UUID, **p):
  values=[Knowledge.organization_id==org, Knowledge.is_deleted.is_(False)]
  for field in ("category","status","priority"):
   if p.get(field): values.append(getattr(Knowledge,field)==p[field])
  if p.get("tag"): values.append(Knowledge.id.in_(select(KnowledgeTag.knowledge_id).where(KnowledgeTag.tag_name==p["tag"])))
  if p.get("search"): values.append(or_(Knowledge.title.contains(p["search"],autoescape=True),Knowledge.content.contains(p["search"],autoescape=True),Knowledge.summary.contains(p["search"],autoescape=True)))
  return values
 def get(self, org,id): return self.session.scalar(select(Knowledge).where(Knowledge.id==id,Knowledge.organization_id==org,Knowledge.is_deleted.is_(False)))
 def list(self,org,*,page,page_size,**p):
  w=self.filters(org,**p); total=self.session.scalar(select(func.count(Knowledge.id)).where(*w)) or 0
  return self.session.scalars(select(Knowledge).where(*w).order_by(Knowledge.updated_at.desc(),Knowledge.id).offset((page-1)*page_size).limit(page_size)).all(),total
 def tags(self,id): return self.session.scalars(select(KnowledgeTag.tag_name).where(KnowledgeTag.knowledge_id==id).order_by(KnowledgeTag.tag_name)).all()
 def stats(self,org):
  w=self.filters(org); cutoff=datetime.now(timezone.utc)-timedelta(days=7); return self.session.execute(select(func.count(Knowledge.id),func.count(func.distinct(Knowledge.category)),func.count(Knowledge.id).filter(Knowledge.priority=="高"),func.count(Knowledge.id).filter(Knowledge.updated_at>=cutoff)).where(*w)).one()
