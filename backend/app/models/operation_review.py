from datetime import date
from uuid import UUID
from sqlalchemy import Date, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, BusinessModelMixin
class OperationReview(BusinessModelMixin, Base):
 __tablename__="operation_reviews"; __table_args__=(Index("ix_reviews_org_date","organization_id","review_date"),)
 task_id:Mapped[UUID]=mapped_column(ForeignKey("operation_tasks.id"),nullable=False); title:Mapped[str]=mapped_column(String(255),nullable=False); review_date:Mapped[date]=mapped_column(Date,nullable=False); goal:Mapped[str|None]=mapped_column(Text); result:Mapped[str|None]=mapped_column(Text); problem:Mapped[str|None]=mapped_column(Text); reason:Mapped[str|None]=mapped_column(Text); improvement:Mapped[str|None]=mapped_column(Text); next_action:Mapped[str|None]=mapped_column(Text)
