from alpine:latest

LABEL maintainer='tfdahlin@gmail.com'

# Installations
RUN apk add --no-cache \
    python3 \
    python3-dev \
    git \
    bash

# Application folders.
RUN mkdir /app
RUN mkdir /app/server
RUN mkdir /app/server/server
RUN touch /app/server/error.log
RUN touch /app/server/app.log
RUN mkdir /app/server/downloads
WORKDIR /app/server

# Copy necessary files.
# Python source files
COPY ./server/apps /app/server/server/apps
COPY ./server/config.py /app/server/server/config.py
COPY ./server/main.py /app/server/server/main.py
COPY ./server/models.py /app/server/server/models.py
COPY ./server/routes.py /app/server/server/routes.py
COPY ./server/util.py /app/server/server/util.py
COPY ./server/tests /app/server/server/tests

# Additional files
COPY ./requirements.txt /app/server/requirements.txt
COPY ./server.sh /app/server/server.sh
COPY ./setup.sh /app/server/setup.sh

# No need to run this as root.
RUN addgroup -S gothmog-server && adduser -S -G gothmog-server gothmog-server
RUN chown -R gothmog-server:gothmog-server /app
USER gothmog-server

# Run setup within the container.
RUN /app/server/setup.sh

# Run the app.
CMD ["/app/server/server.sh"]
