from collections.abc import Generator
from datetime import date
from io import BytesIO
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from openpyxl import Workbook
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_current_organization_id
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import Account, OperationMetric, Organization
from app.services.operation_metric import dedup_key

ORG_ID = UUID("00000000-0000-4000-8000-000000000088")
ACCOUNT_ID = UUID("00000000-0000-4000-8000-000000000188")
OTHER_ACCOUNT_ID = UUID("00000000-0000-4000-8000-000000000288")


@pytest.fixture
def factory() -> sessionmaker[Session]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    maker = sessionmaker(bind=engine, expire_on_commit=False)
    with maker() as session:
        session.add(Organization(id=ORG_ID, name="数据中心测试组织"))
        session.add_all(
            [
                Account(
                    id=ACCOUNT_ID,
                    organization_id=ORG_ID,
                    platform="小红书",
                    account_name="数据账号",
                    account_type="品牌账号",
                ),
                Account(
                    id=OTHER_ACCOUNT_ID,
                    organization_id=ORG_ID,
                    platform="抖音",
                    account_name="视频账号",
                    account_type="矩阵账号",
                ),
            ]
        )
        session.commit()
    return maker


@pytest.fixture
def client(factory: sessionmaker[Session]) -> Generator[TestClient, None, None]:
    def db():
        with factory() as session:
            yield session

    app.dependency_overrides[get_db] = db
    app.dependency_overrides[get_current_organization_id] = lambda: ORG_ID
    with TestClient(app) as value:
        yield value
    app.dependency_overrides.clear()


def payload(title="升学内容", account_id=ACCOUNT_ID, metric_date="2026-08-01"):
    return {
        "account_id": str(account_id),
        "metric_date": metric_date,
        "content_title": title,
        "content_type": "图文",
        "exposure": 100,
        "views": 80,
        "likes": 10,
        "comments": 2,
        "favorites": 3,
        "shares": 1,
        "private_messages": 4,
        "new_leads": 5,
        "valid_leads": 4,
        "high_intent_leads": 2,
        "trial_bookings": 1,
        "deals": 1,
        "revenue": "1999.90",
        "notes": "测试备注",
    }


def test_crud_persistence_platform_sync_and_soft_delete(client: TestClient, factory):
    created = client.post("/api/v1/operation-metrics", json=payload())
    assert created.status_code == 201
    item = created.json()
    assert item["platform"] == "小红书"
    updated = client.put(
        f"/api/v1/operation-metrics/{item['id']}", json=payload("更新内容", OTHER_ACCOUNT_ID)
    )
    assert updated.status_code == 200
    assert updated.json()["platform"] == "抖音"
    assert client.get(f"/api/v1/operation-metrics/{item['id']}").status_code == 200
    assert client.delete(f"/api/v1/operation-metrics/{item['id']}").status_code == 204
    assert client.get(f"/api/v1/operation-metrics/{item['id']}").status_code == 404
    with factory() as session:
        stored = session.scalar(
            select(OperationMetric).where(OperationMetric.id == UUID(item["id"]))
        )
        assert stored and stored.is_deleted is True and stored.platform == "抖音"


def test_filters_search_sort_and_pagination(client: TestClient):
    client.post("/api/v1/operation-metrics", json=payload("家长升学", ACCOUNT_ID, "2026-08-01"))
    client.post(
        "/api/v1/operation-metrics", json=payload("数学视频", OTHER_ACCOUNT_ID, "2026-08-02")
    )
    assert client.get("/api/v1/operation-metrics?search=家长").json()["total"] == 1
    assert client.get("/api/v1/operation-metrics?platform=抖音").json()["total"] == 1
    assert client.get(f"/api/v1/operation-metrics?account_id={ACCOUNT_ID}").json()["total"] == 1
    assert (
        client.get("/api/v1/operation-metrics?date_from=2026-08-02&date_to=2026-08-02").json()[
            "total"
        ]
        == 1
    )
    page = client.get(
        "/api/v1/operation-metrics?page=2&page_size=1&sort_by=views&sort_order=desc"
    ).json()
    assert page["total"] == 2 and page["total_pages"] == 2 and len(page["items"]) == 1


def test_statistics_and_zero_denominators(client: TestClient):
    zero = client.get("/api/v1/operation-metrics/statistics").json()
    assert zero["interaction_rate"] == "0.00"
    client.post("/api/v1/operation-metrics", json=payload())
    stats = client.get("/api/v1/operation-metrics/statistics").json()
    assert stats["exposure"] == 100 and stats["interactions"] == 16
    assert stats["interaction_rate"] == "20.00"
    assert stats["valid_lead_rate"] == "80.00"
    assert stats["revenue"] == "1999.90"


def csv_content(rows: list[str]) -> bytes:
    header = "日期,账号,内容标题,曝光,播放,点赞,评论,收藏,分享,私信,新增线索,有效线索,高意向,试听,成交,成交金额,备注\n"
    return (header + "\n".join(rows)).encode("utf-8-sig")


def test_csv_preview_confirm_duplicate_and_export(client: TestClient):
    content = csv_content(["2026-08-03,数据账号,CSV内容,100,80,10,2,3,1,4,5,4,2,1,1,99.90,正常"])
    preview = client.post(
        "/api/v1/operation-metrics/import", files={"file": ("metrics.csv", content, "text/csv")}
    ).json()
    assert preview["can_import"] and preview["success_count"] == 0 and len(preview["preview"]) == 1
    confirmed = client.post(
        "/api/v1/operation-metrics/import?confirm=true",
        files={"file": ("metrics.csv", content, "text/csv")},
    ).json()
    assert confirmed["success_count"] == 1
    duplicate = client.post(
        "/api/v1/operation-metrics/import?confirm=true",
        files={"file": ("metrics.csv", content, "text/csv")},
    ).json()
    assert duplicate["duplicate_count"] == 1 and duplicate["success_count"] == 0
    exported = client.get("/api/v1/operation-metrics/export?platform=小红书")
    assert exported.status_code == 200 and "CSV内容" in exported.content.decode("utf-8-sig")


def test_excel_import_and_atomic_invalid_batch(client: TestClient):
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["日期", "账号", "内容标题", "曝光", "成交金额"])
    sheet.append([date(2026, 8, 4), "数据账号", "Excel内容", 50, 88.8])
    stream = BytesIO()
    workbook.save(stream)
    result = client.post(
        "/api/v1/operation-metrics/import?confirm=true",
        files={
            "file": (
                "metrics.xlsx",
                stream.getvalue(),
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        },
    ).json()
    assert result["success_count"] == 1 and result["failed_count"] == 0
    invalid = csv_content(
        [
            "2026-08-05,数据账号,有效行,1,1,0,0,0,0,0,0,0,0,0,0,0,",
            "bad-date,不存在账号,错误行,-1,0,0,0,0,0,0,0,0,0,0,0,x,",
        ]
    )
    failed = client.post(
        "/api/v1/operation-metrics/import?confirm=true",
        files={"file": ("bad.csv", invalid, "text/csv")},
    ).json()
    assert (
        failed["can_import"] is False
        and failed["success_count"] == 0
        and failed["failed_count"] == 1
    )
    assert client.get("/api/v1/operation-metrics?search=有效行").json()["total"] == 0


def test_one_thousand_rows_list_filter_and_statistics(client: TestClient, factory):
    with factory() as session:
        session.add_all(
            [
                OperationMetric(
                    organization_id=ORG_ID,
                    account_id=ACCOUNT_ID,
                    metric_date=date(2026, 7, (index % 28) + 1),
                    platform="小红书",
                    content_title=f"规模数据{index}",
                    content_type="图文",
                    exposure=index,
                    views=index,
                    dedup_key=dedup_key(None, f"规模数据{index}"),
                )
                for index in range(1000)
            ]
        )
        session.commit()
    listed = client.get("/api/v1/operation-metrics?page=50&page_size=20").json()
    filtered = client.get("/api/v1/operation-metrics?search=规模数据99").json()
    stats = client.get("/api/v1/operation-metrics/statistics").json()
    assert listed["total"] == 1000 and len(listed["items"]) == 20
    assert filtered["total"] == 11
    assert stats["exposure"] == sum(range(1000))
