FROM maven:3.5-jdk-8-alpine

COPY ./autosuggest /usr/src/autosuggest/

WORKDIR /usr/src/autosuggest
RUN mvn install
