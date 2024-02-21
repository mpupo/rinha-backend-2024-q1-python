from abc import ABC, abstractmethod
import logging
from typing import Tuple

from sqlalchemy import select, update
from src.rinha.database.orm.models import TransactionModel, ClientModel
from src.rinha.database.schemas import TransactionCreateSchema
from src.rinha.domain.models import Client

from src.rinha.domain.models.transaction import Transaction
from sqlalchemy.ext.asyncio import AsyncSession
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


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

    async def add(self, client: Client | ClientModel) -> None:
        logger.info(f"Creating client [{client.id}, {client.limite}, {client.saldo}]")
        self.db.add(client)
        logger.info(f"Done creating client [{client.id}, {client.limite}, {client.saldo}]")

    # async def get(self, client_id: int) -> Client:
    #     cliente = (await self.db.execute(select(ClientModel).filter(ClientModel.id == client_id))).scalar_one_or_none()
    #     return Client(id=cliente.id, limit=cliente.limite, balance=cliente.saldo)

    async def get(self, client_id: int) -> ClientModel:
        logger.info(f"Searching for client {client_id}.")
        client = (await self.db.execute(select(ClientModel).filter(ClientModel.id == client_id))).scalar_one_or_none()
        logger.info(f"Client found! [{client.id}, {client.limite}, {client.saldo}]")
        return client
    
    async def update_balance(self, client_id: int, balance: int) -> ClientModel:
        model = (await self.db.execute(select(ClientModel).filter(ClientModel.id == client_id))).scalar_one_or_none()
        logger.info(f"Updating balance for client {model.id}. {model.saldo} to {balance}")
        model.saldo = balance
        logger.info(f"Balance updated! {model.saldo} to {balance}")
        return model

class TransactionRepository(Repository[Transaction]):

    async def add(self, transaction: Transaction, client: ClientModel) -> None:
        logger.info(f"Creating transaction for client {client.id}.")
        schema = TransactionCreateSchema.from_domain(transaction=transaction)
        db_model = TransactionModel(
            cliente_id=schema.cliente_id,
            tipo=schema.tipo.value,
            descricao=schema.descricao,
            valor=schema.valor
        )
        db_model.client = client
        logger.info(f"Inserting transaction ({db_model.tipo}, {db_model.valor}) for client {client.id}.")
        self.db.add(db_model)
        logger.info(f"Done inserting transaction ({db_model.tipo}, {db_model.valor}) for client {client.id}.")
        return None

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
