from abc import ABC, abstractmethod

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from rinha.domain.schemas import (
    ClientSchema,
    TransactionCreateSchema,
    TransactionSchema,
)
from src.rinha.database.orm.models import ClientModel, TransactionModel


class Repository[T](ABC):
    def __init__(self, db: AsyncSession):
        self.db = db

    @abstractmethod
    async def add(self, **kwargs: object) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get(self, client_id: int) -> T:
        raise NotImplementedError


class ClientRepository(Repository[ClientSchema]):
    async def add(self, **kwargs: object) -> None:
        raise NotImplementedError

    async def update(self, client: ClientSchema) -> None:
        model = ClientModel(**client.model_dump())
        await self.db.merge(model)

    async def get(self, client_id: int) -> ClientSchema:
        model = (
            await self.db.execute(
                select(ClientModel).filter(ClientModel.id == client_id)
            )
        ).scalar_one_or_none()
        return ClientSchema.model_validate(model)


class TransactionRepository(Repository[TransactionSchema]):
    async def add(
        self, transaction: TransactionCreateSchema, client: ClientSchema
    ) -> None:
        model = TransactionModel(**transaction.model_dump())
        client_model = (
            await self.db.execute(
                select(ClientModel).filter(ClientModel.id == client.id)
            )
        ).scalar_one_or_none()
        model.client = client_model
        self.db.add(model)

    async def get(self, client_id: int) -> TransactionSchema:
        raise NotImplementedError
