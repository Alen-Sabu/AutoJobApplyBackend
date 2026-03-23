"""add automations table

Revision ID: 9b2c3d4e5f6
Revises: d4e5f6a7b8c9
Create Date: 2026-02-12
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "d4e5f6a7b8c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "automations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("target_titles", sa.Text(), nullable=True),
        sa.Column("locations", sa.Text(), nullable=True),
        sa.Column("daily_limit", sa.Integer(), nullable=False, server_default="25"),
        sa.Column("platforms", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("cover_letter_template", sa.Text(), nullable=True),
        sa.Column("status", sa.String(), nullable=False, server_default="paused"),
        sa.Column("total_applied", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_automations_id"), "automations", ["id"], unique=False)
    op.create_index(op.f("ix_automations_user_id"), "automations", ["user_id"], unique=False)
    op.create_index(op.f("ix_automations_status"), "automations", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_automations_status"), table_name="automations")
    op.drop_index(op.f("ix_automations_user_id"), table_name="automations")
    op.drop_index(op.f("ix_automations_id"), table_name="automations")
    op.drop_table("automations")

