FROM postgres:15-alpine

ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=password
ENV POSTGRES_DB=innoevent

COPY init.sql /docker-entrypoint-initdb.d/

EXPOSE 5432
