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

from catkin_pkg.package import parse_package_string


class PackageMetadata:
    def __init__(self, pkg_xml, evaluate_condition_context=None):
        self.upstream_email = None
        self.upstream_name = None
        self.homepage = 'https://wiki.ros.org'
        pkg = parse_package_string(pkg_xml)
        if evaluate_condition_context:
            pkg.evaluate_conditions(evaluate_condition_context)
        self.upstream_license = pkg.licenses
        self.description = pkg.description
        if 'website' in [url.type for url in pkg.urls]:
            self.homepage = [
                url.url for url in pkg.urls if url.type == 'website'
            ][0]
        elif len(pkg.urls) > 0:
            self.homepage = [
                url.url for url in pkg.urls
            ][0]
        self.longdescription = pkg.description
        self.upstream_email = [
            author.email for author in pkg.maintainers
        ][0]
        self.upstream_name = [
            author.name for author in pkg.maintainers
        ][0]
        self.author_email = [
            author.email for author in pkg.authors
        ][0] if pkg.authors else ''
        self.author_name = [
            author.name for author in pkg.authors
        ][0] if pkg.authors else ''
        self.member_of_groups = [
            group.name for group in pkg.member_of_groups
        ]
        self.build_type = pkg.get_build_type()
