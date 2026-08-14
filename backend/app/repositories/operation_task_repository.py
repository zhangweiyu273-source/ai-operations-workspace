from datetime import datetime
from sqlalchemy import func,select,or_
from app.models import OperationTask,Account,Topic
class OperationTaskRepository:
 def __init__(self,s):self.s=s
 def get(self,org,id):return self.s.scalar(select(OperationTask).where(OperationTask.id==id,OperationTask.organization_id==org,OperationTask.is_deleted.is_(False)))
 def account(self,org,id):return self.s.scalar(select(Account.id).where(Account.id==id,Account.organization_id==org,Account.is_deleted.is_(False)))
 def topic(self,org,id):return self.s.scalar(select(Topic.id).where(Topic.id==id,Topic.organization_id==org,Topic.is_deleted.is_(False)))
 def add(self,v):self.s.add(v)
 def list(self,org,page,page_size,**p):
  w=[OperationTask.organization_id==org,OperationTask.is_deleted.is_(False)]
  for k in ('status','task_type','priority','assignee','related_account_id','related_topic_id'):
   if p.get(k):w.append(getattr(OperationTask,k)==p[k])
  if p.get('search'):w.append(or_(OperationTask.title.contains(p['search']),OperationTask.description.contains(p['search'])))
  if p.get('deadline_from'):w.append(OperationTask.deadline>=p['deadline_from'])
  if p.get('deadline_to'):w.append(OperationTask.deadline<=p['deadline_to'])
  return self.s.scalars(select(OperationTask).where(*w).order_by(OperationTask.updated_at.desc()).offset((page-1)*page_size).limit(page_size)).all(),self.s.scalar(select(func.count(OperationTask.id)).where(*w)) or 0
 def stats(self,org,now):
  w=[OperationTask.organization_id==org,OperationTask.is_deleted.is_(False)];return self.s.execute(select(func.count(OperationTask.id),func.count(OperationTask.id).filter(OperationTask.status=='已完成'),func.count(OperationTask.id).filter(OperationTask.status=='进行中'),func.count(OperationTask.id).filter(OperationTask.deadline<now,OperationTask.status.not_in(['已完成','已取消']))).where(*w)).one()
