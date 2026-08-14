from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_current_organization_id
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import Account, Keyword, Organization, Topic, TopicKeyword

ORG_ID = UUID("00000000-0000-4000-8000-000000000096")


def make_client() -> tuple[TestClient, sessionmaker[Session], tuple[Account, Keyword, Keyword]]:
    engine = create_engine("sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    maker = sessionmaker(bind=engine, expire_on_commit=False)
    with maker() as session:
        organization = Organization(id=ORG_ID, name="选题测试组织")
        account = Account(organization_id=ORG_ID, platform="小红书", account_name="测试账号", account_type="品牌账号", status="启用")
        other = Account(organization_id=ORG_ID, platform="抖音", account_name="抖音账号", account_type="老师IP", status="启用")
        keyword_1 = Keyword(organization_id=ORG_ID, keyword="广州初中数学补课", normalized_keyword="广州初中数学补课", platform="小红书", status="启用")
        keyword_2 = Keyword(organization_id=ORG_ID, keyword="初三数学提分", normalized_keyword="初三数学提分", platform="小红书", status="启用")
        session.add_all([organization, account, other, keyword_1, keyword_2])
        session.commit()
        ids = (account.id, keyword_1.id, keyword_2.id)

    def db():
        with maker() as session:
            yield session

    app.dependency_overrides[get_db] = db
    app.dependency_overrides[get_current_organization_id] = lambda: ORG_ID
    with maker() as session:
        return TestClient(app), maker, (session.get(Account, ids[0]), session.get(Keyword, ids[1]), session.get(Keyword, ids[2]))


def payload(account_id, keyword_ids, **changes):
    value = {"title": "孩子数学成绩一直50分，问题到底在哪里？", "platform": "小红书", "account_id": str(account_id), "content_type": "图文", "status": "待创作", "target_user": "初三家长", "subject": "数学", "priority": "高", "pain_point": "成绩低", "notes": "搜索获客", "keyword_ids": [str(v) for v in keyword_ids]}
    value.update(changes)
    return value


def test_topic_crud_filters_pagination_stats_and_soft_delete():
    client, maker, (account, keyword_1, keyword_2) = make_client()
    with client:
        created = client.post("/api/v1/topics", json=payload(account.id, [keyword_1.id, keyword_2.id]))
        assert created.status_code == 201
        topic_a = created.json()
        assert topic_a["keyword_count"] == 2 and set(topic_a["keyword_ids"]) == {str(keyword_1.id), str(keyword_2.id)}
        topic_b = client.post("/api/v1/topics", json=payload(account.id, [keyword_1.id], title="初三数学如何提分", status="制作中", priority="中")).json()
        assert client.get(f"/api/v1/topics/{topic_a['id']}").json()["title"] == topic_a["title"]
        updated = client.put(f"/api/v1/topics/{topic_a['id']}", json=payload(account.id, [keyword_1.id], title="数学50分的根因", status="已发布"))
        assert updated.status_code == 200 and updated.json()["status"] == "已发布" and updated.json()["keyword_count"] == 1
        for query in ("search=根因", "platform=小红书", f"account_id={account.id}", "status=已发布", "content_type=图文", "subject=数学", "priority=高"):
            assert client.get(f"/api/v1/topics?{query}").json()["total"] >= 1
        page = client.get("/api/v1/topics?page=2&page_size=1").json()
        assert page["page"] == 2 and page["page_size"] == 1 and page["total"] == 2 and len(page["items"]) == 1
        stats = client.get("/api/v1/topics/stats").json()
        assert stats["total"] == 2 and stats["published"] == 1 and stats["in_production"] == 1 and stats["platform_count"] == 1
        assert client.delete(f"/api/v1/topics/{topic_a['id']}").status_code == 204
        assert client.get(f"/api/v1/topics/{topic_a['id']}").status_code == 404
    with maker() as session:
        deleted = session.get(Topic, UUID(topic_a["id"]))
        assert deleted and deleted.is_deleted
        # Soft deletion keeps the historical association; Topic B's shared keyword remains intact.
        assert session.scalar(select(TopicKeyword).where(TopicKeyword.topic_id == UUID(topic_b["id"]))) is not None


def test_topic_keyword_many_to_many_add_remove_and_validation():
    client, maker, (account, keyword_1, keyword_2) = make_client()
    with client:
        topic_a = client.post("/api/v1/topics", json=payload(account.id, [keyword_1.id, keyword_2.id])).json()
        topic_b = client.post("/api/v1/topics", json=payload(account.id, [keyword_1.id], title="第二个选题")).json()
        assert client.delete(f"/api/v1/topics/{topic_a['id']}/keywords/{keyword_2.id}").status_code == 204
        assert client.get(f"/api/v1/topics/{topic_a['id']}").json()["keyword_ids"] == [str(keyword_1.id)]
        assert client.post(f"/api/v1/topics/{topic_a['id']}/keywords?keyword_id={keyword_2.id}").status_code == 200
        assert client.post(f"/api/v1/topics/{topic_a['id']}/keywords?keyword_id=00000000-0000-4000-8000-000000000777").status_code == 404
        assert client.post("/api/v1/topics", json=payload("00000000-0000-4000-8000-000000000778", [])).status_code == 400
        assert client.post("/api/v1/topics", json=payload(account.id, ["00000000-0000-4000-8000-000000000779"])).status_code == 400
    with maker() as session:
        links = session.scalars(select(TopicKeyword).where(TopicKeyword.keyword_id == keyword_1.id)).all()
        assert {str(link.topic_id) for link in links} == {topic_a["id"], topic_b["id"]}
