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

from getpass import getpass
import os
import sys

import docker
from superflore.TempfileManager import TempfileManager
from superflore.utils import err
from superflore.utils import info
from superflore.utils import ok


class Docker(object):
    def __init__(self):
        self.client = docker.from_env()
        self.image = None
        self.directory_map = dict()
        self.bash_cmds = list()

    def map_directory(self, host, container=None, mode='rw'):
        self.directory_map[host] = dict()
        self.directory_map[host]['bind'] = container or host
        self.directory_map[host]['mode'] = mode

    def add_bash_command(self, cmd):
        self.bash_cmds.append(cmd)

    def clear_commands(self):
        self.bash_cmds = list()

    def build(self, dockerfile):
        dockerfile_directory = os.path.dirname(dockerfile)
        if not (os.path.isdir(dockerfile_directory) and
                os.path.isfile('%s/Dockerfile' % dockerfile_directory)):
            raise NoDockerfileSupplied(
                'You must supply the location of the Dockerfile.'
            )
        self.image = self.client.images.build(path=dockerfile_directory)

    def login(self):
        # TODO(allenh1): add OAuth here, and fall back on user input
        # if the OAuth doesn't exist (however one finds that).
        if not ('DOCKER_USERNAME' in os.environ and
                'DOCKER_PASSWORD' in os.environ):
            if os.isatty(sys.stdin.fileno()):
                user = getpass('Docker username:')
                pswd = getpass('Docker password:')
            else:
                raise RuntimeError(
                    "Please set 'DOCKER_USERNAME' and 'DOCKER_PASSWORD'" +
                    " when not in interactive mode."
                )
        else:
            user = os.environ['DOCKER_USERNAME']
            pswd = os.environ['DOCKER_PASSWORD']
        self.client.login(user, pswd)

    def pull(self, org, repo, tag='latest'):
        self.image = self.client.images.pull('%s/%s:%s' % (org, repo, tag))

    def get_log(self):
        return self.log

    def get_command(self, logging_dir=None, logging_file=None):
        if logging_dir:
            cmd = "bash -c '"
            cmd += (
                " &>> %s/%s && " % (
                    logging_dir, logging_file
                )
            ).join(self.bash_cmds)
            cmd += (" &>> %s/%s'" % (logging_dir, logging_file))
        else:
            cmd = "bash -c '" + " && ".join(self.bash_cmds) + "'"
        return cmd

    def run(self, rm=True, show_cmd=False, privileged=False, log_file=None):
        if log_file:
            # get the location to store the log
            log_path = os.path.dirname(log_file)
            # get the file name
            log_name = log_file.replace(log_path, '').lstrip('/')
        else:
            log_path = None
            log_name = 'log.txt'
        with TempfileManager(log_path) as tmp:
            if log_file:
                # change access to the directory so docker can read it
                os.chmod(tmp, 17407)
            # map into the container
            self.map_directory(tmp)
            cmd_string = self.get_command(tmp, log_name)
            if show_cmd:
                msg = "Running container with command string '%s'..."
                info(msg % cmd_string)
            try:
                self.client.containers.run(
                    image=self.image,
                    remove=rm,
                    command=cmd_string,
                    privileged=privileged,
                    volumes=self.directory_map,
                )
                ok("Docker container exited.")
                if log_file:
                    info("Log file: '%s/%s'" % (tmp, log_name))
            except docker.errors.ContainerError:
                err("Docker container exited with errors.")
                if log_file:
                    info("Log file: '%s/%s'" % (tmp, log_name))
                # save log, then raise.
                with open('%s/%s' % (tmp, log_name), 'r') as logfile:
                    self.log = logfile.read()
                raise
            with open('%s/%s' % (tmp, log_name), 'r') as logfile:
                self.log = logfile.read()


class NoDockerfileSupplied(Exception):
    def __init__(self, message):
        self.message = message
