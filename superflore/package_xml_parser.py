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

from superflore.utils import warn
import xmltodict


class PackageXmlParser:
    def __init__(self, pkg_xml, pkg_name):
        self.upstream_email = None
        self.upstream_name = None
        self.homepage = 'https://wiki.ros.org'
        pkg_fields = xmltodict.parse(pkg_xml)
        self.upstream_license = pkg_fields['package']['license']
        self.description = pkg_fields['package']['description']
        if not isinstance(self.description, str):
            if '#text' in self.description:
                self.description = self.description['#text']
            else:
                self.description = 'None'
        if 'description' in pkg_fields['package']:
            # fill longdescription, if available (defaults to "NONE").
            self.longdescription = pkg_fields['package']['description']
        if 'maintainer' in pkg_fields['package']:
            if isinstance(pkg_fields['package']['maintainer'], list):
                self.upstream_email =\
                    pkg_fields['package']['maintainer'][0]['@email']
                self.upstream_name =\
                    pkg_fields['package']['maintainer'][0]['#text']
            elif isinstance(
                pkg_fields['package']['maintainer']['@email'], list
            ):
                self.upstream_email =\
                    pkg_fields['package']['maintainer'][0]['@email']
                self.upstream_name =\
                    pkg_fields['package']['maintainer'][0]['#text']
            else:
                self.upstream_email =\
                    pkg_fields['package']['maintainer']['@email']
                if '#text' in pkg_fields['package']['maintainer']:
                    self.upstream_name =\
                        pkg_fields['package']['maintainer']['#text']
                else:
                    self.upstream_name = "UNKNOWN"
        if 'url' not in pkg_fields['package']:
            warn("no website field for package {}".format(pkg_name))
        elif isinstance(pkg_fields['package']['url'], str):
            self.homepage = pkg_fields['package']['url']
        elif '@type' in pkg_fields['package']['url']:
            if pkg_fields['package']['url']['@type'] == 'website':
                if '#text' in pkg_fields['package']['url']:
                    self.homepage = pkg_fields['package']['url']['#text']
        else:
            warn("failed to parse website for package {}".format(pkg_name))
