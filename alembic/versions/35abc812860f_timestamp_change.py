"""timestamp change

Revision ID: 35abc812860f
Revises: 9a64fdf0162c
Create Date: 2022-05-18 04:43:19.518913

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '35abc812860f'
down_revision = '9a64fdf0162c'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('users', 'created_at')
    op.add_column('users',
            sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')))
    pass


def downgrade():
    op.drop_column('users', 'created_at')
    op.add_column('users',
            sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('now()')))
    pass
