"""Create operation metrics table.

Revision ID: 20260814_0003
Revises: 20260814_0002
Create Date: 2026-08-14
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260814_0003"
down_revision: str | Sequence[str] | None = "20260814_0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "operation_metrics",
        sa.Column("account_id", sa.Uuid(), nullable=False),
        sa.Column("metric_date", sa.Date(), nullable=False),
        sa.Column("platform", sa.String(length=30), nullable=False),
        sa.Column("content_title", sa.String(length=255), nullable=False),
        sa.Column("content_url", sa.String(length=500), nullable=True),
        sa.Column("content_type", sa.String(length=50), nullable=True),
        sa.Column("publish_time", sa.DateTime(timezone=True), nullable=True),
        *[
            sa.Column(name, sa.BigInteger(), server_default="0", nullable=False)
            for name in (
                "exposure",
                "views",
                "likes",
                "comments",
                "favorites",
                "shares",
                "private_messages",
                "new_leads",
                "valid_leads",
                "high_intent_leads",
                "trial_bookings",
                "deals",
            )
        ],
        sa.Column("revenue", sa.Numeric(precision=14, scale=2), server_default="0", nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("dedup_key", sa.String(length=64), nullable=False),
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
            "exposure >= 0 AND views >= 0 AND likes >= 0 AND comments >= 0",
            name=op.f("ck_operation_metrics_non_negative_primary_metrics"),
        ),
        sa.CheckConstraint(
            "favorites >= 0 AND shares >= 0 AND private_messages >= 0",
            name=op.f("ck_operation_metrics_non_negative_interactions"),
        ),
        sa.CheckConstraint(
            "new_leads >= 0 AND valid_leads >= 0 AND high_intent_leads >= 0",
            name=op.f("ck_operation_metrics_non_negative_leads"),
        ),
        sa.CheckConstraint(
            "trial_bookings >= 0 AND deals >= 0 AND revenue >= 0",
            name=op.f("ck_operation_metrics_non_negative_conversions"),
        ),
        sa.ForeignKeyConstraint(
            ["account_id"], ["accounts.id"], name=op.f("fk_operation_metrics_account_id_accounts")
        ),
        sa.ForeignKeyConstraint(
            ["created_by"], ["users.id"], name=op.f("fk_operation_metrics_created_by_users")
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name=op.f("fk_operation_metrics_organization_id_organizations"),
        ),
        sa.ForeignKeyConstraint(
            ["updated_by"], ["users.id"], name=op.f("fk_operation_metrics_updated_by_users")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_operation_metrics")),
    )
    op.create_index(
        "ix_operation_metrics_org_account", "operation_metrics", ["organization_id", "account_id"]
    )
    op.create_index(
        "ix_operation_metrics_org_date", "operation_metrics", ["organization_id", "metric_date"]
    )
    op.create_index(
        "ix_operation_metrics_org_deleted", "operation_metrics", ["organization_id", "is_deleted"]
    )
    op.create_index(
        "ix_operation_metrics_org_platform", "operation_metrics", ["organization_id", "platform"]
    )
    op.create_index(
        op.f("ix_operation_metrics_organization_id"), "operation_metrics", ["organization_id"]
    )
    op.create_index(
        "uq_operation_metrics_active_identity",
        "operation_metrics",
        ["organization_id", "account_id", "metric_date", "dedup_key"],
        unique=True,
        postgresql_where=sa.text("is_deleted = false"),
    )


def downgrade() -> None:
    op.drop_index("uq_operation_metrics_active_identity", table_name="operation_metrics")
    op.drop_index(op.f("ix_operation_metrics_organization_id"), table_name="operation_metrics")
    op.drop_index("ix_operation_metrics_org_platform", table_name="operation_metrics")
    op.drop_index("ix_operation_metrics_org_deleted", table_name="operation_metrics")
    op.drop_index("ix_operation_metrics_org_date", table_name="operation_metrics")
    op.drop_index("ix_operation_metrics_org_account", table_name="operation_metrics")
    op.drop_table("operation_metrics")
