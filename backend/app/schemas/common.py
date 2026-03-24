from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ListParams(BaseModel):
    limit: int = 50
    offset: int = 0
