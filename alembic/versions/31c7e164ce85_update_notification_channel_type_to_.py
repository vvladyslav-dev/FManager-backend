"""update_notification_channel_type_to_uppercase

Revision ID: 31c7e164ce85
Revises: 429369f34cb3
Create Date: 2025-12-04 10:49:16.000394

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '31c7e164ce85'
down_revision: Union[str, None] = '429369f34cb3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add uppercase 'TELEGRAM' value to enum if not exists
    op.execute("""
        DO $$ 
        BEGIN
            ALTER TYPE notificationchanneltype ADD VALUE IF NOT EXISTS 'TELEGRAM';
        EXCEPTION 
            WHEN duplicate_object THEN NULL;
        END $$;
    """)
    
    # Update existing lowercase 'telegram' records to uppercase 'TELEGRAM'
    op.execute("""
        UPDATE notification_channels 
        SET channel_type = 'TELEGRAM'::notificationchanneltype 
        WHERE channel_type = 'telegram'::notificationchanneltype;
    """)


def downgrade() -> None:
    # Downgrade uppercase back to lowercase
    op.execute("""
        UPDATE notification_channels 
        SET channel_type = 'telegram'::notificationchanneltype 
        WHERE channel_type = 'TELEGRAM'::notificationchanneltype;
    """)
