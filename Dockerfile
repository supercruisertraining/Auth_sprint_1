FROM python:3.10

WORKDIR /app
COPY ./alembic.ini /app
COPY ./waiters /app/waiters
COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r /app/requirements.txt

COPY ./tests /app/tests/
COPY ./src /app/src/