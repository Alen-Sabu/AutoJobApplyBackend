"""site_settings table

Revision ID: f1a2b3c4d5e6
Revises: e0f1a2b3c4d5
Create Date: 2026-02-12

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f1a2b3c4d5e6"
down_revision: Union[str, Sequence[str], None] = "e0f1a2b3c4d5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "site_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("maintenance_mode", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("new_user_registration", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("require_email_verification", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("max_automations_per_user", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("site_name", sa.String(), nullable=False, server_default="'CrypGo'"),
        sa.Column("support_email", sa.String(), nullable=False, server_default="'support@crypgo.com'"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.execute(
        "INSERT INTO site_settings (id, maintenance_mode, new_user_registration, require_email_verification, max_automations_per_user, site_name, support_email) "
        "VALUES (1, false, true, false, 10, 'CrypGo', 'support@crypgo.com')"
    )


def downgrade() -> None:
    op.drop_table("site_settings")
