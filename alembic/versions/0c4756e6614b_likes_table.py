"""likes table

Revision ID: 0c4756e6614b
Revises: 04c17639c52a
Create Date: 2022-05-18 04:31:49.452522

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0c4756e6614b'
down_revision = '04c17639c52a'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('likes',
        sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
        sa.Column('post_id', sa.Integer(), sa.ForeignKey("posts.id", ondelete="CASCADE"), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False))
    pass


def downgrade():
    op.drop_table("likes")
    pass
