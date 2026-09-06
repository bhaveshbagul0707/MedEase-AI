"""Add refresh_tokens and auth_audit tables; add user columns for verification and lockout

Revision ID: c1a2b3d4e5f6
Revises: None
Create Date: 2026-08-07 01:41:09

This migration is additive and backward compatible.

It performs the following steps in upgrade():
- Add columns to the existing users table:
  - email_verification_token (VARCHAR(255), nullable)
  - email_verification_expires (TIMESTAMP with timezone, nullable)
  - failed_login_attempts (INTEGER, NOT NULL, default 0)
  - locked_until (TIMESTAMP with timezone, nullable)
  These columns support email verification, failed-login tracking and temporary lockouts.

- Create a new table refresh_tokens to persist only refresh token identifiers (jti) and metadata:
  - id (INTEGER, PK, autoincrement)
  - jti (VARCHAR(128), unique, indexed, NOT NULL)
  - user_id (INTEGER, FK -> users.id, NOT NULL)
  - created_at (TIMESTAMP with timezone, NOT NULL)
  - expires_at (TIMESTAMP with timezone, NOT NULL)
  - revoked (BOOLEAN, NOT NULL, default False)
  - last_used_at (TIMESTAMP with timezone, nullable)
  - ip_address (VARCHAR(45), nullable)
  - user_agent (VARCHAR(500), nullable)

- Create a new table auth_audit as an append-only audit log for authentication events:
  - id (INTEGER, PK, autoincrement)
  - user_id (INTEGER, FK -> users.id, nullable)
  - event_type (VARCHAR(50), NOT NULL)
  - ip_address (VARCHAR(45), nullable)
  - user_agent (VARCHAR(500), nullable)
  - metadata (TEXT, nullable)
  - created_at (TIMESTAMP with timezone, NOT NULL)

Downgrade reverses these steps in the safe reverse order: drop tables, then drop added columns.

Note: This file only creates migration scripts. It does not execute them. Do NOT apply these migrations without explicit approval.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "c1a2b3d4e5f6"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1) Add new columns to users table (additive, backward compatible)
    op.add_column("users", sa.Column("email_verification_token", sa.String(length=255), nullable=True))
    op.add_column("users", sa.Column("email_verification_expires", sa.DateTime(timezone=True), nullable=True))
    op.add_column("users", sa.Column("failed_login_attempts", sa.Integer(), nullable=False, server_default=sa.text("0")))
    op.add_column("users", sa.Column("locked_until", sa.DateTime(timezone=True), nullable=True))

    # 2) Create refresh_tokens table to store jti and metadata (no full JWTs persisted)
    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("jti", sa.String(length=128), nullable=False, unique=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("last_used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.String(length=500), nullable=True),
    )
    # create an index on created_at and jti for common query patterns
    op.create_index("ix_refresh_tokens_jti", "refresh_tokens", ["jti"], unique=True)
    op.create_index("ix_refresh_tokens_created_at", "refresh_tokens", ["created_at"])

    # 3) Create auth_audit table as append-only audit log
    op.create_table(
        "auth_audit",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("event_type", sa.String(length=50), nullable=False),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("user_agent", sa.String(length=500), nullable=True),
        sa.Column("metadata", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_auth_audit_created_at", "auth_audit", ["created_at"]) 


def downgrade() -> None:
    # Reverse operations: drop audit table, refresh_tokens table, then remove added columns
    op.drop_index("ix_auth_audit_created_at", table_name="auth_audit")
    op.drop_table("auth_audit")

    op.drop_index("ix_refresh_tokens_created_at", table_name="refresh_tokens")
    op.drop_index("ix_refresh_tokens_jti", table_name="refresh_tokens")
    op.drop_table("refresh_tokens")

    # Remove columns from users
    op.drop_column("users", "locked_until")
    op.drop_column("users", "failed_login_attempts")
    op.drop_column("users", "email_verification_expires")
    op.drop_column("users", "email_verification_token")
