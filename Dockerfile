FROM ubuntu:20.04

# update packages
RUN apt-get update

# install conan
RUN apt-get install -y python3 python3-pip
RUN pip install conan

# build tools
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y cmake git

# copy tests
COPY ["entrypoint.sh", "/"]
ENTRYPOINT /entrypoint.sh
