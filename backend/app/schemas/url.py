"""Schemas for URL creation and retrieval."""

from datetime import datetime

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field


class URLCreate(BaseModel):
    """Payload accepted when creating a shortened URL."""

    url: AnyHttpUrl = Field(description="The HTTP or HTTPS URL to shorten")


class URLCreateResponse(BaseModel):
    """Public representation returned after creating a shortened URL."""

    model_config = ConfigDict(from_attributes=True)

    short_code: str
    short_url: str
    original_url: AnyHttpUrl
    created_at: datetime


class ClickEventResponse(BaseModel):
    """Public representation of one recent click event."""

    model_config = ConfigDict(from_attributes=True)

    clicked_at: datetime
    user_agent: str | None
    referrer: str | None


class URLAnalyticsResponse(BaseModel):
    """Aggregate and recent click information for a short URL."""

    short_code: str
    total_clicks: int
    recent_clicks: list[ClickEventResponse]