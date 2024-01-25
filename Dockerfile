FROM python:3.10-slim

SHELL ["/bin/bash", "-c"]

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1  

RUN pip install --upgrade pip  

WORKDIR /cafe_app

RUN mkdir -p /cafe_app

COPY . /cafe_app

RUN pip install -r requirements.txt
