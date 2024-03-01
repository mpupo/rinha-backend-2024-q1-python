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
        echo_sql: bool,
        echo_pool: bool,
        override: bool = False,
        engine_kwargs: dict[str, object] = {},
        session_kwargs: dict[str, object] = {},
    ):
        engine_params = {
            "echo": False,  # "debug" if echo_sql else echo_sql,
            "future": True,
            # "isolation_level": "REPEATABLE READ",
            "pool_size": settings.DB_POOL_SIZE,
            "echo_pool": False,  # "debug" if echo_pool else echo_pool,
            "max_overflow": settings.DB_MAX_OVERFLOW,
            "pool_timeout": settings.DB_POOL_TIMEOUT,
            "pool_pre_ping": settings.DB_POOL_PREPING,
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

        if echo_pool or echo_sql:
            # Much better than echo and echo_pool from engine params:
            for module in ["sqlalchemy.pool", "sqlalchemy.engine"]:
                logging.getLogger(module).setLevel(logging.DEBUG)

    @classmethod
    async def create(cls, transaction: bool = False):
        if not cls.initialized:
            raise ValueError(
                "UnitOfWork is not initialized. Call initialize method first."
            )
        instance_session = cls.sessionmaker()
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
        return self

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
        # else:
        # Removed due to the session.begin()
        #    await self.session.commit()
        # finally:
        #    await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()


async def get_db_session() -> AsyncIterator[SqlAlchemyUnitOfWork]:
    logging.debug(
        f"Pool:{SqlAlchemyUnitOfWork.engine.pool.status()}, EngineID: {id(SqlAlchemyUnitOfWork.engine)}"
    )
    async with SqlAlchemyUnitOfWork.sessionmaker() as session:
        async with session.begin():
            yield SqlAlchemyUnitOfWork(session=session)
