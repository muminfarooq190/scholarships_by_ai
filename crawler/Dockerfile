FROM python:3.12-slim as runtime

ENV PYTHONUNBUFFERED=1 \
    POETRY_VERSION=1.8.2 \
    POETRY_VIRTUALENVS_CREATE=false

WORKDIR /app
RUN pip install --no-cache-dir debugpy
RUN pip install --no-cache-dir poetry==$POETRY_VERSION

# copy just deps first
COPY ingest/pyproject.toml ./
RUN poetry lock --no-update && poetry install --no-root --no-interaction

# copy source
COPY ingest ./ingest

ENTRYPOINT ["python", "-u", "ingest/main.py"]
