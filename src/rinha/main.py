import logging
import sys
from contextlib import asynccontextmanager

import uvicorn
from src.rinha.api.routers.clientes import router as clientes_router
from src.rinha.config.settings import settings
from src.rinha.database.orm.session import sessionmanager
from fastapi import FastAPI

from src.rinha.api.models.healthcheck import HealthCheck

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG if settings.debug_logs else logging.INFO)


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     """
#     Function that handles startup and shutdown events.
#     To understand more, read https://fastapi.tiangolo.com/advanced/events/
#     """
#     yield
#     if sessionmanager._engine is not None:
#         # Close the DB connection
#         await sessionmanager.close()


# app = FastAPI(lifespan=lifespan, title=settings.project_name, docs_url="/api/docs", debug=settings.debug_logs)
app = FastAPI(title=settings.project_name, docs_url="/api/docs", debug=settings.debug_logs)


@app.get("/", response_model=HealthCheck, tags=["status"])
async def health_check():
    return {
        "name": settings.project_name,
    }


# Routers
app.include_router(clientes_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True, port=8000)
