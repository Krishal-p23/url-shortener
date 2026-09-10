"""Public short-code redirection endpoint."""

import re

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache.redis import cache_url, get_cached_url
from app.db.session import get_db_session
from app.services.url_service import get_active_url_by_code


router = APIRouter(tags=["redirects"])
SHORT_CODE_PATTERN = re.compile(r"^[0-9A-Za-z]{1,16}$")


@router.get("/{short_code}", include_in_schema=False)
async def redirect_to_original_url(
    short_code: str,
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
        return RedirectResponse(
            url=cached_url,
            status_code=status.HTTP_307_TEMPORARY_REDIRECT,
        )

    url = await get_active_url_by_code(session, short_code)
    if url is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short URL not found",
        )
    await cache_url(short_code, url.original_url)
    return RedirectResponse(
        url=url.original_url,
        status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    )