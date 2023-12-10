"""add missing phone to user

Revision ID: 6d7fb11ada22
Revises: fe1cf831d6c4
Create Date: 2023-12-11 00:34:19.402012

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "6d7fb11ada22"
down_revision: Union[str, None] = "fe1cf831d6c4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("user", sa.Column("phone", sa.String(length=20), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("user", "phone")
    # ### end Alembic commands ###