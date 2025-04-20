"""Create User and Podcast tables with UUIDs

Revision ID: f0b7204e2572
Revises: 
Create Date: 2025-04-17 16:12:56.157613

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'f0b7204e2572'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:

    # Create users table with UUID
    op.create_table('users',
        sa.Column('userid', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('password', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('profile_picture', sa.LargeBinary(), nullable=True)
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_userid'), 'users', ['userid'], unique=False)

    # Create podcasts table with UUID id and foreign key
    op.create_table('podcasts',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('userid', sa.String(length=36), nullable=False),
        sa.Column('thumbnail_url', sa.String(length=255), nullable=True),
        sa.Column('summarized_content', sa.String(), nullable=True),
        sa.Column('target_language', sa.String(length=50), nullable=True),
        sa.Column('audio_path', sa.String(length=255), nullable=False),
        sa.Column('duration', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['userid'], ['users.userid'], ondelete='CASCADE')
    )
    op.create_index(op.f('ix_podcasts_id'), 'podcasts', ['id'], unique=False)

    op.create_table(
        'heading_section',
        sa.Column('id', sa.String(length=36), primary_key=True, nullable=False),
        sa.Column('header', sa.String(length=255), nullable=False),
        sa.Column('title', sa.Text(), nullable=False),    
        sa.Column('content', sa.Text(), nullable=False),  
        sa.Column('start', sa.Float(), nullable=False),
        sa.Column('end', sa.Float(), nullable=False),
        sa.Column('podcast_id', sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint( ['podcast_id'], ['podcasts.id'], ondelete='CASCADE')
    )

def downgrade() -> None:
    # Drop new tables
    op.drop_index(op.f('ix_podcasts_id'), table_name='podcasts')
    op.drop_table('podcasts')
    op.drop_index(op.f('ix_users_userid'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_table('heading_section')