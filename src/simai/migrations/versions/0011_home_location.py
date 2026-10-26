"""home location per character

Revision ID: 0011
Revises: 0010
Create Date: 2026-10-26

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0011"
down_revision: str | None = "0010"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Niente FK a livello DB: SQLite non supporta ADD CONSTRAINT via
    # ALTER TABLE, e Alembic non emette REFERENCES inline per
    # op.add_column. L'app gestisce già il caso "home_location
    # orfana" (session.get(Location, ...) -> None -> no priorità
    # casa). La FK non aggiunge valore runtime in 1.2.1.
    op.add_column(
        "characters",
        sa.Column(
            "home_location_id",
            sa.Integer,
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("characters", "home_location_id")
