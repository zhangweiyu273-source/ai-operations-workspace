from collections.abc import Generator
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_current_organization_id
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import Account, Organization

ORGANIZATION_ID = UUID("00000000-0000-4000-8000-000000000099")


@pytest.fixture
def session_factory() -> sessionmaker[Session]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    with factory() as session:
        session.add(Organization(id=ORGANIZATION_ID, name="账号测试组织"))
        session.commit()
    return factory


@pytest.fixture
def client(session_factory: sessionmaker[Session]) -> Generator[TestClient, None, None]:
    def override_db() -> Generator[Session, None, None]:
        with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_organization_id] = lambda: ORGANIZATION_ID
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def payload(name: str = "升学规划号", platform: str = "小红书") -> dict[str, str]:
    return {
        "platform": platform,
        "account_name": name,
        "account_url": "https://example.test/account",
        "account_type": "品牌账号",
        "positioning": "升学规划",
        "target_user": "初中家长",
        "operator": "运营负责人",
        "status": "启用",
        "description": "账号备注",
    }


def test_create_and_get_account(client: TestClient) -> None:
    created = client.post("/api/v1/accounts", json=payload())
    assert created.status_code == 201
    account = created.json()
    assert account["account_name"] == "升学规划号"
    assert account["organization_id"] == str(ORGANIZATION_ID)
    detail = client.get(f"/api/v1/accounts/{account['id']}")
    assert detail.status_code == 200
    assert detail.json()["positioning"] == "升学规划"


def test_list_and_search_accounts(client: TestClient) -> None:
    client.post("/api/v1/accounts", json=payload("数学老师号", "抖音"))
    client.post("/api/v1/accounts", json=payload("家庭教育号", "小红书"))
    listed = client.get("/api/v1/accounts?platform=抖音")
    assert listed.status_code == 200
    assert listed.json()["total"] == 1
    assert listed.json()["summary"] == {
        "account_count": 2,
        "platform_count": 2,
        "active_count": 2,
    }
    searched = client.get("/api/v1/accounts?search=家庭")
    assert searched.json()["total"] == 1
    assert searched.json()["items"][0]["account_name"] == "家庭教育号"


def test_update_account(client: TestClient) -> None:
    account_id = client.post("/api/v1/accounts", json=payload()).json()["id"]
    updated_payload = payload("更新后的账号", "视频号")
    updated_payload["status"] = "测试中"
    response = client.put(f"/api/v1/accounts/{account_id}", json=updated_payload)
    assert response.status_code == 200
    assert response.json()["account_name"] == "更新后的账号"
    assert response.json()["status"] == "测试中"


def test_delete_is_soft_delete(client: TestClient, session_factory: sessionmaker[Session]) -> None:
    account_id = client.post("/api/v1/accounts", json=payload()).json()["id"]
    assert client.delete(f"/api/v1/accounts/{account_id}").status_code == 204
    assert client.get(f"/api/v1/accounts/{account_id}").status_code == 404
    assert client.get("/api/v1/accounts").json()["total"] == 0
    with session_factory() as session:
        stored = session.scalar(select(Account).where(Account.id == UUID(account_id)))
        assert stored is not None
        assert stored.is_deleted is True


def test_pagination(client: TestClient) -> None:
    for index in range(3):
        client.post("/api/v1/accounts", json=payload(f"账号{index}"))
    first_page = client.get("/api/v1/accounts?page=1&page_size=2").json()
    second_page = client.get("/api/v1/accounts?page=2&page_size=2").json()
    assert first_page["total"] == 3
    assert first_page["total_pages"] == 2
    assert len(first_page["items"]) == 2
    assert len(second_page["items"]) == 1


def test_account_validation_and_not_found(client: TestClient) -> None:
    invalid = client.post("/api/v1/accounts", json={**payload(), "account_name": "  "})
    assert invalid.status_code == 422
    missing = client.get("/api/v1/accounts/00000000-0000-4000-8000-000000000777")
    assert missing.status_code == 404
    assert missing.json()["error"]["code"] == "ACCOUNT_NOT_FOUND"
