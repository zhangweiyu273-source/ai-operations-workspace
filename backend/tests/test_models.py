from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.models import Account, Organization, User


def make_session() -> Session:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return Session(engine)


def test_organization_model_persists_uuid_and_timestamps() -> None:
    with make_session() as session:
        organization = Organization(name="测试组织")
        session.add(organization)
        session.commit()
        session.refresh(organization)

        assert organization.id is not None
        assert organization.name == "测试组织"
        assert organization.created_at is not None
        assert organization.updated_at is not None


def test_user_model_belongs_to_organization() -> None:
    with make_session() as session:
        organization = Organization(name="测试组织")
        user = User(
            organization=organization,
            name="管理员",
            email="admin@example.test",
            role="admin",
        )
        session.add(user)
        session.commit()
        session.refresh(user)

        assert user.id is not None
        assert user.organization_id == organization.id
        assert user.organization.name == "测试组织"
        assert user.is_active is True


def test_account_model_persists_and_soft_deletes() -> None:
    with make_session() as session:
        organization = Organization(name="账号模型测试组织")
        session.add(organization)
        session.flush()
        account = Account(
            organization_id=organization.id,
            platform="小红书",
            account_name="测试账号",
            account_type="品牌账号",
            status="启用",
        )
        session.add(account)
        session.commit()
        account.is_deleted = True
        session.commit()
        session.refresh(account)
        assert account.id is not None
        assert account.organization_id == organization.id
        assert account.is_deleted is True
