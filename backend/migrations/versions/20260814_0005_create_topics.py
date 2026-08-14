"""Create topics and topic keywords."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision = "20260814_0005"
down_revision = "20260814_0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade():
    op.create_table(
        "topics",
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("content_type", sa.String(30), nullable=False),
        sa.Column("platform", sa.String(30), nullable=False),
        sa.Column("account_id", sa.Uuid(), nullable=False),
        sa.Column("status", sa.String(20), server_default="待规划", nullable=False),
        sa.Column("target_user", sa.String(120)),
        sa.Column("school_stage", sa.String(30)),
        sa.Column("subject", sa.String(30)),
        sa.Column("city", sa.String(60)),
        sa.Column("pain_point", sa.Text()),
        sa.Column("content_goal", sa.String(40)),
        sa.Column("priority", sa.String(10), server_default="中", nullable=False),
        sa.Column("publish_date", sa.Date()),
        sa.Column("content_id", sa.String(100)),
        sa.Column("notes", sa.Text()),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("organization_id", sa.Uuid(), nullable=False),
        sa.Column("created_by", sa.Uuid()),
        sa.Column("updated_by", sa.Uuid()),
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
        sa.ForeignKeyConstraint(["account_id"], ["accounts.id"]),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_topics_org_platform", "topics", ["organization_id", "platform"])
    op.create_index("ix_topics_org_status", "topics", ["organization_id", "status"])
    op.create_index("ix_topics_org_account", "topics", ["organization_id", "account_id"])
    op.create_index("ix_topics_organization_id", "topics", ["organization_id"])
    op.create_table(
        "topic_keywords",
        sa.Column("topic_id", sa.Uuid(), nullable=False),
        sa.Column("keyword_id", sa.Uuid(), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["topic_id"], ["topics.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["keyword_id"], ["keywords.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("topic_id", "keyword_id", name="uq_topic_keywords_topic_keyword"),
    )


def downgrade():
    op.drop_table("topic_keywords")
    op.drop_index("ix_topics_organization_id", table_name="topics")
    op.drop_index("ix_topics_org_account", table_name="topics")
    op.drop_index("ix_topics_org_status", table_name="topics")
    op.drop_index("ix_topics_org_platform", table_name="topics")
    op.drop_table("topics")
