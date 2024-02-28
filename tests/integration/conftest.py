import asyncio
import logging
from pathlib import Path
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient
from rinha.database.orm.models import Base
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer

from src.rinha.config.settings import settings
from src.rinha.database.unit_of_work import SqlAlchemyUnitOfWork, get_db_session
from src.rinha.main import app as actual_app

current_dir = Path(__file__).resolve().parent
root_dir = current_dir.parent.parent


@pytest.fixture(scope="session")
def event_loop(request) -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def dml() -> str:
    with open(root_dir / "postgresql/dml.sql", "r") as dml:
        content = dml.read()
        return content


postgres = (
    PostgresContainer("postgres:latest", driver="psycopg2")
    .with_volume_mapping(
        host=str(root_dir / "postgresql/ddl.sql"),
        container="/docker-entrypoint-initdb.d/ddl.sql",
    )
    .with_volume_mapping(
        host=str(root_dir / "postgresql/dml.sql"),
        container="/docker-entrypoint-initdb.d/dml.sql",
    )
    .with_volume_mapping(
        host=str(root_dir / "postgresql/postgresql.conf"),
        container="/etc/postgresql/postgresql.conf",
    )
)


@pytest.fixture(scope="module", autouse=True)
def setup(request):
    logging.info("Starting PostgresSQL container!")
    postgres.start()

    def remove_container():
        logging.info("Removing PostgresSQL container!")
        postgres.stop()

    request.addfinalizer(remove_container)

    settings.DB.DB_HOST = postgres.get_container_host_ip()
    settings.DB.DB_NAME = postgres.POSTGRES_DB
    settings.DB.DB_USER = postgres.POSTGRES_USER
    settings.DB.DB_PASSWORD = postgres.POSTGRES_PASSWORD
    settings.DB.DB_PORT = postgres.get_exposed_port(5432)
    settings.ECHO_SQL = False
    settings.DEBUG = False


@pytest_asyncio.fixture()
async def async_db(dml: str) -> AsyncGenerator[AsyncSession, None]:
    """Start a test database session."""
    engine = create_async_engine(settings.DB.db_url)
    logging.info("Creating a database session for tests")

    session = async_sessionmaker(engine)()
    yield session
    await session.close()

    async with engine.begin() as conn:
        logging.info("Wiping database")
        await conn.execute(text("DROP TABLE clientes, transacoes CASCADE;"))
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(text(dml))


@pytest_asyncio.fixture
async def test_app(async_db) -> FastAPI:
    """Create a test app with overridden dependencies."""
    await SqlAlchemyUnitOfWork.initialize(
        settings=settings.DB, echo=settings.ECHO_SQL, override=True
    )
    uow = await SqlAlchemyUnitOfWork.create(transaction=True)
    actual_app.dependency_overrides[get_db_session] = lambda: uow
    return actual_app


@pytest_asyncio.fixture
async def client(test_app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=test_app, base_url="http://test") as client:
        yield client
