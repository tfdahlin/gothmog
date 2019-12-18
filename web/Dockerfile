from alpine:latest

LABEL maintainer='tfdahlin@gmail.com'

# Installations
RUN apk add --no-cache \
    curl \
    git \
    bash \
    nodejs \
    npm

# Application folders.
RUN mkdir /app
RUN mkdir /app/web
RUN touch /app/web/error.log
RUN touch /app/web/app.log
WORKDIR /app/web

# No need to run this as root.
RUN addgroup -S gothmog-web && adduser -S -G gothmog-web gothmog-web
RUN chown -R gothmog-web:gothmog-web /app
USER gothmog-web

# Copy necessary files.
COPY ./app.js /app/web/app.js
COPY ./package.json /app/web/package.json
COPY ./res /app/web/res
COPY ./settings.js /app/web/settings.js
COPY ./templates /app/web/templates

RUN sed -i "s/'webPort': .*,/'webPort': 8080,/g" /app/web/settings.js

# Install necessary libraries
RUN npm install

# Run the app.
CMD ["node app.js"]
