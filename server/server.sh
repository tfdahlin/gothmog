#!/bin/bash

##### Functions
function usage() {
    echo "Usage: $1 [args]"
    echo "args:"
    #echo "    -s: Runs the server over HTTPS"
    echo "    --help: Displays usage help"
}

function run_waitress() {
    waitress-serve --port=8080 main:app
}

##### Main
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

if [ "$#" -ge 2 ]; then
    usage
    exit 1
fi

if [ "$#" -eq 2 ]; then
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

run_waitress
