# syntax=docker/dockerfile:1
FROM python:3.8-slim-buster


COPY requirements.txt /

RUN pip3 install -r requirements.txt

EXPOSE 8080
COPY . /app

