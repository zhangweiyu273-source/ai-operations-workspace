from datetime import date, datetime
from uuid import UUID
from sqlalchemy import Date, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, BusinessModelMixin
class OperationTask(BusinessModelMixin, Base):
 __tablename__="operation_tasks"; __table_args__=(Index("ix_tasks_org_status","organization_id","status"),Index("ix_tasks_org_deadline","organization_id","deadline"))
 title:Mapped[str]=mapped_column(String(255),nullable=False); description:Mapped[str|None]=mapped_column(Text); task_type:Mapped[str]=mapped_column(String(30),nullable=False); related_topic_id:Mapped[UUID|None]=mapped_column(ForeignKey("topics.id")); related_account_id:Mapped[UUID|None]=mapped_column(ForeignKey("accounts.id")); status:Mapped[str]=mapped_column(String(20),nullable=False,default="待开始",server_default="待开始"); priority:Mapped[str]=mapped_column(String(10),nullable=False,default="中",server_default="中"); assignee:Mapped[str|None]=mapped_column(String(100)); start_date:Mapped[date|None]=mapped_column(Date); deadline:Mapped[datetime|None]=mapped_column(DateTime(timezone=True)); completed_at:Mapped[datetime|None]=mapped_column(DateTime(timezone=True))
