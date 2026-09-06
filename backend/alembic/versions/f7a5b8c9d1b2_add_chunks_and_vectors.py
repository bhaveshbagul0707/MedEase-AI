"""add document_chunks and vector_entries tables

Revision ID: f7a5b8c9d1b2
Revises: d9f8a6b7c432
Create Date: 2026-08-07 02:32:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'f7a5b8c9d1b2'
down_revision = 'd9f8a6b7c432'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'document_chunks',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('file_id', sa.Integer(), sa.ForeignKey('uploaded_files.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('user_id', sa.Integer(), nullable=False, index=True),
        sa.Column('page_number', sa.Integer(), nullable=True),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_table(
        'vector_entries',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('chunk_id', sa.Integer(), sa.ForeignKey('document_chunks.id', ondelete='CASCADE'), nullable=False, index=True),
        sa.Column('embedding', sa.Text(), nullable=False),
        sa.Column('metadata', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )


def downgrade():
    op.drop_table('vector_entries')
    op.drop_table('document_chunks')
