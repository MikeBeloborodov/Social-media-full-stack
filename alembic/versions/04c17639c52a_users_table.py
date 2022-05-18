"""users table

Revision ID: 04c17639c52a
Revises: c421124d1e13
Create Date: 2022-05-18 04:25:14.777950

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '04c17639c52a'
down_revision = 'c421124d1e13'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('users',
                    sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
                    sa.Column('email', sa.String(), nullable=False, unique=True),
                    sa.Column('password', sa.String(), nullable=False),
                    sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('now()')))
    pass


def downgrade():
    op.drop_table('users')
    pass
