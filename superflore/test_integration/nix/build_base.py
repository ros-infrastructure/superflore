# Copyright 2019 Open Source Robotics Foundation, Inc.
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
from superflore.generators.nix.nix_package import NixPackage
from superflore.utils import err
from superflore.utils import info
from superflore.utils import ok


class NixBuilder:
    def __init__(self, image_owner='nixos', image_name='nix'):
        self.container = Docker()
        self.container.pull(image_owner, image_name)
        self.package_list = dict()

    def add_target(self, ros_distro, pkg):
        pkg = NixPackage.normalize_name(pkg)
        self.package_list[
            'rosPackages.{}.{}'.format(ros_distro, pkg)] = 'unknown'

    def run(self, verbose=True, log_file=None):
        info('testing Nix package integrity')

        nix_ros_overlay_url = 'https://github.com/lopsided98/nix-ros-overlay' \
                              '/archive/master.tar.gz'
        for pkg in sorted(self.package_list.keys()):
            self.container.add_sh_command(
                'nix-build {} -A {}'.format(nix_ros_overlay_url, pkg))
            try:
                self.container.run(rm=True, show_cmd=True, log_file=log_file)
                self.package_list[pkg] = 'building'
                ok("  '%s': building" % pkg)
            except ContainerError:
                self.package_list[pkg] = 'failing'
                err("  '%s': failing" % pkg)
            if verbose:
                print(self.container.log)
            self.container.clear_commands()
        return self.package_list
