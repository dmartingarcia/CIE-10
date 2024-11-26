ARG PYTHON_VERSION=3.13

###################################### BASE IMAGE
FROM python:${PYTHON_VERSION}-alpine AS base-image

WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt
