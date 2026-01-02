"""Make timestamps timezone aware

Revision ID: 6acc7b4fc303
Revises: cd8764615377
Create Date: 2026-01-02 15:41:47.943964

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "6acc7b4fc303"
down_revision: Union[str, Sequence[str], None] = "cd8764615377"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Convert created_at and updated_at columns to TIMESTAMP WITH TIME ZONE
    op.execute("""
        ALTER TABLE users
        ALTER COLUMN created_at TYPE TIMESTAMP WITH TIME ZONE
        USING created_at AT TIME ZONE 'UTC'
    """)

    op.execute("""
        ALTER TABLE users
        ALTER COLUMN updated_at TYPE TIMESTAMP WITH TIME ZONE
        USING updated_at AT TIME ZONE 'UTC'
    """)


def downgrade() -> None:
    """Downgrade schema."""
    # Convert back to TIMESTAMP WITHOUT TIME ZONE
    op.execute("""
        ALTER TABLE users
        ALTER COLUMN created_at TYPE TIMESTAMP WITHOUT TIME ZONE
    """)

    op.execute("""
        ALTER TABLE users
        ALTER COLUMN updated_at TYPE TIMESTAMP WITHOUT TIME ZONE
    """)
