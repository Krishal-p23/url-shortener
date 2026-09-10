"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

from app.api.router import api_router
from app.api.routes.redirects import router as redirects_router
from app.cache.redis import close_redis
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
    await close_redis()
    logging.getLogger(__name__).info("Application shutdown complete")


settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version="0.2.0",
    description="Stage 3 URL creation API with PostgreSQL-backed Base62 codes.",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip()
        for origin in settings.allowed_origins.split(",")
        if origin.strip()
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type"],
)
app.include_router(api_router)


@app.exception_handler(SQLAlchemyError)
async def database_error_handler(
    request: Request,
    exc: SQLAlchemyError,
) -> JSONResponse:
    """Return a stable public error without exposing database details."""

    logging.getLogger(__name__).exception("Database request failure", exc_info=exc)
    return JSONResponse(
        status_code=503,
        content={"detail": "Database service unavailable"},
    )


@app.get("/health", tags=["system"])
async def health_check() -> dict[str, str]:
    """Return a lightweight process health response."""

    return {"status": "healthy", "environment": settings.environment}


app.include_router(redirects_router)