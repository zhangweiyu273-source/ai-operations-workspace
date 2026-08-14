from uuid import UUID
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool
from app.api.dependencies import get_current_organization_id
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import Knowledge, Organization
ORG=UUID("00000000-0000-4000-8000-000000000095")
def client():
 e=create_engine("sqlite+pysqlite:///:memory:",connect_args={"check_same_thread":False},poolclass=StaticPool); Base.metadata.create_all(e); m=sessionmaker(bind=e,expire_on_commit=False)
 with m() as s:s.add(Organization(id=ORG,name="知识测试"));s.commit()
 def db():
  with m() as s:yield s
 app.dependency_overrides[get_db]=db;app.dependency_overrides[get_current_organization_id]=lambda:ORG;return TestClient(app),m
def data(title="课程优势",**v):
 x={"title":title,"category":"课程资料","content":"小班教学与分层辅导","summary":"课程摘要","priority":"高","status":"启用","tags":["数学","家长"]};x.update(v);return x
def test_knowledge_crud_search_filters_tags_stats_and_soft_delete():
 c,m=client()
 with c:
  a=c.post("/api/v1/knowledge",json=data()).json();b=c.post("/api/v1/knowledge",json=data("销售异议",category="销售话术",tags=["家长"],priority="中",content="异议处理话术")).json()
  assert c.get(f"/api/v1/knowledge/{a['id']}").json()["tags"]==["家长","数学"]
  assert c.get("/api/v1/knowledge?search=分层").json()["total"]==1
  for q in ("category=课程资料","priority=高","status=启用","tag=家长","page=2&page_size=1"): assert c.get("/api/v1/knowledge?"+q).status_code==200
  assert c.get("/api/v1/knowledge/stats").json()["total"]==2
  u=c.put(f"/api/v1/knowledge/{a['id']}",json=data("更新课程",tags=["英语"]));assert u.json()["tags"]==["英语"]
  assert c.delete(f"/api/v1/knowledge/{a['id']}").status_code==204;assert c.get(f"/api/v1/knowledge/{a['id']}").status_code==404
  assert "课程资料" in c.get("/api/v1/knowledge/categories").json()["items"] and "家长" in c.get("/api/v1/knowledge/tags").json()["items"]
 with m() as s: assert s.get(Knowledge,UUID(a["id"])).is_deleted
