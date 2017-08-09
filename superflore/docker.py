# Copyright 2017 Open Source Robotics Foundation, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import subprocess


class Docker(object):
    def __init__(self, dockerfile_directory, name):
        self.dockerfile_directory = dockerfile_directory
        self.name = name
        self.directory_map = dict()
        self.bash_cmds = list()

    def map_directory(self, host, container=None):
        if container:
            self.directory_map[host] = container
        else:
            self.directory_map[host] = host

    def add_bash_command(self, cmd):
        self.bash_cmds.append(cmd)

    def build(self):
        try:
            subprocess.run([
                'docker',
                'build',
                '-t',
                self.name,
                self.dockerfile_directory
            ])
        except subprocess.CalledProcessError:
            raise BuildException('failed to build docker image')

    def run(self, rm=True, show_cmd=False):
        cmd = ['docker', 'run', '-ti']
        if rm:
            cmd.append('--rm')
        for host_dir in self.directory_map:
            cmd.append('-v')
            cmd.append('{}:{}'.format(host_dir, self.directory_map[host_dir]))
        cmd.append(self.name)
        cmd.append('bash')
        cmd.append('-c')
        cmd_string = str()
        for i, bash_cmd in enumerate(self.bash_cmds):
            cmd_string += bash_cmd
            if i != len(self.bash_cmds) - 1:
                cmd_string += ' && '
        cmd.append(cmd_string)
        if show_cmd:
            print(cmd)
        try:
            subprocess.run(cmd)
        except subprocess.CalledProcessError:
            raise RunException('failed to run docker image')


class BuildException(Exception):
    def __init__(self, message):
        self.message = message


class RunException(Exception):
    def __init__(self, message):
        self.message = message
