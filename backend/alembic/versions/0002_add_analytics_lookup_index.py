"""Add a composite index for recent per-URL analytics."""

from typing import Sequence, Union

from alembic import op


revision: str = "0002_add_analytics_lookup_index"
down_revision: Union[str, None] = "0001_create_url_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "ix_click_events_url_id_clicked_at",
        "click_events",
        ["url_id", "clicked_at"],
        postgresql_ops={"clicked_at": "DESC"},
    )


def downgrade() -> None:
    op.drop_index(
        "ix_click_events_url_id_clicked_at",
        table_name="click_events",
    )