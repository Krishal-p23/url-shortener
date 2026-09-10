"""Click analytics endpoint."""

import re

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db_session
from app.schemas.url import ClickEventResponse, URLAnalyticsResponse
from app.services.url_service import get_analytics


router = APIRouter(prefix="/urls", tags=["analytics"])


@router.get("/{short_code}/analytics", response_model=URLAnalyticsResponse)
async def read_url_analytics(
    short_code: str,
    session: AsyncSession = Depends(get_db_session),
) -> URLAnalyticsResponse:
    """Return total clicks and recent click metadata for a short URL."""

    if re.fullmatch(r"[0-9A-Za-z]{1,16}", short_code) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short URL not found",
        )
    url, events = await get_analytics(session, short_code)
    if url is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short URL not found",
        )
    return URLAnalyticsResponse(
        short_code=url.short_code,
        total_clicks=url.click_count,
        recent_clicks=[
            ClickEventResponse.model_validate(event) for event in events
        ],
    )