"""create posts table

Revision ID: c421124d1e13
Revises: 
Create Date: 2022-05-18 03:27:14.850882

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c421124d1e13'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('posts',
                sa.Column('id', sa.Integer(), nullable=False, primary_key=True),
                sa.Column('title', sa.String(), nullable=False),
                sa.Column('content', sa.String(), nullable=False),
                sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('now()')),
                sa.Column('updated_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('now()')))
    pass


def downgrade():
    op.drop_table('posts')
    pass
