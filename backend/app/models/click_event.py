"""Click analytics event database model."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ClickEvent(Base):
    """A lightweight event recorded when a short URL is visited."""

    __tablename__ = "click_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    url_id: Mapped[int] = mapped_column(
        ForeignKey("urls.id", ondelete="CASCADE"), nullable=False, index=True
    )
    clicked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), index=True
    )
    user_agent: Mapped[str | None] = mapped_column(String(512), nullable=True)
    referrer: Mapped[str | None] = mapped_column(Text, nullable=True)

    url: Mapped["URL"] = relationship(back_populates="click_events")