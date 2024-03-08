FROM python:3.12.0-alpine as builder

RUN pip install poetry

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN touch README.md

RUN poetry install --without dev,tests --no-root --no-ansi --no-interaction

FROM python:3.12.0-alpine as runtime

LABEL maintainer="Murilo Pupo de Oliveira <murilo.pupo@ymail.com>"

ARG UID=1000
ARG GID=1000
ARG HOSTNAME=api1
ARG DEBUG=False
ARG UVICORN_PORT=8080
ARG FAST_API_SOCKET_PATH=/var/run/rinha

USER root

WORKDIR /app

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    RINHA_DB__DB_NAME=rinha \
    RINHA_DB__DB_USER=rinha \
    RINHA_DB__DB_PASSWORD=rinha \
    RINHA_DB__DB_HOST=db \
    RINHA_DB__DB_PORT=5432 \
    RINHA_DB__DB_POOL_SIZE=10 \
    RINHA_DB__DB_MAX_OVERFLOW=40 \
    RINHA_DB__DB_POOL_TIMEOUT=30 \
    RINHA_DEBUG="${DEBUG}" \
    RINHA_PROFILING=False \
    RINHA_ECHO_SQL="${DEBUG}" \
    RINHA_TIMEZONE=America/Sao_Paulo \
    APP_SOCKET_PATH="${FAST_API_SOCKET_PATH}" \
    APP_HOSTNAME="${HOSTNAME}" \
    APP_PORT="${UVICORN_PORT}"


COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY --chown=python:rinha ./src ./src

RUN addgroup -S rinha --gid ${GID} && \
    adduser -S python --uid ${UID} -G rinha --disabled-password && \
    mkdir ${APP_SOCKET_PATH} && \
    chown python:rinha ${APP_SOCKET_PATH} && \
    chown python:rinha . -R

VOLUME ${APP_SOCKET_PATH}

USER python

EXPOSE ${UVICORN_PORT}

HEALTHCHECK  --interval=2s --timeout=5s --retries=30 --start-period=10s CMD test -S ${APP_SOCKET_PATH}/${APP_HOSTNAME}.sock || exit 1

CMD uvicorn "src.rinha.main:app" --proxy-headers --forwarded-allow-ips "*" --host "0.0.0.0" --port "${APP_PORT}" --workers "1" --uds "${APP_SOCKET_PATH}/${APP_HOSTNAME}.sock"
