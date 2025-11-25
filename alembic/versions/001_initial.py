"""Initial migration

Revision ID: 001_initial
Revises: 
Create Date: 2025-01-27 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op  # type: ignore
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('is_admin', sa.Boolean(), default=False, nullable=False),
        sa.Column('admin_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['admin_id'], ['users.id'], ),
    )
    op.create_index('ix_users_email', 'users', ['email'])

    # Create forms table
    op.create_table(
        'forms',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('creator_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), default=True, nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['creator_id'], ['users.id'], ),
    )

    # Create form_fields table
    op.create_table(
        'form_fields',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('form_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('field_type', sa.String(50), nullable=False),
        sa.Column('label', sa.String(255), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('is_required', sa.Boolean(), default=False, nullable=False),
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('options', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['form_id'], ['forms.id'], ),
    )

    # Create form_submissions table
    op.create_table(
        'form_submissions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('form_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('submitted_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['form_id'], ['forms.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    )

    # Create form_field_values table
    op.create_table(
        'form_field_values',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('submission_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('field_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('value', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['submission_id'], ['form_submissions.id'], ),
        sa.ForeignKeyConstraint(['field_id'], ['form_fields.id'], ),
    )

    # Create files table
    op.create_table(
        'files',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('submission_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('field_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('original_filename', sa.String(255), nullable=False),
        sa.Column('blob_name', sa.String(500), nullable=False),
        sa.Column('blob_url', sa.String(1000), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('content_type', sa.String(100), nullable=True),
        sa.Column('uploaded_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['submission_id'], ['form_submissions.id'], ),
        sa.ForeignKeyConstraint(['field_id'], ['form_fields.id'], ),
    )


def downgrade() -> None:
    op.drop_table('files')
    op.drop_table('form_field_values')
    op.drop_table('form_submissions')
    op.drop_table('form_fields')
    op.drop_table('forms')
    op.drop_table('users')

