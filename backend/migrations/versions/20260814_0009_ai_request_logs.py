from collections.abc import Sequence
import sqlalchemy as sa
from alembic import op

revision = "20260814_0009"
down_revision = "20260814_0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

def upgrade() -> None:
    op.create_table("ai_request_logs", sa.Column("provider", sa.String(40), nullable=False), sa.Column("model", sa.String(100), nullable=False), sa.Column("feature", sa.String(80), nullable=False), sa.Column("status", sa.String(20), nullable=False), sa.Column("prompt_tokens", sa.Integer()), sa.Column("completion_tokens", sa.Integer()), sa.Column("total_tokens", sa.Integer()), sa.Column("latency_ms", sa.Integer()), sa.Column("error_type", sa.String(80)), sa.Column("id", sa.Uuid(), nullable=False), sa.Column("organization_id", sa.Uuid(), nullable=False), sa.Column("created_by", sa.Uuid()), sa.Column("updated_by", sa.Uuid()), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("is_deleted", sa.Boolean(), server_default="false", nullable=False), sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]), sa.PrimaryKeyConstraint("id"))
    op.create_index("ix_ai_request_logs_org_created", "ai_request_logs", ["organization_id", "created_at"])
    op.create_index("ix_ai_request_logs_org_status", "ai_request_logs", ["organization_id", "status"])

def downgrade() -> None:
    op.drop_table("ai_request_logs")
