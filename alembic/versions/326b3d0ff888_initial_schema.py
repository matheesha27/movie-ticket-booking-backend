"""initial schema

Revision ID: 326b3d0ff888
Revises: 
Create Date: 2026-06-04 08:25:10.244776

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '326b3d0ff888'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # STEP 1: Create the 'users' table with all structural columns
    op.create_table(
        'users',
        sa.Column('id', sa.BIGINT(), autoincrement=True, nullable=False),
        sa.Column('first_name', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('last_name', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('email', sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column('password_hash', sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('users_pkey')),
        sa.UniqueConstraint('email', name=op.f('users_email_key'))
    )

    # STEP 2: Create the table index now that the relation actually exists
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)


def downgrade() -> None:
    # Drop the index first, then drop the table cleanly
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')