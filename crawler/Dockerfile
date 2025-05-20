FROM python:3.12-slim as runtime

ENV PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.2 \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /crawler
RUN pip install --no-cache-dir debugpy
RUN pip install --no-cache-dir poetry==$POETRY_VERSION

COPY ingest ./ingest

WORKDIR /crawler/ingest
RUN poetry lock --no-update && poetry install --no-root --no-interaction

WORKDIR /
ENTRYPOINT ["python", "-Xfrozen_modules=off", "-m", "debugpy", "--listen", "0.0.0.0:5678", "--wait-for-client", "crawler/ingest/main.py"]
