"""DB에 NaverUser Table 추가 후 보완

Revision ID: e837333e71e1
Revises: 49abd7e4c043
Create Date: 2025-01-24 09:25:35.188730

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e837333e71e1'
down_revision: Union[str, None] = '49abd7e4c043'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('naver_user',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('naver_id', sa.String(length=50), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_naver_user_naver_id'), 'naver_user', ['naver_id'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_naver_user_naver_id'), table_name='naver_user')
    op.drop_table('naver_user')
    # ### end Alembic commands ###
