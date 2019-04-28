# Copyright 2018 Open Source Robotics Foundation, Inc.
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

from superflore.docker import Docker
from superflore.docker import NoDockerfileSupplied
import unittest

class TestDocker(unittest.TestCase):
    def test_init(self):
        """Test Docker __init__"""
        docker_instance = Docker()
        self.assertTrue(docker_instance.client)
        self.assertEqual(docker_instance.image, None)
        self.assertEqual(docker_instance.directory_map, dict())

    def test_map_dir(self):
        """Test Docker mount directory map"""
        docker_instance = Docker()
        docker_instance.map_directory('/tmp/host', '/tmp/container')
        tmp = dict()
        tmp['/tmp/host'] = dict()
        tmp['/tmp/host']['bind'] = '/tmp/container'
        tmp['/tmp/host']['mode'] = 'rw'
        self.assertEqual(docker_instance.directory_map, tmp)
        docker_instance = Docker()
        docker_instance.map_directory('/tmp/host')
        tmp = dict()
        tmp['/tmp/host'] = dict()
        tmp['/tmp/host']['bind'] = '/tmp/host'
        tmp['/tmp/host']['mode'] = 'rw'
        self.assertEqual(docker_instance.directory_map, tmp)

    def test_add_bash_command(self):
        """Test Docker add bash command"""
        docker_instance = Docker()
        tmp = list()
        tmp.append("echo 'hello, world!'")
        docker_instance.add_bash_command("echo 'hello, world!'")
        self.assertEqual(docker_instance.bash_cmds, tmp)

    def test_build(self):
        """Test Docker build"""
        docker_instance = Docker()
        with self.assertRaises(NoDockerfileSupplied):
            docker_instance.build('Dockerfile')
        docker_instance.build('tests/docker/Dockerfile')

    def test_run(self):
        """Test Docker run"""
        docker_instance = Docker()
        docker_instance.build('tests/docker/Dockerfile')
        docker_instance.add_bash_command("echo Hello, docker")
        docker_instance.run()

    def test_pull(self):
        """Test Docker pull"""
        docker_instance = Docker()
        docker_instance.pull('allenh1', 'ros_gentoo_base')
        docker_instance.add_bash_command("echo Hello, Gentoo")
        docker_instance.run()

    def test_get_command(self):
        """Test the get_command function"""
        docker_instance = Docker()
        docker_instance.add_bash_command("echo Hello, docker")
        docker_instance.add_bash_command("echo command two.")
        # get command string
        ret = docker_instance.get_command()
        self.assertEqual(ret, "bash -c 'echo Hello, docker && echo command two.'")
        # get command string with logging directory.
        ret = docker_instance.get_command('/root', 'log.txt')
        expected = "bash -c 'echo Hello, docker &>> /root/log.txt "\
                   "&& echo command two. &>> /root/log.txt'"
        self.assertEqual(expected, ret)

    def test_logger_output(self):
        """Test the log file output"""
        docker_instance = Docker()
        docker_instance.pull('gentoo', 'stage3-amd64')
        docker_instance.add_bash_command("echo Log Text!")
        docker_instance.run()
        self.assertEqual(docker_instance.log, "Log Text!\n")
