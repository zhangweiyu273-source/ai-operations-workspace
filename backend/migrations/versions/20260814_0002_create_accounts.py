"""Create account matrix table.

Revision ID: 20260814_0002
Revises: 20260814_0001
Create Date: 2026-08-14
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260814_0002"
down_revision: str | Sequence[str] | None = "20260814_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "accounts",
        sa.Column("platform", sa.String(length=30), nullable=False),
        sa.Column("account_name", sa.String(length=120), nullable=False),
        sa.Column("account_url", sa.String(length=500), nullable=True),
        sa.Column("account_avatar", sa.String(length=500), nullable=True),
        sa.Column("account_type", sa.String(length=40), nullable=False),
        sa.Column("positioning", sa.String(length=255), nullable=True),
        sa.Column("target_user", sa.String(length=255), nullable=True),
        sa.Column("operator", sa.String(length=100), nullable=True),
        sa.Column("status", sa.String(length=20), server_default="启用", nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("created_by", sa.Uuid(), nullable=True),
        sa.Column("updated_by", sa.Uuid(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("is_deleted", sa.Boolean(), server_default="false", nullable=False),
        sa.CheckConstraint(
            "status IN ('启用', '停用', '测试中')", name=op.f("ck_accounts_valid_status")
        ),
        sa.ForeignKeyConstraint(
            ["created_by"], ["users.id"], name=op.f("fk_accounts_created_by_users")
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name=op.f("fk_accounts_organization_id_organizations"),
        ),
        sa.ForeignKeyConstraint(
            ["updated_by"], ["users.id"], name=op.f("fk_accounts_updated_by_users")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_accounts")),
    )
    op.create_index("ix_accounts_org_deleted", "accounts", ["organization_id", "is_deleted"])
    op.create_index("ix_accounts_org_platform", "accounts", ["organization_id", "platform"])
    op.create_index("ix_accounts_org_status", "accounts", ["organization_id", "status"])
    op.create_index(op.f("ix_accounts_organization_id"), "accounts", ["organization_id"])


def downgrade() -> None:
    op.drop_index(op.f("ix_accounts_organization_id"), table_name="accounts")
    op.drop_index("ix_accounts_org_status", table_name="accounts")
    op.drop_index("ix_accounts_org_platform", table_name="accounts")
    op.drop_index("ix_accounts_org_deleted", table_name="accounts")
    op.drop_table("accounts")
