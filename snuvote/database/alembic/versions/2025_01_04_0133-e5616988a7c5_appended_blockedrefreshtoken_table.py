"""appended BlockedRefreshToken Table

Revision ID: e5616988a7c5
Revises: e72ea785319e
Create Date: 2025-01-04 01:33:18.284870

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e5616988a7c5'
down_revision: Union[str, None] = 'e72ea785319e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('blocked_refresh_token',
    sa.Column('token_id', sa.String(length=255), nullable=False),
    sa.Column('expires_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('token_id')
    )
    op.execute("""
        CREATE EVENT IF NOT EXISTS delete_expired_blocked_token
        ON SCHEDULE EVERY 1 DAY
            STARTS CURRENT_TIMESTAMP
        DO
            DELETE FROM blocked_refresh_token WHERE expires_at < NOW();
               """)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("DROP EVENT IF EXISTS delete_expired_blocked_token")
    op.drop_table('blocked_refresh_token')
    # ### end Alembic commands ###
