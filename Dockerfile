FROM python:3.12.0-alpine as builder

# RUN apt-get update \
#     && apt-get install -y --no-install-recommends build-essential curl libpq-dev \
#     && apt-get clean \
#     && rm -rf /var/lib/apt/lists/* /usr/share/doc /usr/share/man

RUN pip install poetry

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN touch README.md

RUN poetry install --without dev,tests --no-root

FROM python:3.12.0-alpine as runtime

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY --from=builder ${VIRTUAL_ENV} ${VIRTUAL_ENV}

COPY ./src ./src
# Set the PYTHONPATH environment variable
#ENV PYTHONPATH="/app/src:${PYTHONPATH}"

#RUN useradd --create-home python \
#    && chown python:python -R /app

#USER python

EXPOSE 8080

CMD ["uvicorn", "src.rinha.main:app", "--host", "0.0.0.0", "--port", "8080"]
#ENTRYPOINT ["python3", "/app/src/rinha/main.py"]
#ENTRYPOINT ["tail", "-f", "/dev/null"]