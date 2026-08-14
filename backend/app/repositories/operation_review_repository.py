from sqlalchemy import func,select,or_
from app.models import OperationReview
class OperationReviewRepository:
 def __init__(self,s):self.s=s
 def get(self,org,id):return self.s.scalar(select(OperationReview).where(OperationReview.id==id,OperationReview.organization_id==org,OperationReview.is_deleted.is_(False)))
 def add(self,v):self.s.add(v)
 def list(self,org,page,page_size,task_id=None,search=None):
  w=[OperationReview.organization_id==org,OperationReview.is_deleted.is_(False)];
  if task_id:w.append(OperationReview.task_id==task_id)
  if search:w.append(or_(OperationReview.title.contains(search),OperationReview.result.contains(search),OperationReview.problem.contains(search)))
  return self.s.scalars(select(OperationReview).where(*w).order_by(OperationReview.review_date.desc()).offset((page-1)*page_size).limit(page_size)).all(),self.s.scalar(select(func.count(OperationReview.id)).where(*w)) or 0
 def stats(self,org):return self.s.execute(select(func.count(OperationReview.id),func.max(OperationReview.review_date)).where(OperationReview.organization_id==org,OperationReview.is_deleted.is_(False))).one()
