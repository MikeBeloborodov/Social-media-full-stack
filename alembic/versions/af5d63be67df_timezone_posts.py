"""timezone posts

Revision ID: af5d63be67df
Revises: 35abc812860f
Create Date: 2022-05-18 04:47:46.867886

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'af5d63be67df'
down_revision = '35abc812860f'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('posts', 'created_at')
    op.drop_column('posts', 'updated_at')
    op.add_column('posts',
            sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')))
    op.add_column('posts',
            sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')))
    pass


def downgrade():
    op.drop_column('posts', 'created_at')
    op.drop_column('posts', 'updated_at')
    op.add_column('posts',
            sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('now()')))
    op.add_column('posts',
            sa.Column('updated_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('now()')))
    pass
