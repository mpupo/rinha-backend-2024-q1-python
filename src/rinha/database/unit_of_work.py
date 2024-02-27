import abc
from types import TracebackType
from typing import AsyncIterator

import sqlalchemy
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.rinha.config.settings import settings
from src.rinha.database import repository


class AbstractUnitOfWork(abc.ABC):
    clients: repository.ClientRepository
    transactions: repository.TransactionRepository


engine_params = {
    "echo": "debug" if settings.ECHO_SQL else settings.ECHO_SQL,
    "future": True,
    # "isolation_level": "REPEATABLE READ",
    "pool_size": settings.DB.DB_POOL_SIZE,
    "max_overflow": settings.DB.DB_MAX_OVERFLOW,
    "pool_timeout": settings.DB.DB_POOL_TIMEOUT,
}
session_params = {"autocommit": False, "autoflush": False, "expire_on_commit": False}


engine: AsyncEngine = create_async_engine(settings.DB.db_url, **engine_params)
sessionmaker = async_sessionmaker(bind=engine, **session_params)


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session: AsyncSession):
        self.session = session

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
        except sqlalchemy.exc.SQLAlchemyError:
            pass
        else:
            await self.session.commit()
        finally:
            await self.session.close()


async def get_db_session() -> AsyncIterator[SqlAlchemyUnitOfWork]:
    session = sessionmaker()
    yield session
