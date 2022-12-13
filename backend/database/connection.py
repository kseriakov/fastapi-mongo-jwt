from typing import TypeVar
from pydantic import BaseModel, BaseSettings
from beanie import Document, init_beanie, PydanticObjectId
from motor.motor_asyncio import AsyncIOMotorClient

from users.models import User


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_MINUTES: int
    TOKEN_URL: str

    class Config:
        env_file = ".env"

    async def init_connection(self):
        client = AsyncIOMotorClient(self.DATABASE_URL)
        await init_beanie(database=client.db_name, document_models=[User])


D = TypeVar("D", bound=Document)


class Database:
    def __init__(self, model: D):
        self.model = model

    async def create(self, document: D):
        return await document.create()

    async def get_by_id(self, id: PydanticObjectId):
        return await self.model.get(id) or False

    async def update(self, id: PydanticObjectId, data: BaseModel):
        document = await self.get(id)

        if not document:
            return False

        updated_data = {k: v for k, v in data.dict().items() if v is not None}
        await document.update({"$set": updated_data})
        return document

    async def delete(self, id: PydanticObjectId):
        document = await self.get(id)

        if not document:
            return False

        await document.delete()
        return True
