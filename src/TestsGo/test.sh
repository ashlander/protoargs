#!/bin/bash

SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
cd $SCRIPTPATH

python ../Protoargs/bin/protoargs.py -i ../Schema/src/simple.proto -o ./simple_pa --go || return 1

python ../Protoargs/bin/protoargs.py -i ../Schema/src/schema.proto -o ./schema_pa --go || return 1

python ../Protoargs/bin/protoargs.py -i ../Schema/src/multy_command.proto -o ./multy_command_pa --go || return 1
python ../Protoargs/bin/protoargs.py -i ../Schema/src/multy_command_create.proto -o ./multy_command_create_pa --go || return 1
python ../Protoargs/bin/protoargs.py -i ../Schema/src/multy_command_copy.proto -o ./multy_command_copy_pa --go || return 1

go test -v || return 1

