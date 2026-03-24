from app.tasks.celery_app import celery_app


@celery_app.task(name='proactive.tick')
def proactive_tick() -> str:
    return 'ok'
