# Stage 1: requirements-stage
FROM python:3.10-slim-bullseye as requirements-stage

WORKDIR /tmp

# Устанавливаем Poetry
RUN pip install poetry

# Копируем файл зависимостей Poetry
COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes --with dev

FROM python:3.10-slim-bullseye as production-stage

RUN apt-get update && apt-get -y install libpq-dev gcc g++ curl procps net-tools tini

ENV PYTHONFAULTHANDLER=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY --from=requirements-stage /tmp/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY . /app/

EXPOSE 8000