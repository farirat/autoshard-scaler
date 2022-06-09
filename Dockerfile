FROM python:3.10-slim-bullseye as base
LABEL org.opencontainers.image.authors="fourat@gmail.com"

ENV BOT_TOKEN="<DISCORD BOT TOKEN>"
ENV K8S_NAMESPACE="K8S namespace where to find the statefulset"
ENV K8S_STATEFULSET="K8S statefulset name"
ENV K8S_CONTAINER="K8S bot container name"
ENV K8S_SHARDS_PER_BOT=3
ENV K8S_SCALEUP=1
ENV K8S_SCALEDOWN=1

WORKDIR /app
COPY . /app

ENV PIP_DISABLE_PIP_VERSION_CHECK=1
RUN pip install poetry==1.1.13
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction

CMD python autoshard_scaler/main.py
