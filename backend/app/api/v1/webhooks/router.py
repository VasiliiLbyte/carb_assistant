from fastapi import APIRouter
from pydantic import BaseModel
from app.services.proactive.response_handler import handle_response

router = APIRouter(prefix='/webhooks', tags=['webhooks'])


class ProactiveResponse(BaseModel):
    message_id: str | None = None
    user_id: str | None = None
    payload: dict = {}


@router.post('/proactive_response')
async def proactive_response(data: ProactiveResponse) -> dict:
    return await handle_response(data.model_dump())
