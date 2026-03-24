from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette import status

from app.api.v1.router import api_router

app = FastAPI(title='Universal CRM API', version='0.2.0')
app.include_router(api_router, prefix='/api/v1')


@app.exception_handler(ValueError)
async def value_error_handler(_request: Request, exc: ValueError) -> JSONResponse:
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={'detail': str(exc)})


@app.get('/health')
async def health() -> dict[str, str]:
    return {'status': 'ok'}
