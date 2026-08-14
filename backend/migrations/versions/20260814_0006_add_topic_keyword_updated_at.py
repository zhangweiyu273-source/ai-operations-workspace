from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision = "20260814_0006"
down_revision = "20260814_0005"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade():
    op.add_column(
        "topic_keywords",
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )


def downgrade():
    op.drop_column("topic_keywords", "updated_at")
