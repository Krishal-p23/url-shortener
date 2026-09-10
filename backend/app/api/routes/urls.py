"""URL creation endpoints."""

import re

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.cache.redis import delete_cached_url
from app.db.session import get_db_session
from app.schemas.url import URLCreate, URLCreateResponse, URLResponse
from app.services.url_service import (
    create_url,
    deactivate_url,
    get_active_url_by_code,
)


router = APIRouter(prefix="/urls", tags=["urls"])


@router.post(
    "",
    response_model=URLCreateResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_short_url(
    payload: URLCreate,
    session: AsyncSession = Depends(get_db_session),
) -> URLCreateResponse:
    """Persist a URL and return its compact public link."""

    settings = get_settings()
    url = await create_url(session, str(payload.url))
    short_url = f"{settings.public_base_url.rstrip('/')}/{url.short_code}"
    return URLCreateResponse(
        short_code=url.short_code,
        short_url=short_url,
        original_url=url.original_url,
        created_at=url.created_at,
    )


def validate_short_code(short_code: str) -> None:
    """Reject malformed API short codes as missing resources."""

    if re.fullmatch(r"[0-9A-Za-z]{1,16}", short_code) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short URL not found",
        )


@router.get("/{short_code}", response_model=URLResponse)
async def read_short_url(
    short_code: str,
    session: AsyncSession = Depends(get_db_session),
) -> URLResponse:
    """Return details for an active shortened URL."""

    validate_short_code(short_code)
    url = await get_active_url_by_code(session, short_code)
    if url is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short URL not found",
        )
    settings = get_settings()
    return URLResponse(
        short_code=url.short_code,
        short_url=f"{settings.public_base_url.rstrip('/')}/{url.short_code}",
        original_url=url.original_url,
        created_at=url.created_at,
        updated_at=url.updated_at,
        click_count=url.click_count,
        is_active=url.is_active,
    )


@router.delete("/{short_code}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_short_url(
    short_code: str,
    session: AsyncSession = Depends(get_db_session),
) -> None:
    """Soft-delete a URL and invalidate its cached destination."""

    validate_short_code(short_code)
    url = await deactivate_url(session, short_code)
    if url is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short URL not found",
        )
    await delete_cached_url(short_code)