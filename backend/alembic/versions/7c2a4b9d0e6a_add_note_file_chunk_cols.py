"""add file_id and chunk_id to notes

Revision ID: 7c2a4b9d0e6a
Revises: f7a5b8c9d1b2
Create Date: 2026-08-07 02:40:00.000000
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '7c2a4b9d0e6a'
down_revision = 'f7a5b8c9d1b2'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('notes', sa.Column('file_id', sa.Integer(), sa.ForeignKey('uploaded_files.id', ondelete='SET NULL'), nullable=True))
    op.create_index(op.f('ix_notes_file_id'), 'notes', ['file_id'], unique=False)
    op.add_column('notes', sa.Column('chunk_id', sa.Integer(), sa.ForeignKey('document_chunks.id', ondelete='SET NULL'), nullable=True))
    op.create_index(op.f('ix_notes_chunk_id'), 'notes', ['chunk_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_notes_chunk_id'), table_name='notes')
    op.drop_column('notes', 'chunk_id')
    op.drop_index(op.f('ix_notes_file_id'), table_name='notes')
    op.drop_column('notes', 'file_id')
