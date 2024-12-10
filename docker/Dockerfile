# superflore-devel
# Copyright (C) 2024 Wind River Systems, Inc.
#
# SPDX-License-Identifier: MIT
#

FROM osrf/ros2:devel

ENV ROS_HOME="/home/ubuntu"
ENV ROSDEP_SOURCE_PATH="/home/ubuntu/rosdep"
ENV ROS_DISTRO="rolling"
ENV ROSDISTRO_URL="https://raw.githubusercontent.com/ros/rosdistro/master/rosdep"
ENV GIT_FULLNAME="Firstname Lastname"
ENV GIT_EMAIL="firstname.lastname@example.com"

RUN apt-get update && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y \
        apt-utils \
        curl \
        locales \
        python3 \
        python3-pip \
        python3.12-venv \
        python3-virtualenv \
        vim \
        wget && \
    apt-get clean && \
    locale-gen en_US en_US.UTF-8 && \
    update-locale LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8 && \
    echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

USER ubuntu
WORKDIR /home/ubuntu

RUN git config --global user.email "${GIT_EMAIL}" && \
    git config --global user.name "${GIT_FULLNAME}"

CMD ["/bin/bash"]
