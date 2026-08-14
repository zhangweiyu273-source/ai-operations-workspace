from collections.abc import Sequence
import sqlalchemy as sa
from alembic import op

revision = "20260814_0010"
down_revision = "20260814_0009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

def upgrade() -> None:
    op.create_table("ai_analyses", sa.Column("analysis_type", sa.String(50), nullable=False), sa.Column("title", sa.String(255), nullable=False), sa.Column("date_start", sa.Date()), sa.Column("date_end", sa.Date()), sa.Column("summary", sa.Text(), nullable=False), sa.Column("result_json", sa.JSON(), nullable=False), sa.Column("provider", sa.String(40), nullable=False), sa.Column("model", sa.String(100), nullable=False), sa.Column("prompt_version", sa.String(30), nullable=False), sa.Column("context_version", sa.String(30), nullable=False), sa.Column("status", sa.String(20), nullable=False), sa.Column("id", sa.Uuid(), nullable=False), sa.Column("organization_id", sa.Uuid(), nullable=False), sa.Column("created_by", sa.Uuid()), sa.Column("updated_by", sa.Uuid()), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("is_deleted", sa.Boolean(), server_default="false", nullable=False), sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]), sa.PrimaryKeyConstraint("id"))
    op.create_index("ix_ai_analyses_org_created", "ai_analyses", ["organization_id", "created_at"])
    op.create_index("ix_ai_analyses_org_type", "ai_analyses", ["organization_id", "analysis_type"])

def downgrade() -> None:
    op.drop_table("ai_analyses")
