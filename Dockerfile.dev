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

ARG HOSTNAME

WORKDIR /app

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY ./src ./src

RUN addgroup -S python && \
    adduser -S python -G python && \
    chown python:python /app && \
    mkdir /app/sockets && \
    touch /app/sockets/${HOSTNAME}.sock && \
    chown python:python /app/sockets && \
    chmod 666 /app/sockets/${HOSTNAME}.sock

#USER python

EXPOSE 8080

CMD ["uvicorn", "src.rinha.main:app", "--proxy-headers" , "--forwarded-allow-ips", "*",  "--host", "0.0.0.0", "--port", "8080", "--workers", "1", "--uds",  "/app/sockets/api1.sock"]
