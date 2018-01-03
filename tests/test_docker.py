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

from pkg_resources import resource_filename
from superflore.docker import Docker
import unittest

class TestDocker(unittest.TestCase):
    def get_image(self):
        docker_file = resource_filename('repoman_docker', 'Dockerfile')
        dock = Docker(docker_file, 'gentoo_repoman')
        return dock

    def test_init(self):
        docker_instance = self.get_image()
        self.assertTrue(docker_instance.client)
        self.assertEqual(docker_instance.name, 'gentoo_repoman')
        self.assertEqual(docker_instance.image, None)
        self.assertEqual(docker_instance.directory_map, dict())

    def test_map_dir(self):
        docker_instance = self.get_image()
        docker_instance.map_directory('/tmp/host', '/tmp/container')
        tmp = dict()
        tmp['/tmp/host'] = dict()
        tmp['/tmp/host']['bind'] = '/tmp/container'
        tmp['/tmp/host']['mode'] = 'rw'
        self.assertEqual(docker_instance.directory_map, tmp)
        docker_instance = self.get_image()
        docker_instance.map_directory('/tmp/host')
        tmp = dict()
        tmp['/tmp/host'] = dict()
        tmp['/tmp/host']['bind'] = '/tmp/host'
        tmp['/tmp/host']['mode'] = 'rw'
        self.assertEqual(docker_instance.directory_map, tmp)

    def test_add_bash_command(self):
        docker_instance = self.get_image()
        tmp = list()
        tmp.append("echo 'hello, world!'")
        docker_instance.add_bash_command("echo 'hello, world!'")
        self.assertEqual(docker_instance.bash_cmds, tmp)
