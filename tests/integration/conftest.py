import asyncio
import logging
from typing import AsyncGenerator, Generator
from sqlalchemy import create_engine

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncSession, async_sessionmaker, create_async_engine
from src.rinha.config.settings import settings

from src.rinha.database.orm.models import Base
from src.rinha.database.orm.session import get_db_session
from src.rinha.main import app as actual_app
from sqlalchemy import text

import os
import pytest
from testcontainers.postgres import PostgresContainer

from pathlib import Path


@pytest.fixture(scope="session")
def event_loop(request) -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Get the directory of the current script
current_dir = Path(__file__).resolve().parent

# Move two directories up to reach the root directory
root_dir = current_dir.parent.parent

# Construct the path to script.sql
script_path = root_dir / "script.sql"

postgres = PostgresContainer('postgres:9.5', driver="psycopg2").with_volume_mapping(
    host=str(script_path),
    container='/docker-entrypoint-initdb.d/script.sql'
).with_volume_mapping(
    host=str(root_dir/'postgresql.conf'),
    container="/etc/postgresql/postgresql.conf"
)


@pytest.fixture(scope="module", autouse=True)
def setup(request):
    logging.info("Iniciando container postgres")
    postgres.start()

    def remove_container():
        logging.info("Removendo container postgres")
        #postgres.stop()

    #request.addfinalizer(remove_container)

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

    logging.info(f"Conectando ao banco: {settings.db.db_url}")
    engine = create_async_engine(settings.db.db_url)

    #async with engine.begin() as conn:
        #await conn.run_sync(Base.metadata.drop_all)
        #await conn.run_sync(Base.metadata.create_all)

    session = async_sessionmaker(engine)()
    yield session
    await session.close()


@pytest.fixture
def test_app(async_db: AsyncSession) -> FastAPI:
    """Create a test app with overridden dependencies."""
    #actual_app.dependency_overrides[get_db_session] = lambda: async_db
    return actual_app


@pytest_asyncio.fixture
async def client(test_app: FastAPI) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=test_app, base_url="http://test") as client:
        yield client
