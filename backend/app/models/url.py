"""URL mapping database model."""

from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class URL(Base):
    """A persistent mapping from a compact code to an original URL."""

    __tablename__ = "urls"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    original_url: Mapped[str] = mapped_column(Text, nullable=False)
    short_code: Mapped[str] = mapped_column(
        String(16), nullable=False, unique=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    click_count: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="0"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="true"
    )

    click_events: Mapped[list["ClickEvent"]] = relationship(
        back_populates="url",
        cascade="all, delete-orphan",
    )