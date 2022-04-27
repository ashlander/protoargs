#!/bin/bash

#/***************************************************************************\
#* C++ build and conan package creation
#\***************************************************************************/

# build protoargs helper
cd /opt && git clone https://github.com/ashlander/protoargs.git
cd /opt/protoargs && mkdir release && cd release && conan install -s build_type=Release ../.
cd /opt/protoargs/release && conan build ../.
cd /opt/protoargs/release && conan export-pkg ../. protoargs/0.1.0@ashlander/testing

# run c++ google tests
/opt/protoargs/release/bin/tests
