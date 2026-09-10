"""Central API router."""

from fastapi import APIRouter

from app.api.routes.urls import router as urls_router
from app.config import get_settings


api_router = APIRouter(prefix=get_settings().api_prefix)
api_router.include_router(urls_router)