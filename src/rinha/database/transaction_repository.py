from abc import ABC, abstractmethod
import logging
from typing import Tuple

from sqlalchemy import select
from src.rinha.database.orm.models import TransactionModel, ClientModel
from src.rinha.database.schemas import TransactionCreateSchema
from src.rinha.domain.models import Client

from src.rinha.domain.models.transaction import Transaction
from sqlalchemy.ext.asyncio import AsyncSession


class Repository[T](ABC):
    def __init__(self, db: AsyncSession):
        self.db = db

    @abstractmethod
    async def get_all(self, client_id: int) -> Tuple[T]:
        raise NotImplementedError

    @abstractmethod
    async def add(self, **kwargs: object) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get(self, client_id: int) -> T:
        raise NotImplementedError


class ClientRepository(Repository[Client]):

    async def get_all(self, client_id: int) -> Tuple[Client]:
        pass

    async def add(self, **kwargs: object) -> None:
        pass

    async def get(self, client_id: int) -> Client | None:
        cliente = (await self.db.execute(select(ClientModel).filter(ClientModel.id == client_id))).scalar_one_or_none()
        if not cliente:
            return None
        return Client(id=cliente.id, limit=cliente.limite, initial_value=cliente.saldo_inicial)


class TransactionRepository(Repository[Transaction]):

    async def add(self, transaction: Transaction) -> None:
        schema = TransactionCreateSchema.from_domain(transaction=transaction)
        logging.info
        db_model = TransactionModel(
            cliente_id=schema.cliente_id,
            tipo=schema.tipo.value,
            descricao=schema.descricao
        )
        self.db.add(db_model)
        await self.db.commit()

    async def get_all(self, client_id: int) -> Tuple[Transaction]:
        transactions = (
            await self.db.scalars(
                select(TransactionModel).where(TransactionModel.cliente_id == client_id)
            )
        ).all()
        return tuple(
            Transaction(
                id=transaction.id,
                client_id=transaction.cliente_id,
                type=transaction.tipo,
                description=transaction.descricao,
                created_at=transaction.realizada_em,
            )
            for transaction in transactions
        )

    def get(self, client_id: int) -> Transaction:
        raise NotImplementedError
