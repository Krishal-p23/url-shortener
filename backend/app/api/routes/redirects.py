"""Public short-code redirection endpoint."""

import re
import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from app.cache.redis import cache_url, get_cached_url
from app.db.session import get_db_session
from app.services.url_service import get_active_url_by_code, record_click


router = APIRouter(tags=["redirects"])
logger = logging.getLogger(__name__)
SHORT_CODE_PATTERN = re.compile(r"^[0-9A-Za-z]{1,16}$")


@router.get("/{short_code}", include_in_schema=False)
async def redirect_to_original_url(
    short_code: str,
    request: Request,
    session: AsyncSession = Depends(get_db_session),
) -> RedirectResponse:
    """Look up an active short code and redirect to its original URL."""

    if SHORT_CODE_PATTERN.fullmatch(short_code) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short URL not found",
        )

    cached_url = await get_cached_url(short_code)
    if cached_url is not None:
        await _record_click_safely(
            session, cached_url.url_id, request.headers.get("user-agent"),
            request.headers.get("referer"),
        )
        return RedirectResponse(
            url=cached_url.original_url,
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
        )

    url = await get_active_url_by_code(session, short_code)
    if url is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short URL not found",
        )
    await cache_url(short_code, url.id, url.original_url)
    await _record_click_safely(
        session, url.id, request.headers.get("user-agent"),
        request.headers.get("referer"),
    )
    return RedirectResponse(
        url=url.original_url,
        status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    )


async def _record_click_safely(
    session: AsyncSession,
    url_id: int,
    user_agent: str | None,
    referrer: str | None,
) -> None:
    """Record analytics without making redirect availability depend on it."""

    try:
        await record_click(session, url_id, user_agent, referrer)
    except SQLAlchemyError:
        await session.rollback()
        logger.warning("Unable to record click for URL id %s", url_id)