import logging
import sys

import uvicorn
from fastapi import FastAPI

from src.rinha.api.models.healthcheck import HealthCheck
from src.rinha.api.routers.clientes import router as clientes_router
from src.rinha.config.settings import settings

logging.basicConfig(
    stream=sys.stdout, level=logging.DEBUG if settings.debug_logs else logging.INFO
)

app = FastAPI(
    title=settings.project_name, docs_url="/api/docs", debug=settings.debug_logs
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
