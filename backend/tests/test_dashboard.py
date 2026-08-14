from datetime import date, datetime, timedelta, timezone
from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_current_organization_id
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import Account, Keyword, Knowledge, OperationReview, OperationTask, Organization, Topic

ORG_ID = UUID("00000000-0000-4000-8000-000000000099")


def client_with_session(session: Session) -> TestClient:
    def override_db():
        yield session

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_organization_id] = lambda: ORG_ID
    return TestClient(app)


def test_dashboard_returns_empty_organization_data() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    with sessionmaker(bind=engine, expire_on_commit=False)() as session:
        session.add(Organization(id=ORG_ID, name="仪表盘空组织")); session.commit()
        client = client_with_session(session)
        response = client.get("/api/v1/dashboard")
        assert response.status_code == 200
        body = response.json()
        assert body["tasks"] == {"today": 0, "in_progress": 0, "overdue": 0, "pending_review": 0}
        assert body["today_tasks"] == [] and body["review_reminders"] == []
    app.dependency_overrides.clear()


def test_dashboard_aggregates_real_data_and_limits_large_lists() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    with sessionmaker(bind=engine, expire_on_commit=False)() as session:
        session.add(Organization(id=ORG_ID, name="仪表盘测试组织"))
        account = Account(organization_id=ORG_ID, platform="小红书", account_name="数学账号", account_type="老师IP", status="启用")
        session.add(account); session.flush()
        topic = Topic(organization_id=ORG_ID, title="数学提分选题", platform="小红书", account_id=account.id, content_type="图文", status="待创作", priority="高")
        session.add(topic)
        session.add_all([
            Keyword(organization_id=ORG_ID, keyword=f"数学关键词{i}", normalized_keyword=f"数学关键词{i}", commercial_intent="高" if i < 2 else "中", content_status="未使用" if i < 3 else "已进入选题")
            for i in range(30)
        ])
        session.add(Knowledge(organization_id=ORG_ID, title="课程资料", category="课程资料", content="课程介绍", priority="高", status="启用"))
        session.flush()
        now = datetime.now(timezone.utc)
        today_task = OperationTask(organization_id=ORG_ID, title="今日制作", task_type="内容创作", related_topic_id=topic.id, related_account_id=account.id, status="进行中", priority="高", assignee="张老师", start_date=date.today(), deadline=now + timedelta(hours=2))
        overdue_task = OperationTask(organization_id=ORG_ID, title="逾期发布", task_type="内容发布", status="待开始", priority="中", deadline=now - timedelta(days=1))
        completed_task = OperationTask(organization_id=ORG_ID, title="待复盘任务", task_type="数据分析", status="已完成", priority="中", completed_at=now)
        session.add_all([today_task, overdue_task, completed_task]); session.flush()
        session.add(OperationReview(organization_id=ORG_ID, task_id=today_task.id, title="数据问题复盘", review_date=date.today(), problem="互动率偏低"))
        session.commit()
        client = client_with_session(session)
        response = client.get("/api/v1/dashboard")
        assert response.status_code == 200
        body = response.json()
        assert body["tasks"] == {"today": 1, "in_progress": 1, "overdue": 1, "pending_review": 1}
        assert body["content"] == {"total": 1, "pending_creation": 1, "in_production": 0, "published": 0}
        assert body["keywords"] == {"total": 30, "high_commercial_intent": 2, "unused": 3, "recently_added": 30}
        assert body["accounts"]["platform_distribution"] == {"小红书": 1}
        assert body["knowledge"]["category_count"] == 1
        assert body["today_tasks"][0]["account_name"] == "数学账号"
        assert body["today_tasks"][0]["topic_title"] == "数学提分选题"
        assert body["review_reminders"][0]["problem_summary"] == "互动率偏低"
        assert len(body["today_tasks"]) <= 8 and len(body["review_reminders"]) <= 5
    app.dependency_overrides.clear()
