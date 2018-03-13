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

from docker.errors import ContainerError
from superflore.docker import Docker
from superflore.utils import err
from superflore.utils import info
from superflore.utils import ok


class GentooBuilder:
    def __init__(
        self, image_owner='allenh1', image_name='ros_gentoo_base'
    ):
        self.container = Docker()
        self.container.pull(image_owner, image_name)
        self.package_list = dict()

    def add_target(self, ros_distro, pkg):
        # TODO(allenh1): it might be nice to add a Python3 target
        # in case we want to test both.
        self.package_list['ros-%s/%s' % (ros_distro, pkg)] = 'unknown'

    def run(self, verbose=True, log_file=None):
        # TODO(allenh1): add the ability to check out a non-master
        # branch of the overlay (for CI).
        info('testing gentoo package integrity')
        for pkg in sorted(self.package_list.keys()):
            self.container.add_bash_command('emaint sync -r ros-overlay')
            self.container.add_bash_command('emerge %s' % pkg)
            try:
                self.container.run(
                    rm=True, show_cmd=True, privileged=True, log_file=log_file
                )
                self.package_list[pkg] = 'building'
                ok("  '%s': building" % pkg)
            except ContainerError:
                self.package_list[pkg] = 'failing'
                err("  '%s': failing" % pkg)
            if verbose:
                print(self.container.log)
            self.container.clear_commands()
        return self.package_list
