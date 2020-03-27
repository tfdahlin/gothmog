#!/bin/bash
function usage() {
    echo "Usage: $0 <api_url> <op_name>"
}

# Cheat to get this file's directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
SHOULD_EXIT=0


if [ -z "$API_URL" ]; then
    echo "API_URL environment variable not set."
    SHOULD_EXIT=1
fi

if [ -z "$OP_NAME" ]; then
    echo "OP_NAME environment variable not set."
    SHOULD_EXIT=1
fi

if [ $SHOULD_EXIT == 1 ]; then
    exit 1
fi

# Run the op, and redirect output to an error file.
. $DIR/env/bin/activate && python $DIR/main.py $API_URL $OP_NAME >> $DIR/error.log
