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
RUN touch /app/server/error.log
RUN touch /app/server/app.log
RUN mkdir /app/downloads
WORKDIR /app/server

# No need to run this as root.
RUN addgroup -S gothmog-server && adduser -S -G gothmog-server gothmog-server
RUN chown -R gothmog-server:gothmog-server /app
USER gothmog-server

# Copy necessary files.
COPY ./apps /app/server/apps
COPY ./config.py /app/server/config.py
COPY ./main.py /app/server/main.py
COPY ./models.py /app/server/models.py
COPY ./requirements.txt /app/server/requirements.txt
COPY ./routes.py /app/server/routes.py
COPY ./server.sh /app/server/server.sh
COPY ./setup.sh /app/server/setup.sh
COPY ./tests /app/server/tests
COPY ./util.py /app/server/util.py

# Run setup within the container.
RUN /app/server/setup.sh

# Run the app.
CMD ["/app/server/server.sh"]
