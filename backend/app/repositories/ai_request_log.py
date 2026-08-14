from datetime import datetime, time, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import AIRequestLog


class AIRequestLogRepository:
    def __init__(self, session: Session) -> None: self.session = session
    def add(self, item: AIRequestLog) -> None: self.session.add(item)
    def statistics(self, organization_id: UUID):
        start = datetime.combine(datetime.now(timezone.utc).date(), time.min, tzinfo=timezone.utc)
        return self.session.execute(select(func.count(AIRequestLog.id), func.count(AIRequestLog.id).filter(AIRequestLog.status == "success"), func.count(AIRequestLog.id).filter(AIRequestLog.status == "failed"), func.coalesce(func.sum(AIRequestLog.total_tokens), 0), func.avg(AIRequestLog.latency_ms)).where(AIRequestLog.organization_id == organization_id, AIRequestLog.created_at >= start)).one()
