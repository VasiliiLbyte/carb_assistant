from pydantic import BaseModel


class OpenClawMessageRequest(BaseModel):
    channel: str
    recipient: str
    text: str
    buttons: list[dict] = []
