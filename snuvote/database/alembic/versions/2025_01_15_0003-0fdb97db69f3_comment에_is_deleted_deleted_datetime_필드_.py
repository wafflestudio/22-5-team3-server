"""comment에 is_deleted, deleted_datetime 필드 추가

Revision ID: 0fdb97db69f3
Revises: 4fa11f1eada9
Create Date: 2025-01-15 00:03:28.237425

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0fdb97db69f3'
down_revision: Union[str, None] = '4fa11f1eada9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # comment 테이블에 is_deleted Column 추가 (기존 데이터에는 server_default='0'(False) 적용)
    op.add_column('comment', sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='0'))
    # server_default 제거
    op.alter_column('comment', 'is_deleted', server_default=None)

    # deleted_datetime Column 추가
    op.add_column('comment', sa.Column('deleted_datetime', sa.DateTime(timezone=True), nullable=True))



def downgrade() -> None:
    # deleted_datetime Column 삭제
    op.drop_column('comment', 'deleted_datetime')
    # is_deleted Column 삭제
    op.drop_column('comment', 'is_deleted')
