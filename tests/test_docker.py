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

from time import gmtime, strftime
import re

from superflore.docker import docker
class TestDocker(unittest.TestCase):
    def get_image(self):
        docker_file = resource_filename('repoman_docker', 'Dockerfile')
        dock = Docker(docker_file, 'gentoo_repoman')
        return dock

    def test_init(self):
        docker_instance = get_image()
        self.assertTrue(docker_instance.client)
        self.assertEqual(docker_instance.name, 'gentoo_repoman')
        self.assertEqual(docker_instance.image, None)
        self.assertEqual(docker_instance.directory_map, dict())

