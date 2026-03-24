from fastapi import APIRouter
from app.schemas.ai import AISuggestTaskRequest, AIAssigneeRequest, AIResponse
from app.services.ai.task_auto_creator import suggest_task
from app.services.ai.recommender import suggest_assignee
from app.services.ai.competency_load_manager import load_analysis
from app.services.ai.task_updater import reassign_tasks

router = APIRouter(prefix='/ai', tags=['ai'])


@router.post('/suggest_task', response_model=AIResponse)
async def suggest_task_endpoint(payload: AISuggestTaskRequest):
    return {'result': await suggest_task(payload.text, payload.project_id)}


@router.post('/create_task', response_model=AIResponse)
async def create_task_endpoint(payload: AISuggestTaskRequest):
    draft = await suggest_task(payload.text, payload.project_id)
    draft['status'] = 'to-do'
    return {'result': draft}


@router.post('/suggest_assignee', response_model=AIResponse)
async def suggest_assignee_endpoint(payload: AIAssigneeRequest):
    return {'result': await suggest_assignee(payload.task_title, payload.required_skills)}


@router.get('/load_analysis', response_model=AIResponse)
async def load_analysis_endpoint():
    return {'result': await load_analysis()}


@router.post('/reassign_tasks', response_model=AIResponse)
async def reassign_tasks_endpoint():
    return {'result': await reassign_tasks()}
