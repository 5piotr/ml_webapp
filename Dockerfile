FROM python:3.11-bookworm

RUN apt-get -y update

WORKDIR /code

COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
