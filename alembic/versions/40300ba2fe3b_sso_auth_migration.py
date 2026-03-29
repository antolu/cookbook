"""sso_auth_migration

Revision ID: 40300ba2fe3b
Revises: b187b6d002ed
Create Date: 2026-03-29 20:58:52.944636

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '40300ba2fe3b'
down_revision = 'b187b6d002ed'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Drop unique constraint on username if it exists
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_constraint("users_username_key", type_="unique")
        batch_op.alter_column("username", nullable=True)
        batch_op.add_column(sa.Column("full_name", sa.String(length=255), nullable=True))
        batch_op.drop_column("hashed_password")
        batch_op.drop_column("is_active")
        batch_op.drop_column("is_superuser")
        batch_op.drop_column("is_verified")


def downgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(sa.Column("is_verified", sa.Boolean(), nullable=False, server_default="false"))
        batch_op.add_column(sa.Column("is_superuser", sa.Boolean(), nullable=False, server_default="false"))
        batch_op.add_column(sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"))
        batch_op.add_column(sa.Column("hashed_password", sa.String(length=1024), nullable=False, server_default=""))
        batch_op.drop_column("full_name")
        batch_op.alter_column("username", nullable=False)
        batch_op.create_unique_constraint("users_username_key", ["username"])