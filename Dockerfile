FROM ubuntu:14.04

MAINTAINER Dmitry Zhiltsov <dzhiltsov@me.com>

RUN apt-get update && \
    apt-get install -y \
    build-essential \
    python3-pycurl \
    cmake \
    git \
    wget \
    python3-pip \
    unzip \
    pkg-config \
    libswscale-dev \
    python3-dev \
    python3-numpy \
    libtbb2 \
    libtbb-dev \
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libjasper-dev \
    libavformat-dev \
    && apt-get -y clean all \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /
RUN wget https://github.com/Itseez/opencv/archive/3.0.0.zip \
    && unzip 3.0.0.zip \
    && mkdir /opencv-3.0.0/cmake_binary \
    && cd /opencv-3.0.0/cmake_binary \
    && cmake .. \
    && make install \
    && rm /3.0.0.zip \
    && rm -r /opencv-3.0.0

COPY . /var/imwor
WORKDIR /var/imwor

RUN pip3 install tornado
RUN pip3 install Pillow
