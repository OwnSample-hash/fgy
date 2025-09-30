#!/bin/bash

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 
   exit 1
fi

apt-get update -y
apt-get install -y \
  build-essential \
  git \
  cmake \
  libssl-dev \
  zsh \
  libboost-all-dev \
  redis \
  mariadb-server \
  libargon2-dev \
  libargon2-1 \
  gdb \
  gpg-agent \
  ninja-build \
  qt6-base-dev \
  librange-v3-dev \
  ccache \
  inetutils-ping