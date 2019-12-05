#!/bin/bash

##### Functions
function usage() {
    echo "Usage: $1 [args]"
    echo "args:"
    echo "    -s: Runs the server over HTTPS"
    echo "    --help: Displays usage help"
}

##### Main
if [ "$#" -ge 2 ]; then
    usage
    exit 1
fi

if [ "$1" == "--help" ]; then
    usage
    exit 0
fi

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

if [ "$1" == "-s" ]; then
    gunicorn --certfile=./crypto/server.crt --keyfile=./crypto/server.key --bind 0.0.0.0:443 --chdir $DIR main:app
else
    gunicorn --bind 0.0.0.0:8080 --chdir $DIR main:app
fi

