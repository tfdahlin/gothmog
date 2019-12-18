#!/bin/bash

##### Functions
function usage() {
    echo "Usage: $0 [args]"
    echo ""
    echo "Args:"
    #echo "    -s: Runs the server over HTTPS"
    echo "    -h, --help: Displays usage help"
    echo "    -p <port>, --port <port>: Port to run on"
}

function run_waitress() {
    waitress-serve --port=$1 main:app
}

##### Main
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

if [ "$#" -eq 0 ]; then
    run_waitress 8080
    exit 0
fi

if [ "$#" -eq 1 ]; then
    if [ "$1" == "--help" ]; then
        usage
        exit 0
    elif [ "$1" == "-h" ]; then
        usage
        exit 0
    else
        usage
        exit 1
    fi
fi

if [ "$#" -eq 2 ]; then
    if [ "$1" == "-p" ]; then
        run_waitress $2
        exit 0
    elif [ "$1" == "--port" ]; then
        run_waitress $2
        exit 0
    else
        usage
        exit 1
    fi
fi

usage
