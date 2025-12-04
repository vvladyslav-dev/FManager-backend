"""refactor_notification_channels

Revision ID: 429369f34cb3
Revises: 23ceae0ceb3b
Create Date: 2025-12-03 18:14:55.102545

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid


# revision identifiers, used by Alembic.
revision: str = '429369f34cb3'
down_revision: Union[str, None] = '23ceae0ceb3b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create ENUM type with both lowercase and uppercase values for compatibility
    notification_channel_type = postgresql.ENUM('telegram', 'TELEGRAM', name='notificationchanneltype')
    # Create ENUM type only if not exists
    try:
        notification_channel_type.create(op.get_bind(), checkfirst=True)
    except Exception:
        # In some cases Alembic may attempt to create during table creation; ignore duplicates
        pass
    
    # Create notification_channels table
    # Use existing ENUM type without recreating during table create
    enum_ref = postgresql.ENUM('telegram', 'TELEGRAM', name='notificationchanneltype', create_type=False)
    op.create_table(
        'notification_channels',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('channel_type', enum_ref, nullable=False),
        sa.Column('is_enabled', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('config', postgresql.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.UniqueConstraint('user_id', 'channel_type', name='uq_user_channel_type')
    )
    
    # Create indexes
    op.create_index('ix_notification_channels_user_id', 'notification_channels', ['user_id'])
    op.create_index('ix_notification_channels_channel_type', 'notification_channels', ['channel_type'])
    op.create_index('ix_notification_channels_is_enabled', 'notification_channels', ['is_enabled'])
    
    # Migrate existing data from users table
    connection = op.get_bind()
    connection.execute(sa.text("""
        INSERT INTO notification_channels (id, user_id, channel_type, is_enabled, config, created_at, updated_at)
        SELECT 
            gen_random_uuid(),
            id,
            'TELEGRAM'::notificationchanneltype,
            telegram_notifications_enabled,
            jsonb_build_object('chat_id', telegram_chat_id),
            NOW(),
            NOW()
        FROM users
        WHERE telegram_chat_id IS NOT NULL AND telegram_chat_id != ''
    """))
    
    # Drop old columns from users table
    op.drop_column('users', 'telegram_chat_id')
    op.drop_column('users', 'telegram_notifications_enabled')
    op.drop_column('users', 'email_notifications_enabled')
    op.drop_column('users', 'notification_preferences')


def downgrade() -> None:
    # Add old columns back to users table
    op.add_column('users', sa.Column('telegram_chat_id', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('telegram_notifications_enabled', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('email_notifications_enabled', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('notification_preferences', postgresql.JSON(), nullable=True))
    
    # Migrate data back from notification_channels to users
    connection = op.get_bind()
    connection.execute(sa.text("""
        UPDATE users u
        SET 
            telegram_chat_id = nc.config->>'chat_id',
            telegram_notifications_enabled = nc.is_enabled
        FROM notification_channels nc
        WHERE u.id = nc.user_id AND nc.channel_type = 'telegram'::notificationchanneltype
    """))
    
    # Drop indexes
    op.drop_index('ix_notification_channels_is_enabled', 'notification_channels')
    op.drop_index('ix_notification_channels_channel_type', 'notification_channels')
    op.drop_index('ix_notification_channels_user_id', 'notification_channels')
    
    # Drop table
    op.drop_table('notification_channels')
    
    # Drop ENUM type
    notification_channel_type = postgresql.ENUM('telegram', 'TELEGRAM', name='notificationchanneltype')
    # Drop ENUM type if exists
    try:
        notification_channel_type.drop(op.get_bind(), checkfirst=True)
    except Exception:
        pass
