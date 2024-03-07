import abc
import logging
from asyncio import current_task
from types import TracebackType

import sqlalchemy
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)

from src.rinha.config.settings import PostgresSettings
from src.rinha.database import repository


class AbstractUnitOfWork(abc.ABC):
    clients: repository.ClientRepository
    transactions: repository.TransactionRepository

    @abc.abstractmethod
    async def __aenter__(self):
        raise NotImplementedError

    @abc.abstractmethod
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ):
        raise NotImplementedError


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    engine: AsyncEngine
    sessionmaker: async_sessionmaker
    registry: async_scoped_session
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
            "echo": False,
            "future": True,
            "pool_size": settings.DB_POOL_SIZE,
            "echo_pool": False,
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

        # Much better than echo and echo_pool from engine params:
        if echo_sql:
            logging.getLogger("sqlalchemy.engine").setLevel(logging.DEBUG)
        if echo_pool:
            logging.getLogger("sqlalchemy.pool").setLevel(logging.DEBUG)

    @classmethod
    async def dispose(cls) -> None:
        await cls.engine.dispose()

    async def __aenter__(self):
        if not self.initialized:
            raise ValueError(
                "UnitOfWork is not initialized. Call initialize method first."
            )
        self.session = self.sessionmaker()
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
            logging.exception(f"Error: {e}")
            raise
        else:
            await self.session.commit()
        finally:
            await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()


async def get_db_session() -> SqlAlchemyUnitOfWork:
    logging.debug(
        f"Pool:{SqlAlchemyUnitOfWork.engine.pool.status()}, EngineID: {id(SqlAlchemyUnitOfWork.engine)}"
    )
    return SqlAlchemyUnitOfWork()
