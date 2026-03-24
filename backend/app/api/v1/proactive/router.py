from fastapi import APIRouter
from pydantic import BaseModel
from app.integrations.openclaw.client import OpenClawClient

router = APIRouter(prefix='/proactive', tags=['proactive'])
_rules: list[dict] = []


class RulePayload(BaseModel):
    name: str
    trigger_type: str
    action_type: str = 'send_message'
    config: dict = {}


class SendPayload(BaseModel):
    channel: str
    recipient: str
    text: str
    buttons: list[dict] = []


@router.get('/rules')
async def list_rules() -> list[dict]:
    return _rules


@router.post('/rules')
async def create_rule(payload: RulePayload) -> dict:
    item = payload.model_dump()
    _rules.append(item)
    return item


@router.post('/send')
async def send(payload: SendPayload) -> dict:
    return await OpenClawClient().send_message(payload.model_dump())
