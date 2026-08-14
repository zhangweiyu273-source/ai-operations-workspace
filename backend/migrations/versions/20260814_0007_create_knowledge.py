from collections.abc import Sequence
import sqlalchemy as sa
from alembic import op

revision = "20260814_0007"
down_revision = "20260814_0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

def upgrade():
    op.create_table("knowledge", sa.Column("title", sa.String(255), nullable=False), sa.Column("category", sa.String(50), nullable=False), sa.Column("content", sa.Text(), nullable=False), sa.Column("summary", sa.Text()), sa.Column("source_type", sa.String(50)), sa.Column("source_name", sa.String(255)), sa.Column("priority", sa.String(10), server_default="中", nullable=False), sa.Column("status", sa.String(20), server_default="启用", nullable=False), sa.Column("id", sa.Uuid(), nullable=False), sa.Column("organization_id", sa.Uuid(), nullable=False), sa.Column("created_by", sa.Uuid()), sa.Column("updated_by", sa.Uuid()), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("is_deleted", sa.Boolean(), server_default="false", nullable=False), sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]), sa.PrimaryKeyConstraint("id"))
    op.create_index("ix_knowledge_org_category", "knowledge", ["organization_id", "category"]); op.create_index("ix_knowledge_org_status", "knowledge", ["organization_id", "status"]); op.create_index("ix_knowledge_org_updated", "knowledge", ["organization_id", "updated_at"])
    op.create_table("knowledge_tags", sa.Column("knowledge_id", sa.Uuid(), nullable=False), sa.Column("tag_name", sa.String(80), nullable=False), sa.Column("id", sa.Uuid(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False), sa.ForeignKeyConstraint(["knowledge_id"], ["knowledge.id"], ondelete="CASCADE"), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("knowledge_id", "tag_name", name="uq_knowledge_tags_knowledge_tag"))

def downgrade():
    op.drop_table("knowledge_tags"); op.drop_index("ix_knowledge_org_updated", table_name="knowledge"); op.drop_index("ix_knowledge_org_status", table_name="knowledge"); op.drop_index("ix_knowledge_org_category", table_name="knowledge"); op.drop_table("knowledge")
