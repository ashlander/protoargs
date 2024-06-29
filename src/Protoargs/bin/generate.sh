#!/bin/bash

# find python binary
python=$(which python)
if [ -z "$python" ]; then
    python=$(which python3)
fi
if [ -z "$python" ]; then
    python=$(which python2)
fi

SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
$python $SCRIPTPATH/protoargs.py -i protoargs.proto -o "${SCRIPTPATH}" --py
