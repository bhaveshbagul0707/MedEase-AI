"""Add uploaded_files lifecycle and storage fields

Revision ID: d9f8a6b7c432
Revises: c1a2b3d4e5f6
Create Date: 2026-08-07 01:52:06

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "d9f8a6b7c432"
down_revision: Union[str, None] = "c1a2b3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add columns to uploaded_files
    op.add_column(
        "uploaded_files",
        sa.Column("status", sa.String(length=50), nullable=False, server_default=sa.text("'PENDING'")),
    )
    op.add_column(
        "uploaded_files",
        sa.Column("storage_path", sa.String(length=1000), nullable=True),
    )
    op.add_column(
        "uploaded_files",
        sa.Column("mime_type", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "uploaded_files",
        sa.Column("checksum_sha256", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "uploaded_files",
        sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "uploaded_files",
        sa.Column("processed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "uploaded_files",
        sa.Column("processing_error", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("uploaded_files", "processing_error")
    op.drop_column("uploaded_files", "processed_at")
    op.drop_column("uploaded_files", "uploaded_at")
    op.drop_column("uploaded_files", "checksum_sha256")
    op.drop_column("uploaded_files", "mime_type")
    op.drop_column("uploaded_files", "storage_path")
    op.drop_column("uploaded_files", "status")
