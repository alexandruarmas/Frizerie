"""Add GDPR consent fields to users table

Revision ID: 7ac6c07e27a8
Revises: 74c3f048c41d
Create Date: 2025-05-28 01:08:49.602503

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7ac6c07e27a8'
down_revision: Union[str, None] = '74c3f048c41d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('terms_accepted', sa.Boolean(), nullable=True))
    op.add_column('users', sa.Column('terms_accepted_at', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'terms_accepted_at')
    op.drop_column('users', 'terms_accepted')
    # ### end Alembic commands ###
