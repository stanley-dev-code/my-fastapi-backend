"""add container size to containers

Revision ID: a23538af2484
Revises: 038c53f42db2
Create Date: 2026-08-01 14:12:04.042208

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a23538af2484'
down_revision: Union[str, Sequence[str], None] = '038c53f42db2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    container_size_enum = sa.Enum(
        'TWENTY_FT', 'FORTY_FT', 'FORTY_FT_HC', 'FORTY_FIVE_FT_HC',
        name='containersize'
    )
    container_size_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        'containers',
        sa.Column('container_size', container_size_enum, nullable=False, server_default='TWENTY_FT')
    )


def downgrade() -> None:
    op.drop_column('containers', 'container_size')
    sa.Enum(name='containersize').drop(op.get_bind(), checkfirst=True)