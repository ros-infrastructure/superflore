#!/bin/bash

set -x

# export ROS_HOME=${HOME}
if [ -z "$ROS_HOME" ]; then
    echo "ROS_HOME is not set"
    exit 1
fi

# export ROSDEP_SOURCE_PATH=${ROS_HOME}/rosdep
if [ -z "$ROSDEP_SOURCE_PATH" ]; then
    echo "ROSDEP_SOURCE_PATH is not set"
    exit 1
fi
mkdir -p ${ROSDEP_SOURCE_PATH}

PROJECT_DIR=$PWD

python3 -m venv $HOME/superflore_venv
source $HOME/superflore_venv/bin/activate
python3 -m pip install .

echo "Running rosdep init"
rosdep init

echo "Running rosdep update"
rosdep update

cd ${PROJECT_DIR}
ROSDISTRO_GIT="https://github.com/ros/rosdistro"
git clone ${ROSDISTRO_GIT} ${HOME}/rosdistro

ROSDISTRO_URL="https://raw.githubusercontent.com/ros/rosdistro/master/rosdep"
sed -i -e "s|${ROSDISTRO_URL}|file://${HOME}/rosdistro/rosdep|" ${ROSDEP_SOURCE_PATH}/20-default.list