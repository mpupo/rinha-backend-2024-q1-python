import logging
import sys
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from src.rinha.api.models.healthcheck import HealthCheck
from src.rinha.api.routers.clientes import router as clientes_router
from src.rinha.config.settings import settings
from src.rinha.database.unit_of_work import SqlAlchemyUnitOfWork

logging.basicConfig(
    stream=sys.stdout, level=logging.DEBUG if settings.debug else logging.INFO
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Function that handles startup and shutdown events.
    To understand more, read https://fastapi.tiangolo.com/advanced/events/
    """
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
    yield
    await SqlAlchemyUnitOfWork.dispose()


app = FastAPI(
    lifespan=lifespan,
    title=settings.project_name,
    docs_url="/api/docs",
    debug=settings.debug,
)


@app.get("/", response_model=HealthCheck, tags=["status"])
async def health_check():
    return {
        "name": settings.project_name,
    }


# Routers
app.include_router(clientes_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True, port=8000)
