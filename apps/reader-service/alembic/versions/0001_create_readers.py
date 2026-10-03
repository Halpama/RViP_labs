"""create readers"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001_create_readers"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "readers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("card_number", sa.String(length=100), nullable=False),
        sa.Column("card_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("book_title", sa.String(length=500), nullable=True),
        sa.Column("registered_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("card_number", name="uq_readers_card_number"),
    )


def downgrade() -> None:
    op.drop_table("readers")
