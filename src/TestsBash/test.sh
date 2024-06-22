#!/bin/bash

# find python binary
python=$(which python)
if [ -z "$python" ]; then
    python=$(which python3)
fi
if [ -z "$python" ]; then
    python=$(which python2)
fi

# geerate files from scema via protoargs
SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
$python $SCRIPTPATH/../Protoargs/bin/protoargs.py -i ${SCRIPTPATH}/../Schema/src/simple.proto -o "${SCRIPTPATH}/src" --bash || exit 1
$python $SCRIPTPATH/../Protoargs/bin/protoargs.py -i ${SCRIPTPATH}/../Schema/src/bools.proto -o "${SCRIPTPATH}/src" --bash || exit 1
$python $SCRIPTPATH/../Protoargs/bin/protoargs.py -i ${SCRIPTPATH}/../Schema/src/schema.proto -o "${SCRIPTPATH}/src" --bash || exit 1
$python $SCRIPTPATH/../Protoargs/bin/protoargs.py -i ${SCRIPTPATH}/../Schema/src/multy_command_copy.proto -o "${SCRIPTPATH}/src" --bash || exit 1
$python $SCRIPTPATH/../Protoargs/bin/protoargs.py -i ${SCRIPTPATH}/../Schema/src/multy_command_create.proto -o "${SCRIPTPATH}/src" --bash || exit 1
$python $SCRIPTPATH/../Protoargs/bin/protoargs.py -i ${SCRIPTPATH}/../Schema/src/multy_command.proto -o "${SCRIPTPATH}/src" --bash || exit 1

# find bash binary
bash=$(which bash)

# testing
$bash $SCRIPTPATH/src/test_simple.sh || exit 1
$bash $SCRIPTPATH/src/test_schema.sh || exit 1
$bash $SCRIPTPATH/src/test_bools.sh || exit 1
