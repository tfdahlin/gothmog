from alpine:latest

LABEL maintainer='tdahlin@2u.com'

# Installations
RUN apk add --no-cache \
    python3 \
    python3-dev \
    git \
    bash
    #echo

# Application folders.
RUN mkdir /app
RUN mkdir /app/client
RUN touch /app/client/error.log
RUN touch /app/client/app.log
RUN mkdir /app/downloads
WORKDIR /app/client

# No need to run this as root.
RUN addgroup -S gothmog-client && adduser -S -G gothmog-client gothmog-client
RUN chown -R gothmog-client:gothmog-client /app
USER gothmog-client

# Copy necessary files.
COPY ./main.py /app/client/main.py
COPY ./requirements.txt /app/client/requirements.txt
COPY ./setup.sh /app/client/setup.sh
COPY ./start.sh /app/client/start.sh

# Defaults to default_op and server api on host machine
ARG API_URL=http://host.docker.internal:8080
ARG OP_NAME=default_op
ENV API_URL $API_URL
ENV OP_NAME $OP_NAME

# Run setup within the container.
RUN /app/client/setup.sh

# Run the app.
CMD ["/app/client/start.sh"]