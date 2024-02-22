import abc
import logging
from typing import Any, AsyncIterator
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)
from src.rinha.config.settings import settings

from src.rinha.database import repository


class AbstractUnitOfWork(abc.ABC):
    clients: repository.ClientRepository
    transactions: repository.TransactionRepository

    async def __aexit__(self, exn_type, exn_value, traceback):
        if exn_type is not None:
            logging.exception("Ocorreu um erro inesperado!")
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
    def __init__(
        self,
        host: str,
        engine_kwargs: dict[str, Any] = {},
        session_kwargs: dict[str, Any] = {},
    ):
        self._engine: AsyncEngine = create_async_engine(host, **engine_kwargs)
        self._sessionmaker = async_sessionmaker(bind=self._engine, **session_kwargs)

    async def __aenter__(self):
        self.session: AsyncSession = self._sessionmaker()
        self.clients = repository.ClientRepository(self.session)
        self.transactions = repository.TransactionRepository(self.session)

    async def __aexit__(self, *args):
        await super().__aexit__(*args)
        await self._engine.dispose()
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
    uow = SqlAlchemyUnitOfWork(
        settings.db.db_url,
        {
            "echo": settings.echo_sql,
            "future": True,
            # "isolation_level": "REPEATABLE READ",
        },
        {"autocommit": False, "autoflush": False, "expire_on_commit": True},
    )
    yield uow
