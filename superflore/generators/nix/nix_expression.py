# -*- coding: utf-8 -*-
#
# Copyright (c) 2016 David Bensoussan, Synapticon GmbH
# Copyright (c) 2019 Open Source Robotics Foundation, Inc.
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to
# deal  in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
# sell copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#
from operator import attrgetter
import os
from textwrap import dedent
from time import gmtime, strftime
from typing import Iterable, Set
import urllib.parse

from superflore.utils import get_license


def _escape_nix_string(string: str):
    return '"{}"'.format(string.replace("\\", "\\\\")
                               .replace("${", r"\${")
                               .replace('"', r"\""))


class NixLicense:
    """
    Converts a ROS license to the correct Nix license attribute.
    """

    _LICENSE_MAP = {
        'Apache-2.0': 'asl20',
        'ASL 2.0': 'asl20',
        'Boost-1.0': 'boost',
        'BSD-2': 'bsd2',
        'BSD-3-Clause': 'bsd3',
        'BSD': 'bsdOriginal',
        'CC-BY-NC-SA-4.0': 'cc-by-nc-sa-40',
        'GPL-1': 'gpl1',
        'GPL-2': 'gpl2',
        'GPL-3.0-only': 'gpl3Only',
        'GPL-3': 'gpl3',
        'LGPL-2.1': 'lgpl21',
        'LGPL-2': 'lgpl2',
        'LGPL-3.0-only': 'lgpl3Only',
        'LGPL-3': 'lgpl3',
        'MIT': 'mit',
        'MPL-1.0': 'mpl10',
        'MPL-1.1': 'mpl11',
        'MPL-2.0': 'mpl20',
        'PD': 'publicDomain',
    }

    def __init__(self, name):
        try:
            name = get_license(name)
            self.name = self._LICENSE_MAP[name]
            self.custom = False
        except KeyError:
            self.name = name
            self.custom = True

    @property
    def nix_code(self) -> str:
        if self.custom:
            return _escape_nix_string(self.name)
        else:
            return self.name


class NixExpression:
    def __init__(self, name: str, version: str,
                 src_url: str, src_sha256: str,
                 description: str, licenses: Iterable[NixLicense],
                 distro_name: str,
                 build_type: str,
                 build_inputs: Set[str] = set(),
                 propagated_build_inputs: Set[str] = set(),
                 check_inputs: Set[str] = set(),
                 native_build_inputs: Set[str] = set(),
                 propagated_native_build_inputs: Set[str] = set()
                 ) -> None:
        self.name = name
        self.version = version
        self.src_url = src_url
        self.src_sha256 = src_sha256
        # fetchurl's naming logic cannot account for URL parameters
        self.src_name = os.path.basename(
            urllib.parse.urlparse(self.src_url).path)

        self.description = description
        self.licenses = licenses
        self.distro_name = distro_name
        self.build_type = build_type

        self.build_inputs = build_inputs
        self.propagated_build_inputs = propagated_build_inputs
        self.check_inputs = check_inputs
        self.native_build_inputs = native_build_inputs
        self.propagated_native_build_inputs = \
            propagated_native_build_inputs

    @staticmethod
    def _to_nix_list(it: Iterable[str]) -> str:
        return '[ ' + ' '.join(it) + ' ]'

    @staticmethod
    def _to_nix_parameter(dep: str) -> str:
        return dep.split('.')[0]

    def get_text(self, distributor: str, license_name: str) -> str:
        """
        Generate the Nix expression, given the distributor line
        and the license text.
        """

        ret = []
        ret += dedent('''
        # Copyright {} {}
        # Distributed under the terms of the {} license

        ''').format(
            strftime("%Y", gmtime()), distributor,
            license_name)

        ret += '{ lib, buildRosPackage, fetchurl, ' + \
               ', '.join(sorted(set(map(self._to_nix_parameter,
                                        self.build_inputs |
                                        self.propagated_build_inputs |
                                        self.check_inputs |
                                        self.native_build_inputs |
                                        self.propagated_native_build_inputs)))
                         ) + ' }:'

        ret += dedent('''
        buildRosPackage {{
          pname = "ros-{distro_name}-{name}";
          version = "{version}";

          src = fetchurl {{
            url = "{src_url}";
            name = "{src_name}";
            sha256 = "{src_sha256}";
          }};

          buildType = "{build_type}";
        ''').format(
            distro_name=self.distro_name,
            name=self.name,
            version=self.version,
            src_url=self.src_url,
            src_name=self.src_name,
            src_sha256=self.src_sha256,
            build_type=self.build_type)

        if self.build_inputs:
            ret += "  buildInputs = {};\n" \
                .format(self._to_nix_list(sorted(self.build_inputs)))

        if self.check_inputs:
            ret += "  checkInputs = {};\n" \
                .format(self._to_nix_list(sorted(self.check_inputs)))

        if self.propagated_build_inputs:
            ret += "  propagatedBuildInputs = {};\n" \
                .format(self._to_nix_list(sorted(
                    self.propagated_build_inputs)))

        if self.native_build_inputs:
            ret += "  nativeBuildInputs = {};\n" \
                .format(self._to_nix_list(sorted(self.native_build_inputs)))

        if self.propagated_native_build_inputs:
            ret += "  propagatedNativeBuildInputs = {};\n".format(
                self._to_nix_list(sorted(self.propagated_native_build_inputs)))

        ret += dedent('''
          meta = {{
            description = {};
            license = with lib.licenses; {};
          }};
        }}
        ''').format(_escape_nix_string(self.description),
                    self._to_nix_list(map(attrgetter('nix_code'),
                                          self.licenses)))

        return ''.join(ret)
