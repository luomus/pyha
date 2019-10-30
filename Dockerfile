FROM python:3.5

# Copy the instant client rpms to the server
COPY oracle/*.rpm /tmp/

# Install dependensies
RUN apt-get update \
    && apt-get -y install unzip alien libaio-dev iputils-ping sudo \
    && alien -i /tmp/*.rpm

WORKDIR /usr/src/app

# Setup the build environment
ENV ORACLE_HOME=/usr/lib/oracle/12.2/client64
ENV PATH=$PATH:$ORACLE_HOME/bin
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$ORACLE_HOME/lib

# Install the application dependencies
COPY Requirements.txt ./
COPY docker-entrypoint.sh ./
RUN pip install --no-cache-dir -r Requirements.txt

# Copy the application to the server
COPY project .

# Define script that is run on startup
ENTRYPOINT ["./docker-entrypoint.sh"]
CMD python manage.py runserver 0.0.0.0:8000