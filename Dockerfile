FROM python:3.6

ARG ENABLE_DEBUG
ARG EMAIL_ERROR_RATE_LIMIT
ARG EMAIL_ERROR_RATE_KEY_LIMIT
ARG ADMIN_NAME
ARG ADMIN_EMAIL
ARG SERVER_EMAIL
ARG DJANGO_SECRET_KEY
ARG PYHA_LISTEN_PORT
ARG PYHA_URL
ARG LAJI_AUTH_URL
ARG LAJI_ETL_FILE_DOWNLOAD_URL
ARG TRIPLESTORE_URL
ARG TRIPLESTORE_USER
ARG TRIPLESTORE_PASSWORD
ARG PDF_API_URL
ARG PDF_API_USER
ARG PDF_API_PASSWORD
ARG APILAJIFI_URL
ARG APILAJIFI_TOKEN
ARG LAJI_AUTH_TARGET
ARG PYHA_API_USER
ARG PYHA_API_PASSWORD
ARG OBSERVATION_LINK_PREFIX
ARG OFFICIAL_OBSERVATION_LINK_PREFIX
ARG DB_NAME
ARG DB_USER
ARG DB_PASSWORD
ARG SKIP_OFFICIAL
ARG DB_ENGINE
ARG DOMAIN_PATH_PREFIX
ARG ZABBIX_STATUS_SUB_DIR
ARG ADMIN_SUB_DIR
ARG STATIC_URL

COPY oracle/*.rpm /tmp/

RUN apt-get update \
    && apt-get -y install unzip alien libaio-dev iputils-ping sudo \
    && alien -i /tmp/*.rpm

WORKDIR /usr/src/app
ENV ORACLE_HOME=/usr/lib/oracle/12.2/client64
ENV PATH=$PATH:$ORACLE_HOME/bin
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$ORACLE_HOME/lib
ENV ENABLE_DEBUG=$ENABLE_DEBUG \
    EMAIL_ERROR_RATE_LIMIT=$EMAIL_ERROR_RATE_LIMIT \
    EMAIL_ERROR_RATE_KEY_LIMIT=$EMAIL_ERROR_RATE_KEY_LIMIT \
    ADMIN_NAME=$ADMIN_NAME \
    ADMIN_EMAIL=$ADMIN_EMAIL \
    SERVER_EMAIL=$SERVER_EMAIL \
    DJANGO_SECRET_KEY=$DJANGO_SECRET_KEY \
    PYHA_LISTEN_PORT=$PYHA_LISTEN_PORT \
    PYHA_URL=$PYHA_URL \
    LAJI_AUTH_URL=$LAJI_AUTH_URL \
    LAJI_ETL_FILE_DOWNLOAD_URL=$LAJI_ETL_FILE_DOWNLOAD_URL \
    TRIPLESTORE_URL=$TRIPLESTORE_URL \
    TRIPLESTORE_USER=$TRIPLESTORE_USER \
    TRIPLESTORE_PASSWORD=$TRIPLESTORE_PASSWORD \
    PDF_API_URL=$PDF_API_URL \
    PDF_API_USER=$PDF_API_USER \
    PDF_API_PASSWORD=$PDF_API_PASSWORD \
    APILAJIFI_URL=$APILAJIFI_URL \
    APILAJIFI_TOKEN=$APILAJIFI_TOKEN \
    LAJI_AUTH_TARGET=$LAJI_AUTH_TARGET \
    PYHA_API_USER=$PYHA_API_USER \
    PYHA_API_PASSWORD=$PYHA_API_PASSWORD \
    OBSERVATION_LINK_PREFIX=$OBSERVATION_LINK_PREFIX \
    OFFICIAL_OBSERVATION_LINK_PREFIX=$OFFICIAL_OBSERVATION_LINK_PREFIX \
    DB_NAME=$DB_NAME \
    DB_USER=$DB_USER \
    DB_PASSWORD=$DB_PASSWORD \
    SKIP_OFFICIAL=$SKIP_OFFICIAL \
    DB_ENGINE=$DB_ENGINE \
    DOMAIN_PATH_PREFIX=$DOMAIN_PATH_PREFIX \
    ZABBIX_STATUS_SUB_DIR=$ZABBIX_STATUS_SUB_DIR \
    ADMIN_SUB_DIR=$ADMIN_SUB_DIR \
    STATIC_URL=$STATIC_URL

COPY Requirements.txt ./
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r Requirements.txt

COPY . .

RUN echo $LD_LIBRARY_PATH \
    && echo $ORACLE_HOME

RUN python project/manage.py collectstatic \
    && python project/manage.py makemigrations \
    && python project/manage.py migrate \
    && python project/manage.py createcachetable \
    && python project/manage.py makemessages -a \
    && python project/manage.py compilemessages

CMD python project/manage.py runserver 0.0.0.0:8000