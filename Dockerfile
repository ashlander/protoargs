FROM ubuntu:20.04

# update packages
RUN apt-get update

# install conan
RUN apt-get install -y python3 python3-pip
RUN pip install conan

# build tools
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y cmake git

# install rust
RUN apt-get install -y curl
RUN curl https://sh.rustup.rs -sSf | bash -s -- -y
RUN echo 'source $HOME/.cargo/env' >> $HOME/.bashrc
#RUN $HOME/.cargo/bin/rustc --version
#RUN $HOME/.cargo/bin/cargo --version

# copy tests
COPY ["entrypoint.sh", "/"]
ENTRYPOINT /entrypoint.sh
