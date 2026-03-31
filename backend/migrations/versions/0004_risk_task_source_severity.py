"""risk fields for stage 8 analyzer

Revision ID: 0004_risk_task_source_severity
Revises: 0003_user_competency_load
Create Date: 2026-03-31
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0004_risk_task_source_severity"
down_revision = "0003_user_competency_load"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("risks", sa.Column("severity", sa.String(length=20), nullable=False, server_default="low"))
    op.add_column("risks", sa.Column("source", sa.String(length=30), nullable=False, server_default="message"))
    op.add_column("risks", sa.Column("task_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key("fk_risks_task_id_tasks", "risks", "tasks", ["task_id"], ["id"], ondelete="SET NULL")
    op.create_index("ix_risks_severity", "risks", ["severity"])
    op.create_index("ix_risks_source", "risks", ["source"])
    op.create_index("ix_risks_task_id", "risks", ["task_id"])


def downgrade() -> None:
    op.drop_index("ix_risks_task_id", table_name="risks")
    op.drop_index("ix_risks_source", table_name="risks")
    op.drop_index("ix_risks_severity", table_name="risks")
    op.drop_constraint("fk_risks_task_id_tasks", "risks", type_="foreignkey")
    op.drop_column("risks", "task_id")
    op.drop_column("risks", "source")
    op.drop_column("risks", "severity")
