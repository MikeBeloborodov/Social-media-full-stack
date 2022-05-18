"""likes to posts

Revision ID: 35a0cee4edb4
Revises: af5d63be67df
Create Date: 2022-05-18 15:56:31.854060

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '35a0cee4edb4'
down_revision = 'af5d63be67df'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('posts', sa.Column('likes', sa.Integer(), nullable=False, server_default=sa.text('0')))
    pass

def downgrade():
    op.drop_column('posts', 'likes')
    pass