FROM ubuntu:16.04

RUN apt-get update -y && \
    apt-get install -y python-pip python-dev
COPY ./requirements.txt /usr/src/car/requirements.txt
WORKDIR /usr/src/car
RUN pip install -r requirements.txt