"""Proactive module router (rules + trigger)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import LLMClient, get_db, get_llm_client, require_roles
from app.proactive.proactive_engine import ProactiveEngine
from app.proactive.schemas import (
    ProactiveRuleCreate,
    ProactiveRuleOut,
    ProactiveRuleUpdate,
    ProactiveTriggerRequest,
    ProactiveTriggerResponse,
)

router = APIRouter(prefix="/proactive", tags=["proactive"])


@router.get("/rules", response_model=list[ProactiveRuleOut])
async def list_rules(
    session: AsyncSession = Depends(get_db),
    llm_client: LLMClient = Depends(get_llm_client),
    _user: dict = Depends(require_roles("admin", "pm", "engineer", "viewer")),
) -> list[ProactiveRuleOut]:
    """List proactive rules."""

    engine = ProactiveEngine(db=session, llm_client=llm_client)
    rules = await engine.list_rules()
    return [ProactiveRuleOut.model_validate({**item.__dict__, "id": str(item.id)}) for item in rules]


@router.post("/rules", response_model=ProactiveRuleOut, status_code=status.HTTP_201_CREATED)
async def create_rule(
    payload: ProactiveRuleCreate,
    session: AsyncSession = Depends(get_db),
    llm_client: LLMClient = Depends(get_llm_client),
    _user: dict = Depends(require_roles("admin", "pm")),
) -> ProactiveRuleOut:
    """Create proactive rule."""

    engine = ProactiveEngine(db=session, llm_client=llm_client)
    item = await engine.create_rule(payload.model_dump())
    return ProactiveRuleOut.model_validate({**item.__dict__, "id": str(item.id)})


@router.put("/rules/{rule_id}", response_model=ProactiveRuleOut)
async def update_rule(
    rule_id: str,
    payload: ProactiveRuleUpdate,
    session: AsyncSession = Depends(get_db),
    llm_client: LLMClient = Depends(get_llm_client),
    _user: dict = Depends(require_roles("admin", "pm")),
) -> ProactiveRuleOut:
    """Update proactive rule."""

    engine = ProactiveEngine(db=session, llm_client=llm_client)
    item = await engine.update_rule(rule_id, payload.model_dump(exclude_unset=True))
    return ProactiveRuleOut.model_validate({**item.__dict__, "id": str(item.id)})


@router.delete("/rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rule(
    rule_id: str,
    session: AsyncSession = Depends(get_db),
    llm_client: LLMClient = Depends(get_llm_client),
    _user: dict = Depends(require_roles("admin", "pm")),
) -> Response:
    """Delete proactive rule."""

    engine = ProactiveEngine(db=session, llm_client=llm_client)
    await engine.delete_rule(rule_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/trigger", response_model=ProactiveTriggerResponse)
async def trigger_ping(
    payload: ProactiveTriggerRequest,
    session: AsyncSession = Depends(get_db),
    llm_client: LLMClient = Depends(get_llm_client),
    _user: dict = Depends(require_roles("admin", "pm", "engineer")),
) -> ProactiveTriggerResponse:
    """Manually trigger proactive ping for a task and rule."""

    engine = ProactiveEngine(db=session, llm_client=llm_client)
    ping = await engine.send_proactive_ping(payload.rule_id, payload.task_id)
    return ProactiveTriggerResponse(sent=True, ping=ping)
