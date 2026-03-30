"""user competency/load fields

Revision ID: 0003_user_competency_load
Revises: 0002_user_password_hash
Create Date: 2026-03-30
"""

from alembic import op
import sqlalchemy as sa

revision = "0003_user_competency_load"
down_revision = "0002_user_password_hash"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("competency", sa.Float(), nullable=False, server_default="0"),
    )
    op.add_column(
        "users",
        sa.Column("load", sa.Integer(), nullable=False, server_default="0"),
    )


def downgrade() -> None:
    op.drop_column("users", "load")
    op.drop_column("users", "competency")

