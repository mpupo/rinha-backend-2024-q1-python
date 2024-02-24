import asyncio
import logging
from pathlib import Path
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer

from src.rinha.config.settings import settings
from src.rinha.database.unit_of_work import SqlAlchemyUnitOfWork, get_db_session
from src.rinha.main import app as actual_app


@pytest.fixture(scope="session")
def event_loop(request) -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module", autouse=True)
def setup(request):
    current_dir = Path(__file__).resolve().parent
    root_dir = current_dir.parent.parent

    postgres = (
        PostgresContainer("postgres:latest", driver="psycopg2")
        .with_volume_mapping(
            host=str(root_dir / "postgresql/script.sql"),
            container="/docker-entrypoint-initdb.d/script.sql",
        )
        .with_volume_mapping(
            host=str(root_dir / "postgresql/postgresql.conf"),
            container="/etc/postgresql/postgresql.conf",
        )
    )
    logging.info("Starting PostgresSQL container!")
    postgres.start()

    def remove_container():
        logging.info("Removing PostgresSQL container!")
        postgres.stop()

    request.addfinalizer(remove_container)

    settings.db.DB_HOST = postgres.get_container_host_ip()
    settings.db.DB_NAME = postgres.POSTGRES_DB
    settings.db.DB_USER = postgres.POSTGRES_USER
    settings.db.DB_PASSWORD = postgres.POSTGRES_PASSWORD
    settings.db.DB_PORT = postgres.get_exposed_port(5432)


# @pytest.fixture(scope="function", autouse=True)
# def setup_data():
#     logging.info(f"Conectando ao banco: {postgres.get_connection_url()}")
#     engine = create_engine(postgres.get_connection_url())
#
#     with engine.begin() as connection:
#         connection.execute(text("DELETE FROM transacoes;"))


@pytest_asyncio.fixture()
async def async_db() -> AsyncGenerator[AsyncSession, None]:
    """Start a test database session."""

    logging.info(f"Connecting to the database: {settings.db.db_url}")
    engine = create_async_engine(settings.db.db_url)

    # async with engine.begin() as conn:
    # await conn.run_sync(Base.metadata.drop_all)
    # await conn.run_sync(Base.metadata.create_all)

    session = async_sessionmaker(engine)()
    yield session
    await session.close()


@pytest_asyncio.fixture
async def test_app(async_db: AsyncSession) -> FastAPI:
    """Create a test app with overridden dependencies."""
    await SqlAlchemyUnitOfWork.initialize(
        settings.db.db_url,
        {
            "echo": "debug" if settings.echo_sql else settings.echo_sql,
            "future": True,
            # "isolation_level": "REPEATABLE READ",
            "pool_size": settings.db.DB_POOL_SIZE,
            "max_overflow": settings.db.DB_MAX_OVERFLOW,
            "pool_timeout": settings.db.DB_POOL_TIMEOUT,
        },
        {"autocommit": False, "autoflush": False, "expire_on_commit": False},
    )
    uow = await SqlAlchemyUnitOfWork.create()
    actual_app.dependency_overrides[get_db_session] = lambda: uow
    return actual_app


@pytest_asyncio.fixture
async def client(test_app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=test_app, base_url="http://test") as client:
        yield client
