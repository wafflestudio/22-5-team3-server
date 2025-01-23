"""User DB에서 password를 hashed_password로 교체

Revision ID: 49abd7e4c043
Revises: 9e2715d6e171
Create Date: 2025-01-23 23:11:56.190187

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '49abd7e4c043'
down_revision: Union[str, None] = '9e2715d6e171'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # password Column을 hashed_password로 교체
    op.alter_column(
        'user', # table name
        'password', # original column name
        new_column_name='hashed_password',
        type_=sa.String(60),
        existing_type=sa.String(20),
        existing_nullable=False
    )

    # 기존 회원들의 hashed_password를 특정값으로 교체
    # op.execute(
    # "UPDATE user SET hashed_password = 'hashed_password' ")


def downgrade() -> None:
    op.alter_column(
        'user',
        'hashed_password',
        new_column_name = 'password',
        type = sa.String(20),
        existing_type = sa.String(60),
        existing_nullable = False
    )
