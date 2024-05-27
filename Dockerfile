FROM python:3.12.3-slim-bookworm

WORKDIR /app

COPY requirements.txt /app/

RUN pip install -r /app/requirements.txt