"""add_smth

Revision ID: 64281d04b0bc
Revises: 4e445294ae63
Create Date: 2024-12-21 21:01:21.677321

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '64281d04b0bc'
down_revision = '4e445294ae63'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('sessions', sa.Column('created_ts', sa.DateTime(), server_default=sa.text('now()'), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('sessions', 'created_ts')
    # ### end Alembic commands ###