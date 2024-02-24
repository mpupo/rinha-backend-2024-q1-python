import abc
import logging
from types import TracebackType
from typing import Any, AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.rinha.database import repository


class AbstractUnitOfWork(abc.ABC):
    clients: repository.ClientRepository
    transactions: repository.TransactionRepository

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ):
        if exc_type is not None:
            logging.exception(f"Ocorreu um erro! {exc_val}")
            await self.rollback()

    @abc.abstractmethod
    async def commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    async def rollback(self):
        raise NotImplementedError

    @abc.abstractmethod
    async def begin(self):
        raise NotImplementedError

    @abc.abstractmethod
    async def refresh(self):
        raise NotImplementedError


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    _engine: AsyncEngine | None
    _sessionmaker: async_sessionmaker | None
    _initialized: bool = False

    @classmethod
    async def initialize(
        cls,
        host: str,
        engine_kwargs: dict[str, Any] = {},
        session_kwargs: dict[str, Any] = {},
    ):
        cls._engine = create_async_engine(host, **engine_kwargs)
        cls._sessionmaker = async_sessionmaker(bind=cls._engine, **session_kwargs)
        cls._initialized = True

    @classmethod
    async def create(cls):
        if not cls._initialized:
            raise ValueError(
                "UnitOfWork is not initialized. Call initialize method first."
            )
        instance_session = cls._sessionmaker()
        instance = cls(session=instance_session)
        return instance

    @classmethod
    async def dispose(cls) -> None:
        await cls._engine.dispose()

    def __init__(self, session: AsyncSession):
        self.session = session
        self.clients: repository.ClientRepository | None = None
        self.transactions: repository.TransactionRepository | None = None

    async def __aenter__(self):
        self.clients = repository.ClientRepository(self.session)
        self.transactions = repository.TransactionRepository(self.session)

    async def __aexit__(self, *args):
        await super().__aexit__(*args)
        await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()

    async def begin(self):
        await self.session.begin()

    async def refresh(self, object: Any):
        await self.session.refresh(object)


async def get_db_session() -> AsyncIterator[SqlAlchemyUnitOfWork]:
    uow = await SqlAlchemyUnitOfWork.create()
    yield uow
