from abc import ABC

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.rinha.database.orm.models import ClientModel, TransactionModel
from src.rinha.domain.schemas import (
    ClientSchema,
    ClientSchemaWithTransactions,
    TransactionCreateSchema,
)


class Repository(ABC):
    def __init__(self, db: AsyncSession):
        self.db = db


class ClientRepository(Repository):
    async def update(self, client: ClientSchema) -> None:
        model = ClientModel(**client.model_dump())
        await self.db.merge(model)

    async def get(
        self, id: int, with_transactions: bool = False
    ) -> ClientSchemaWithTransactions:
        if with_transactions:
            query = (
                select(ClientModel)
                .options(joinedload(ClientModel.transactions))
                .fetch(10)
                .filter(ClientModel.id == id)
            )
        else:
            query = select(ClientModel).filter(ClientModel.id == id)
        model = (await self.db.execute(query)).unique().scalar_one_or_none()
        return (
            ClientSchemaWithTransactions.model_validate(model)
            if with_transactions
            else ClientSchema.model_validate(model)
        )


class TransactionRepository(Repository):
    async def add(self, new_model: TransactionCreateSchema) -> None:
        model = TransactionModel(**new_model.model_dump())
        self.db.add(model)
