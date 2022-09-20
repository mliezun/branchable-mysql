FROM ubuntu:22.04

ARG DEBIAN_FRONTEND=noninteractive

WORKDIR /app

RUN apt-get update -yyqq && \
    apt-get install -yyqq mysql-server python3 python3-pip fuse-overlayfs curl strace && \
    mkdir -p layers/base/conf && \
    mkdir -p layers/base/data && \
    mkdir -p layers/base/logs && \
    mkdir -p layers/base/var/lib/mysql-files && \
    chown -R mysql:mysql layers/base

COPY my.cnf layers/base/conf/
RUN mysqld \
    --initialize-insecure \
    --datadir=/app/layers/base/data/ \
    --pid-file=/app/layers/base/var/mysqld.pid \
    --socket=/app/layers/base/var/mysqld.sock \
    --secure-file-priv=/app/layers/base/var/lib/mysql-files \
    --port=33061 \
    --log-error=/app/layers/base/logs/error.log \
    --log-bin=/app/layers/base/var/mysql-bin.log \
    --slow-query-log-file=/app/layers/base/logs/slow_query.log \
    --general-log-file=/app/layers/base/logs/query.log \
    --user=mysql \
    --bind-address=127.0.0.1 || true

COPY scripts scripts

COPY web/requirements.txt web/requirements.txt
RUN pip install -r web/requirements.txt

COPY web/main.py web/main.py


ENTRYPOINT [ "./scripts/entrypoint.sh" ]
