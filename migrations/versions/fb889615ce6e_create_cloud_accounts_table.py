"""create cloud_accounts table

Revision ID: fb889615ce6e
Revises:
Create Date: 2026-10-25 15:22:48.990738

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fb889615ce6e'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "cloud_accounts",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("account_id", sa.String(64), nullable=False),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("provider", sa.String(20), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime, nullable=False),
        sa.UniqueConstraint("account_id", "provider")
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("cloud_accounts")
