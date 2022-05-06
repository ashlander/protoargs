#!/bin/bash

#/***************************************************************************\
#* C++ build and conan package creation
#\***************************************************************************/

# build protoargs helper
cd /opt && git clone https://github.com/ashlander/protoargs.git || return 1
cd /opt/protoargs && mkdir release && cd release && conan install -s build_type=Release ../. || return 1
cd /opt/protoargs/release && conan build ../. || return 1
cd /opt/protoargs/release && conan export-pkg ../. protoargs/0.1.0@ashlander/testing || return 1

# run c++ google tests
/opt/protoargs/release/bin/tests || return 1

/***************************************************************************\
* Rust build and run tests
\***************************************************************************/

cd /opt/protoargs/src/TestsRust
./test.sh || return 1
