"""Top-level API router.

For now, this includes the existing v1 router tree under `/api/v1`.
As the project transitions to `app.routers.*`, we can progressively move
endpoints here without breaking clients.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.router import api_router as v1_api_router

api_router = APIRouter()
api_router.include_router(v1_api_router, prefix="/api/v1")

