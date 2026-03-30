"""FastAPI application entrypoint."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette import status

from app.routers.router import api_router
from app.routers.ai import router as ai_router
from app.routers.documents import router as documents_router
from app.routers.openclaw import router as openclaw_router
from app.routers.proactive import router as proactive_router
from app.routers.projects import router as projects_router
from app.routers.recommender import router as recommender_router
from app.routers.tasks import router as tasks_router
from app.integrations.storage.minio_client import ensure_bucket_exists

_log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    try:
        ensure_bucket_exists()
    except Exception:
        _log.warning('MinIO bucket check/create failed; presigned uploads may be unavailable', exc_info=True)
    yield


app = FastAPI(title='Universal CRM API', version='0.2.0', lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
app.include_router(projects_router, prefix="/api/v1")
app.include_router(tasks_router, prefix="/api/v1")
app.include_router(ai_router, prefix="/api/v1")
app.include_router(openclaw_router, prefix="/api/v1")
app.include_router(documents_router, prefix="/api/v1")
app.include_router(proactive_router, prefix="/api/v1")
app.include_router(recommender_router, prefix="/api/v1")


@app.exception_handler(ValueError)
async def value_error_handler(_request: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={'detail': str(exc)})


@app.get('/health')
async def health() -> dict[str, str]:
    return {'status': 'ok'}
