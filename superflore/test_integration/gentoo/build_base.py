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


class GentooBuilder:
    def __init__(
        self, image_owner='allenh1', image_name='ros_gentoo_base'
    ):
        self.container = Docker()
        self.container.pull(image_owner, image_name)
        self.package_list = dict()

    def add_target(self, ros_distro, pkg):
        self.package_list['%s/%s' % (ros_distro, pkg)] = 'unknown'
