#!/bin/bash
function usage() {
    echo "Usage: $1 <api_url> <op_name>"
}

# Cheat to get this file's directory
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Run the op, and redirect output to an error file.
# Simultaneously, tail the app log, and the error file to stdout
(. $DIR/env/bin/activate && python $DIR/main.py $API_URL $OP_NAME >> $DIR/error.log) & (tail -f $DIR/app.log >&1) & (tail -f $DIR/error.log >&1)
