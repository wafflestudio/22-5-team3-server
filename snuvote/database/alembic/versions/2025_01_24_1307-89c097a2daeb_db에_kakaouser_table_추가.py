"""DB에 KakaoUser Table 추가

Revision ID: 89c097a2daeb
Revises: e837333e71e1
Create Date: 2025-01-24 13:07:16.994176

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '89c097a2daeb'
down_revision: Union[str, None] = 'e837333e71e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('kakao_user',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('kakao_id', sa.BigInteger(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_kakao_user_kakao_id'), 'kakao_user', ['kakao_id'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_kakao_user_kakao_id'), table_name='kakao_user')
    op.drop_table('kakao_user')
    # ### end Alembic commands ###
