from types import SimpleNamespace

import pytest
from sqlalchemy.exc import IntegrityError

from app.services.url_service import create_url


class FakeResult:
    def __init__(self, value: int) -> None:
        self.value = value

    def scalar_one(self) -> int:
        return self.value


class FakeSession:
    def __init__(self, sequence_values: list[int], fail_first_commit: bool = False):
        self.sequence_values = iter(sequence_values)
        self.fail_first_commit = fail_first_commit
        self.committed_urls = []
        self.rollback_count = 0

    async def execute(self, statement: object) -> FakeResult:
        return FakeResult(next(self.sequence_values))

    def add(self, url: object) -> None:
        self.committed_urls.append(url)

    async def commit(self) -> None:
        if self.fail_first_commit:
            self.fail_first_commit = False
            raise IntegrityError("insert", {}, Exception("duplicate"))

    async def rollback(self) -> None:
        self.rollback_count += 1

    async def refresh(self, url: object) -> None:
        url.created_at = SimpleNamespace(isoformat=lambda: "created")


@pytest.mark.asyncio
async def test_create_url_encodes_allocated_sequence_id() -> None:
    session = FakeSession([3843])

    url = await create_url(session, "https://example.com")

    assert url.id == 3843
    assert url.short_code == "zz"
    assert url.original_url == "https://example.com"


@pytest.mark.asyncio
async def test_create_url_retries_after_unique_constraint_failure() -> None:
    session = FakeSession([61, 62], fail_first_commit=True)

    url = await create_url(session, "https://example.com")

    assert url.id == 62
    assert url.short_code == "10"
    assert session.rollback_count == 1