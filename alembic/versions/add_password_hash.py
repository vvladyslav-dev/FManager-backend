"""Add password_hash column to users table."""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_password_hash'
down_revision = '665fb26d9d88'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('password_hash', sa.String(255), nullable=True))


def downgrade():
    op.drop_column('users', 'password_hash')

