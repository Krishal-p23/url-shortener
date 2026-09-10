"""Create URL mappings and click analytics tables."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0001_create_url_tables"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "urls",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("original_url", sa.Text(), nullable=False),
        sa.Column("short_code", sa.String(length=16), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "click_count",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("short_code"),
    )
    op.create_index("ix_urls_short_code", "urls", ["short_code"], unique=True)

    op.create_table(
        "click_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("url_id", sa.Integer(), nullable=False),
        sa.Column(
            "clicked_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("user_agent", sa.String(length=512), nullable=True),
        sa.Column("referrer", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["url_id"], ["urls.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_click_events_url_id", "click_events", ["url_id"])
    op.create_index("ix_click_events_clicked_at", "click_events", ["clicked_at"])


def downgrade() -> None:
    op.drop_index("ix_click_events_clicked_at", table_name="click_events")
    op.drop_index("ix_click_events_url_id", table_name="click_events")
    op.drop_table("click_events")
    op.drop_index("ix_urls_short_code", table_name="urls")
    op.drop_table("urls")