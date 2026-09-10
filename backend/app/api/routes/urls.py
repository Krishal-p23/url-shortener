"""URL creation endpoints."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.db.session import get_db_session
from app.schemas.url import URLCreate, URLCreateResponse
from app.services.url_service import create_url


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