from abc import ABC, abstractmethod

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.rinha.database.orm.models import ClientModel, TransactionModel
from src.rinha.domain.schemas import (
    ClientSchema,
    ClientSchemaWithTransactions,
    TransactionCreateSchema,
    TransactionSchema,
)


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

    async def get(
        self, client_id: int, with_transactions: bool = False
    ) -> ClientSchema | ClientSchemaWithTransactions:
        if with_transactions:
            query = (
                select(ClientModel)
                .options(joinedload(ClientModel.transactions))
                .fetch(10)
                .filter(ClientModel.id == client_id)
            )
        else:
            query = select(ClientModel).filter(ClientModel.id == client_id)
        model = (await self.db.execute(query)).unique().scalar_one_or_none()
        return (
            ClientSchemaWithTransactions.model_validate(model)
            if with_transactions
            else ClientSchema.model_validate(model)
        )


class TransactionRepository(Repository[TransactionSchema]):
    async def add(
        self, transaction: TransactionCreateSchema, client: ClientSchema
    ) -> None:
        model = TransactionModel(**transaction.model_dump())
        self.db.add(model)

    async def get(self, client_id: int) -> TransactionSchema:
        raise NotImplementedError
