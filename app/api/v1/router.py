"""Central API router for version 1."""

from fastapi import APIRouter

from app.api.v1.health import router as health_router

api_router = APIRouter()

api_router.include_router(health_router)
