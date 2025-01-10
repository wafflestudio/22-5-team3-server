"""Vote의 create, end_datetime를 Timestamp로 변경

Revision ID: 0a5a02cfb40b
Revises: ac9dd8c234ab
Create Date: 2025-01-10 18:32:23.324963

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0a5a02cfb40b'
down_revision: Union[str, None] = 'ac9dd8c234ab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(f"""
        UPDATE vote
        SET create_datetime = CONVERT_TZ(create_datetime, 'Asia/Seoul', 'UTC');
    """)
    # DATETIME을 TIMESTAMP로 변경
    op.alter_column(
        'vote',
        'create_datetime',
        type_=sa.TIMESTAMP(timezone=False),  # TIMESTAMP로 변경
        existing_type=sa.DATETIME(),
        existing_nullable=False  # 기존 NULL 허용 여부를 유지  # 기존 기본값 유지
    )
    op.execute(f"""
        UPDATE vote
        SET create_datetime = CONVERT_TZ(create_datetime, 'Asia/Seoul', 'UTC');
    """)
    # DATETIME을 TIMESTAMP로 변경
    op.alter_column(
        'vote',
        'end_datetime',
        type_=sa.TIMESTAMP(timezone=False),  # TIMESTAMP로 변경
        existing_type=sa.DATETIME(),
        existing_nullable=False  # 기존 NULL 허용 여부를 유지  # 기존 기본값 유지
    )
    op.execute(f"""
        UPDATE vote
        SET end_datetime = CONVERT_TZ(end_datetime, 'Asia/Seoul', 'UTC');
    """)



def downgrade() -> None:
    op.alter_column(
        'vote',
        'end_datetime',
        type_=sa.DATETIME(),
        existing_type=sa.TIMESTAMP(timezone=False),
        existing_nullable=True
    )
    op.execute(f"""
        UPDATE vote
        SET end_datetime = CONVERT_TZ(end_datetime, 'UTC', 'Asia/Seoul');
    """)
    op.alter_column(
        'vote',
        'create_datetime',
        type_=sa.DATETIME(),
        existing_type=sa.TIMESTAMP(timezone=False),
        existing_nullable=True
    )
    op.execute(f"""
        UPDATE vote
        SET create_datetime = CONVERT_TZ(create_datetime, 'UTC', 'Asia/Seoul');
    """)
    pass
