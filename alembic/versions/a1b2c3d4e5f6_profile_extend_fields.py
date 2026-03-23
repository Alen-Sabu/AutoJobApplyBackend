"""profile extend fields for frontend

Revision ID: a1b2c3d4e5f6
Revises: 8a1b2c3d4e5f
Create Date: 2026-02-12

Add headline, primary_location, years_experience, compensation_currency,
top_skills, cover_letter_tone, matching_preferences to profiles.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "8a1b2c3d4e5f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("profiles", sa.Column("headline", sa.String(), nullable=True))
    op.add_column("profiles", sa.Column("primary_location", sa.String(), nullable=True))
    op.add_column("profiles", sa.Column("years_experience", sa.String(), nullable=True))
    op.add_column("profiles", sa.Column("compensation_currency", sa.String(), nullable=True))
    op.add_column("profiles", sa.Column("top_skills", sa.Text(), nullable=True))
    op.add_column("profiles", sa.Column("cover_letter_tone", sa.Text(), nullable=True))
    op.add_column("profiles", sa.Column("matching_preferences", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("profiles", "matching_preferences")
    op.drop_column("profiles", "cover_letter_tone")
    op.drop_column("profiles", "top_skills")
    op.drop_column("profiles", "compensation_currency")
    op.drop_column("profiles", "years_experience")
    op.drop_column("profiles", "primary_location")
    op.drop_column("profiles", "headline")
