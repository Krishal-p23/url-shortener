"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.config import get_settings


def configure_logging(log_level: str) -> None:
    """Configure application-wide logging once during startup."""

    logging.basicConfig(
        level=log_level.upper(),
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize application services when the process starts."""

    settings = get_settings()
    configure_logging(settings.log_level)
    logging.getLogger(__name__).info(
        "Starting %s in %s mode",
        settings.app_name,
        settings.environment,
    )
    yield
    logging.getLogger(__name__).info("Application shutdown complete")


settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version="0.2.0",
    description="Stage 2 foundation for a distributed URL shortener.",
    lifespan=lifespan,
)


@app.get("/health", tags=["system"])
async def health_check() -> dict[str, str]:
    """Return a lightweight process health response."""

    return {"status": "healthy", "environment": settings.environment}