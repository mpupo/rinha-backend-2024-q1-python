from abc import ABC, abstractmethod
import logging

from sqlalchemy import select
from src.rinha.database.orm.models import TransactionModel, ClientModel
from src.rinha.database.schemas import TransactionCreateSchema
from src.rinha.domain.models import Client

from src.rinha.domain.models.transaction import Transaction
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Repository[T](ABC):
    def __init__(self, db: AsyncSession):
        self.db = db

    @abstractmethod
    async def add(self, **kwargs: object) -> None:
        raise NotImplementedError

    @abstractmethod
    async def get(self, client_id: int) -> T:
        raise NotImplementedError


class ClientRepository(Repository[Client]):
    async def add(self, client: Client | ClientModel) -> None:
        logger.info(f"Creating client [{client.id}, {client.limit}, {client.balance}]")
        self.db.add(client)
        logger.info(
            f"Done creating client [{client.id}, {client.limit}, {client.balance}]"
        )

    async def get(self, client_id: int) -> ClientModel:
        logger.info(f"Searching for client {client_id}.")
        client = (
            await self.db.execute(
                select(ClientModel).filter(ClientModel.id == client_id)
            )
        ).scalar_one_or_none()
        logger.info(f"Client found! [{client.id}, {client.limit}, {client.balance}]")
        return client


class TransactionRepository(Repository[Transaction]):
    async def add(self, transaction: Transaction, client: ClientModel) -> None:
        logger.info(f"Creating transaction for client {client.id}.")
        schema = TransactionCreateSchema.model_validate(transaction)
        db_model = TransactionModel(
            client_id=schema.client_id,
            type=schema.type.value,
            description=schema.description,
            value=schema.value,
        )
        db_model.client = client
        logger.info(
            f"Inserting transaction ({db_model.type}, {db_model.value}) for client {client.id}."
        )
        self.db.add(db_model)
        logger.info(
            f"Done inserting transaction ({db_model.type}, {db_model.value}) for client {client.id}."
        )

    async def get(self, client_id: int) -> Transaction:
        raise NotImplementedError
