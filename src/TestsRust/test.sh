#!/bin/bash

# geerate files from scema via protoargs
SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
python $SCRIPTPATH/../Protoargs/bin/protoargs.py -i ${SCRIPTPATH}/../Schema/src/simple.proto -o "${SCRIPTPATH}/src" --rust || return 1
python $SCRIPTPATH/../Protoargs/bin/protoargs.py -i ${SCRIPTPATH}/../Schema/src/schema.proto -o "${SCRIPTPATH}/src" --rust || return 1
python $SCRIPTPATH/../Protoargs/bin/protoargs.py -i ${SCRIPTPATH}/../Schema/src/multy_command_copy.proto -o "${SCRIPTPATH}/src" --rust || return 1
python $SCRIPTPATH/../Protoargs/bin/protoargs.py -i ${SCRIPTPATH}/../Schema/src/multy_command_create.proto -o "${SCRIPTPATH}/src" --rust || return 1
python $SCRIPTPATH/../Protoargs/bin/protoargs.py -i ${SCRIPTPATH}/../Schema/src/multy_command.proto -o "${SCRIPTPATH}/src" --rust || return 1

cargo build || return 1 # --release
cargo test || return 1
