#!/bin/bash
function usage() {
    echo "Usage: $0 <api_url> <op_name>"
}

# Cheat to get this file's directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

if [ -z "$API_URL" ]; then
    usage
    exit 1
fi

if [ -z "$OP_NAME" ]; then
    usage
    exit 1
fi

# Run the op, and redirect output to an error file.
. $DIR/env/bin/activate && python $DIR/client/main.py $API_URL $OP_NAME >> $DIR/error.log
