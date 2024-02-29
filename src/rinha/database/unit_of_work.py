import abc
import logging
from asyncio import current_task
from types import TracebackType
from typing import AsyncIterator

import sqlalchemy
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)

from src.rinha.config.settings import PostgresSettings
from src.rinha.database import repository


class AbstractUnitOfWork(abc.ABC):
    clients: repository.ClientRepository
    transactions: repository.TransactionRepository


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    engine: AsyncEngine | None
    sessionmaker: async_sessionmaker | None
    registry: async_scoped_session | None
    initialized: bool = False

    @classmethod
    async def initialize(
        cls,
        settings: PostgresSettings,
        echo: bool,
        override: bool = False,
        engine_kwargs: dict[str, object] = {},
        session_kwargs: dict[str, object] = {},
    ):
        engine_params = {
            "echo": "debug" if echo else echo,
            "future": True,
            # "isolation_level": "REPEATABLE READ",
            "pool_size": settings.DB_POOL_SIZE,
            "max_overflow": settings.DB_MAX_OVERFLOW,
            "pool_timeout": settings.DB_POOL_TIMEOUT,
            **engine_kwargs,
        }
        session_params = {
            "autocommit": False,
            "autoflush": False,
            "expire_on_commit": False,
            **session_kwargs,
        }
        if not cls.initialized or override:
            cls.engine = create_async_engine(settings.db_url, **engine_params)
            cls.sessionmaker = async_sessionmaker(bind=cls.engine, **session_params)
            cls.registry = async_scoped_session(
                cls.sessionmaker, scopefunc=current_task
            )
            cls.initialized = True

    @classmethod
    async def create(cls, transaction: bool = False):
        if not cls.initialized:
            raise ValueError(
                "UnitOfWork is not initialized. Call initialize method first."
            )
        instance_session = cls.registry()
        if transaction:
            await instance_session.begin()
        instance = cls(session=instance_session)
        return instance

    @classmethod
    async def dispose(cls) -> None:
        await cls.engine.dispose()

    def __init__(self, session: AsyncSession):
        self.session = session
        self.clients: repository.ClientRepository | None = None
        self.transactions: repository.TransactionRepository | None = None

    async def __aenter__(self):
        self.clients = repository.ClientRepository(self.session)
        self.transactions = repository.TransactionRepository(self.session)

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ):
        try:
            if exc_type is not None:
                await self.session.rollback()
        except sqlalchemy.exc.SQLAlchemyError as e:
            logging.exception(f"Ocorreu um erro: {e}")
            raise
        else:
            await self.session.commit()
        finally:
            # await self.session.close()
            await type(self).registry.remove()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()


async def get_db_session() -> AsyncIterator[SqlAlchemyUnitOfWork]:
    uow = await SqlAlchemyUnitOfWork.create()
    return uow
