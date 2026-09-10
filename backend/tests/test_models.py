from sqlalchemy import inspect

from app.db.base import Base
from app.models import ClickEvent, URL


def test_url_table_has_expected_columns_and_constraints() -> None:
    table = URL.__table__

    assert set(table.columns.keys()) == {
        "id",
        "original_url",
        "short_code",
        "created_at",
        "updated_at",
        "click_count",
        "is_active",
    }
    assert table.primary_key.columns.keys() == {"id"}
    assert any(constraint.name is None for constraint in table.constraints)
    assert any(
        column.name == "short_code" and column.unique
        for column in table.columns
    )


def test_click_event_references_url_table() -> None:
    foreign_keys = list(ClickEvent.__table__.c.url_id.foreign_keys)

    assert len(foreign_keys) == 1
    assert foreign_keys[0].target_fullname == "urls.id"
    assert Base.metadata.tables.keys() == {"urls", "click_events"}