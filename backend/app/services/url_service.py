"""Business logic for creating persistent short URLs."""

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.url import URL
from app.utils.base62 import encode_base62


async def create_url(
    session: AsyncSession,
    original_url: str,
    max_attempts: int = 3,
) -> URL:
    """Create a URL using the PostgreSQL primary-key sequence as its code source.

    The sequence allocates an ID atomically, so concurrent requests never need
    to coordinate in application memory. The resulting ID is encoded as Base62.
    """

    for _ in range(max_attempts):
        sequence_result = await session.execute(
            text("SELECT nextval(pg_get_serial_sequence('urls', 'id'))")
        )
        url_id = sequence_result.scalar_one()
        url = URL(
            id=url_id,
            original_url=original_url,
            short_code=encode_base62(url_id),
        )
        session.add(url)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            continue
        await session.refresh(url)
        return url

    raise RuntimeError("Unable to allocate a unique short code")