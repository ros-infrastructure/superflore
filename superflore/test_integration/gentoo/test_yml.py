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


class TestYml:
    def __init__(self, distros):
        # TODO(allenh1): type checking on args
        self.distro_changes = dict()
        if isinstance(distros, str):
            self.distro_changes[distros] = list()
        else:
            for distro in distros:
                self.distro_changes[distro] = list()

    def add_package(self, distro, pkg):
        self.distro_changes[distro].append(pkg)

    def get_text(self):
        ret = ''
        for distro in self.distro_changes.keys():
            if self.distro_changes[distro]:
                ret += '%s:\n' % distro
                for pkg in self.distro_changes[distro]:
                    ret += '  - %s\n' % pkg
        return ret
