from io import BytesIO
from uuid import UUID

from fastapi.testclient import TestClient
from openpyxl import Workbook
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_current_organization_id
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import Keyword, Organization

ORG_ID = UUID("00000000-0000-4000-8000-000000000098")


def keyword_payload(keyword: str = "广州 初中 数学 补课"):
    return {
        "keyword": keyword,
        "platform": "小红书",
        "source": "人工录入",
        "city": "广州",
        "school_stage": "初中",
        "grade": "初三",
        "subject": "数学",
        "need_type": "提分",
        "pain_point": "家长希望短期提分",
        "search_intent": "机构寻找",
        "commercial_intent": "高",
        "content_status": "未使用",
        "status": "启用",
        "notes": "测试备注",
    }


def make_client() -> tuple[TestClient, sessionmaker[Session]]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    maker = sessionmaker(bind=engine, expire_on_commit=False)
    with maker() as session:
        session.add(Organization(id=ORG_ID, name="关键词测试组织"))
        session.commit()

    def db():
        with maker() as session:
            yield session

    app.dependency_overrides[get_db] = db
    app.dependency_overrides[get_current_organization_id] = lambda: ORG_ID
    return TestClient(app), maker


def test_keyword_crud_normalization_and_soft_delete():
    client, maker = make_client()
    with client:
        created = client.post("/api/v1/keywords", json=keyword_payload()).json()
        assert (
            client.post(
                "/api/v1/keywords", json=keyword_payload("  广州　初中   数学 补课  ")
            ).status_code
            == 409
        )
        updated = client.put(
            f"/api/v1/keywords/{created['id']}", json=keyword_payload("广州初三数学补课哪里好")
        )
        assert updated.status_code == 200 and updated.json()["keyword"] == "广州初三数学补课哪里好"
        assert client.get(f"/api/v1/keywords/{created['id']}").status_code == 200
        assert client.delete(f"/api/v1/keywords/{created['id']}").status_code == 204
        assert client.get(f"/api/v1/keywords/{created['id']}").status_code == 404
    with maker() as session:
        item = session.scalar(select(Keyword).where(Keyword.id == UUID(created["id"])))
        assert item and item.is_deleted


def test_keyword_filters_search_sort_pagination_and_statistics():
    client, _ = make_client()
    with client:
        first = keyword_payload("广州初中数学补课")
        second = {
            **keyword_payload("深圳初三英语冲刺"),
            "city": "深圳",
            "subject": "英语",
            "commercial_intent": "中",
            "content_status": "已进入选题",
            "platform": "抖音",
        }
        assert client.post("/api/v1/keywords", json=first).status_code == 201
        assert client.post("/api/v1/keywords", json=second).status_code == 201
        assert client.get("/api/v1/keywords?search=家长").json()["total"] == 2
        assert (
            client.get(
                "/api/v1/keywords?platform=小红书&source=人工录入&city=广州&school_stage=初中&grade=初三&subject=数学&search_intent=机构寻找&commercial_intent=高&content_status=未使用&status=启用"
            ).json()["total"]
            == 1
        )
        page = client.get(
            "/api/v1/keywords?page=2&page_size=1&sort_by=keyword&sort_order=asc"
        ).json()
        assert page["total"] == 2 and len(page["items"]) == 1
        stats = client.get("/api/v1/keywords/stats").json()
        assert stats == {
            "total": 2,
            "high_commercial_intent": 1,
            "unused": 1,
            "in_topics": 1,
            "platform_count": 2,
            "subject_count": 2,
        }


def csv_content(rows: list[str]) -> bytes:
    header = (
        "关键词,平台,来源,城市,学段,年级,学科,需求类型,痛点,搜索意图,商业意图,内容状态,状态,备注\n"
    )
    return (header + "\n".join(rows)).encode("utf-8-sig")


def test_keyword_csv_import_preview_duplicates_and_export():
    client, _ = make_client()
    content = csv_content(
        [
            "广州初中数学补课,小红书,搜索联想,广州,初中,初三,数学,提分,成绩下滑,机构寻找,高,未使用,启用,导入"
        ]
    )
    with client:
        preview = client.post(
            "/api/v1/keywords/import", files={"file": ("keywords.csv", content, "text/csv")}
        ).json()
        assert (
            preview["can_import"] and preview["success_count"] == 0 and len(preview["preview"]) == 1
        )
        assert (
            client.post(
                "/api/v1/keywords/import?confirm=true",
                files={"file": ("keywords.csv", content, "text/csv")},
            ).json()["success_count"]
            == 1
        )
        duplicate = client.post(
            "/api/v1/keywords/import?confirm=true",
            files={"file": ("keywords.csv", content, "text/csv")},
        ).json()
        assert duplicate["duplicate_count"] == 1 and duplicate["success_count"] == 0
        exported = client.get("/api/v1/keywords/export?platform=小红书")
        assert exported.status_code == 200 and "广州初中数学补课" in exported.content.decode(
            "utf-8-sig"
        )


def test_keyword_excel_import_and_invalid_batch_is_atomic():
    client, _ = make_client()
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(
        ["关键词", "平台", "来源", "城市", "学段", "年级", "学科", "商业意图", "内容状态", "状态"]
    )
    sheet.append(
        [
            "广州初三数学冲刺",
            "小红书",
            "Excel导入",
            "广州",
            "初中",
            "初三",
            "数学",
            "高",
            "未使用",
            "启用",
        ]
    )
    stream = BytesIO()
    workbook.save(stream)
    with client:
        assert (
            client.post(
                "/api/v1/keywords/import?confirm=true",
                files={
                    "file": (
                        "keywords.xlsx",
                        stream.getvalue(),
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    )
                },
            ).json()["success_count"]
            == 1
        )
        invalid = csv_content(
            [
                "有效关键词,小红书,人工录入,广州,初中,初三,数学,提分,痛点,机构寻找,高,未使用,启用,",
                "另一条,小红书,人工录入,广州,初中,初三,数学,提分,痛点,机构寻找,错误,未使用,启用,",
            ]
        )
        failed = client.post(
            "/api/v1/keywords/import?confirm=true",
            files={"file": ("invalid.csv", invalid, "text/csv")},
        ).json()
        assert (
            not failed["can_import"]
            and failed["success_count"] == 0
            and client.get("/api/v1/keywords?search=有效关键词").json()["total"] == 0
        )


def test_keyword_one_thousand_rows_performance_shape():
    client, maker = make_client()
    with maker() as session:
        session.add_all(
            [
                Keyword(
                    organization_id=ORG_ID,
                    keyword=f"广州初中数学关键词{index}",
                    normalized_keyword=f"广州初中数学关键词{index}",
                    city="广州",
                    school_stage="初中",
                    grade="初三",
                    subject="数学",
                    platform="小红书",
                    commercial_intent="高" if index % 2 else "中",
                    content_status="未使用",
                )
                for index in range(1000)
            ]
        )
        session.commit()
    with client:
        listed = client.get("/api/v1/keywords?page=50&page_size=20").json()
        filtered = client.get(
            "/api/v1/keywords?city=广州&school_stage=初中&subject=数学&commercial_intent=高"
        ).json()
        assert listed["total"] == 1000 and len(listed["items"]) == 20 and filtered["total"] == 500
