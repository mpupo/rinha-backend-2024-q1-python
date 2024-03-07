from abc import ABC

from sqlalchemy import select, update
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
        # Removed the code below because it increased the RAM consumption.
        # model = ClientModel(**client.model_dump())
        # await self.db.merge(model)
        stmt = (
            update(ClientModel)
            .where(ClientModel.id == client.id)
            .values(balance=client.balance)
        )
        await self.db.execute(stmt)

    async def get(
        self, id: int, with_transactions: bool = False
    ) -> ClientSchema | ClientSchemaWithTransactions:
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
            else ClientSchema.model_construct(
                _fields_set={"id", "limit", "balance"},
                **{"id": model.id, "limit": model.limit, "balance": model.balance},
            )
        )


class TransactionRepository(Repository):
    async def add(self, new_model: TransactionCreateSchema) -> None:
        model = TransactionModel(**new_model.model_dump())
        self.db.add(model)
