"""Create keyword asset table.

Revision ID: 20260814_0004
Revises: 20260814_0003
Create Date: 2026-08-14
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260814_0004"
down_revision: str | Sequence[str] | None = "20260814_0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "keywords",
        sa.Column("keyword", sa.String(length=255), nullable=False),
        sa.Column("normalized_keyword", sa.String(length=255), nullable=False),
        sa.Column("platform", sa.String(length=30)),
        sa.Column("source", sa.String(length=50)),
        sa.Column("city", sa.String(length=60)),
        sa.Column("school_stage", sa.String(length=30)),
        sa.Column("grade", sa.String(length=30)),
        sa.Column("subject", sa.String(length=30)),
        sa.Column("need_type", sa.String(length=60)),
        sa.Column("pain_point", sa.Text()),
        sa.Column("search_intent", sa.String(length=40)),
        sa.Column("commercial_intent", sa.String(length=10)),
        sa.Column("content_status", sa.String(length=30)),
        sa.Column("status", sa.String(length=20), server_default="启用", nullable=False),
        sa.Column("notes", sa.Text()),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("created_by", sa.Uuid()), sa.Column("updated_by", sa.Uuid()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("is_deleted", sa.Boolean(), server_default="false", nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], name=op.f("fk_keywords_organization_id_organizations")),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], name=op.f("fk_keywords_created_by_users")),
        sa.ForeignKeyConstraint(["updated_by"], ["users.id"], name=op.f("fk_keywords_updated_by_users")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_keywords")),
    )
    for name, columns in (
        ("ix_keywords_org_platform", ["organization_id", "platform"]),
        ("ix_keywords_org_city", ["organization_id", "city"]),
        ("ix_keywords_org_subject", ["organization_id", "subject"]),
        ("ix_keywords_org_deleted", ["organization_id", "is_deleted"]),
        (op.f("ix_keywords_organization_id"), ["organization_id"]),
    ): op.create_index(name, "keywords", columns)
    op.create_index("uq_keywords_active_normalized", "keywords", ["organization_id", "normalized_keyword"], unique=True, postgresql_where=sa.text("is_deleted = false"))


def downgrade() -> None:
    op.drop_index("uq_keywords_active_normalized", table_name="keywords")
    op.drop_index(op.f("ix_keywords_organization_id"), table_name="keywords")
    op.drop_index("ix_keywords_org_deleted", table_name="keywords")
    op.drop_index("ix_keywords_org_subject", table_name="keywords")
    op.drop_index("ix_keywords_org_city", table_name="keywords")
    op.drop_index("ix_keywords_org_platform", table_name="keywords")
    op.drop_table("keywords")
