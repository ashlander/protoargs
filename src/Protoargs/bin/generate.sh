#!/bin/bash

SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
python $SCRIPTPATH/protoargs.py -i protoargs.proto -o "${SCRIPTPATH}" --py
