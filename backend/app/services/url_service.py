"""Business logic for creating persistent short URLs."""

from sqlalchemy import select, text, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.url import URL
from app.models.click_event import ClickEvent
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


async def get_active_url_by_code(
    session: AsyncSession,
    short_code: str,
) -> URL | None:
    """Return an active URL mapping for a short code, if one exists."""

    result = await session.execute(
        select(URL).where(
            URL.short_code == short_code,
            URL.is_active.is_(True),
        )
    )
    return result.scalar_one_or_none()


async def record_click(
    session: AsyncSession,
    url_id: int,
    user_agent: str | None,
    referrer: str | None,
) -> None:
    """Persist one click event and atomically increment the URL counter."""

    session.add(
        ClickEvent(
            url_id=url_id,
            user_agent=user_agent[:512] if user_agent else None,
            referrer=referrer,
        )
    )
    await session.execute(
        update(URL)
        .where(URL.id == url_id)
        .values(click_count=URL.click_count + 1)
    )
    await session.commit()


async def get_analytics(
    session: AsyncSession,
    short_code: str,
    recent_limit: int = 20,
) -> tuple[URL | None, list[ClickEvent]]:
    """Return a URL mapping and its most recent click events."""

    url_result = await session.execute(
        select(URL).where(URL.short_code == short_code)
    )
    url = url_result.scalar_one_or_none()
    if url is None:
        return None, []

    event_result = await session.execute(
        select(ClickEvent)
        .where(ClickEvent.url_id == url.id)
        .order_by(ClickEvent.clicked_at.desc())
        .limit(recent_limit)
    )
    return url, list(event_result.scalars().all())