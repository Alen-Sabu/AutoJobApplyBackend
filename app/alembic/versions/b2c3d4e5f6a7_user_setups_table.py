"""user_setups table for onboarding

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-02-12

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_setups",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("full_name", sa.String(), nullable=True),
        sa.Column("email", sa.String(), nullable=True),
        sa.Column("phone", sa.String(), nullable=True),
        sa.Column("location", sa.String(), nullable=True),
        sa.Column("linkedin_url", sa.String(), nullable=True),
        sa.Column("years_experience", sa.String(), nullable=True),
        sa.Column("top_skills", sa.Text(), nullable=True),
        sa.Column("resume_file_name", sa.String(), nullable=True),
        sa.Column("resume_file_path", sa.String(), nullable=True),
        sa.Column("setup_complete", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index(op.f("ix_user_setups_id"), "user_setups", ["id"], unique=False)
    op.create_index(op.f("ix_user_setups_user_id"), "user_setups", ["user_id"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_user_setups_user_id"), table_name="user_setups")
    op.drop_index(op.f("ix_user_setups_id"), table_name="user_setups")
    op.drop_table("user_setups")
