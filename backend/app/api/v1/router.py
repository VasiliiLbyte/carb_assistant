from fastapi import APIRouter
from app.api.v1.auth.router import router as auth_router
from app.api.v1.users.router import router as users_router
from app.api.v1.documents.router import router as documents_router
from app.api.v1.risks.router import router as risks_router
from app.api.v1.ai.router import router as ai_router
from app.api.v1.proactive.router import router as proactive_router
from app.api.v1.webhooks.router import router as webhooks_router
from app.api.v1.knowledge.router import router as knowledge_router

api_router = APIRouter()
for r in [auth_router, users_router, documents_router, risks_router, ai_router, proactive_router, webhooks_router, knowledge_router]:
    api_router.include_router(r)
