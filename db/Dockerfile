FROM mysql:5.7

RUN apt-get update -y && \
    apt-get install -y locales vim && \
    echo "ja_JP.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen && \
    update-locale LANG=ja_JP.UTF-8

# docker-compose.ymlのvolumesでマウントすると権限がなくて実行出来ないため
COPY ./sql /docker-entrypoint-initdb.d/
RUN chmod -R 777 /docker-entrypoint-initdb.d/

ENV LANG="ja_JP.UTF-8" \
    TZ="Asia/Tokyo" \
    MYSQL_ROOT_PASSWORD="password" \
    MYSQL_USER="minael" \
    MYSQL_PASSWORD="password" \
    MYSQL_DATABASE="minique_docker" \
    MYSQL_ALLOW_EMPTY_PASSWORD="yes"

# CMD ["mysqld", "--character-set-server=utf8", "--collation-server=utf8_unicode_ci"]
