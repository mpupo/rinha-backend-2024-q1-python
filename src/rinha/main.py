import logging
import sys
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from src.rinha.api.models.healthcheck import HealthCheck
from src.rinha.api.routers.clientes import router as clientes_router
from src.rinha.config.settings import settings
from src.rinha.database.unit_of_work import engine

logging.basicConfig(
    stream=sys.stdout, level=logging.DEBUG if settings.DEBUG else logging.INFO
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Function that handles startup and shutdown events.
    To understand more, read https://fastapi.tiangolo.com/advanced/events/
    """
    yield
    await engine.dispose()


app = FastAPI(
    lifespan=lifespan,
    title=settings.PROJECT_NAME,
    debug=settings.DEBUG,
)

if settings.PROFILING:
    from fastapi.requests import Request
    from fastapi.responses import HTMLResponse
    from pyinstrument import Profiler

    @app.middleware("http")
    async def profile_request(request: Request, call_next):
        """Profile the current request

        https://pyinstrument.readthedocs.io/en/latest/guide.html#profile-a-web-request-in-fastapi
        https://blog.balthazar-rouberol.com/how-to-profile-a-fastapi-asynchronous-request
        """
        profiler = Profiler(async_mode="enabled")
        profiler.start()
        await call_next(request)
        profiler.stop()
        return HTMLResponse(profiler.output_html())


@app.get("/", response_model=HealthCheck, tags=["status"])
async def health_check():
    return {
        "name": settings.PROJECT_NAME,
    }


# Routers
app.include_router(clientes_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
