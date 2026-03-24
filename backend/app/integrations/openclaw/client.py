import httpx
from app.core.config import settings


class OpenClawClient:
    def __init__(self) -> None:
        self.base_url = settings.openclaw_base_url
        self.headers = {'Authorization': f'Bearer {settings.openclaw_api_key}'}

    async def send_message(self, payload: dict) -> dict:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(f'{self.base_url}/messages/send', json=payload, headers=self.headers)
            return {'status_code': response.status_code, 'body': response.text}
