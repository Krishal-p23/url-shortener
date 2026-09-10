import pytest

from app.services.url_service import record_click


class FakeSession:
    def __init__(self) -> None:
        self.added = []
        self.executed = []
        self.commit_count = 0

    def add(self, value: object) -> None:
        self.added.append(value)

    async def execute(self, statement: object) -> None:
        self.executed.append(statement)

    async def commit(self) -> None:
        self.commit_count += 1


@pytest.mark.asyncio
async def test_record_click_persists_event_and_commits() -> None:
    session = FakeSession()

    await record_click(
        session,
        url_id=7,
        user_agent="a" * 600,
        referrer="https://referrer.example",
    )

    event = session.added[0]
    assert event.url_id == 7
    assert len(event.user_agent) == 512
    assert event.referrer == "https://referrer.example"
    assert len(session.executed) == 1
    assert session.commit_count == 1