from pydantic import BaseModel


class ItemCreate(BaseModel):
    name: str
    description: str


class ItemResponse(BaseModel):
    name: str
    description: str
    author: str