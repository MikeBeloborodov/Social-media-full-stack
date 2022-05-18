"""owner id

Revision ID: 9a64fdf0162c
Revises: 0c4756e6614b
Create Date: 2022-05-18 04:36:39.949969

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9a64fdf0162c'
down_revision = '0c4756e6614b'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('posts',
            sa.Column('owner_id', sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False))
    pass


def downgrade():
    op.drop_column('posts', 'owner_id')
    pass
