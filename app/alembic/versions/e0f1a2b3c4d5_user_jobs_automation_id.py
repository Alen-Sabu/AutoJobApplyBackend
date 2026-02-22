"""user_jobs automation_id

Revision ID: e0f1a2b3c4d5
Revises: 9b2c3d4e5f6
Create Date: 2026-02-12

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e0f1a2b3c4d5"
down_revision: Union[str, Sequence[str], None] = "9b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "user_jobs",
        sa.Column("automation_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_user_jobs_automation_id",
        "user_jobs",
        "automations",
        ["automation_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(op.f("ix_user_jobs_automation_id"), "user_jobs", ["automation_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_user_jobs_automation_id"), table_name="user_jobs")
    op.drop_constraint("fk_user_jobs_automation_id", "user_jobs", type_="foreignkey")
    op.drop_column("user_jobs", "automation_id")
