#!/bin/sh

SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

# build docker image
#docker build --no-cache -t protoargs:latest .
docker build -t protoargs:latest .
